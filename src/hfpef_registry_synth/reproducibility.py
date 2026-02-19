"""Reproducibility manifest and frozen snapshot packaging."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .config import PipelineConfig


@dataclass
class ReproducibilityArtifacts:
    run_id: str
    snapshot_dir: Path
    archive_path: Path
    manifest_path: Path


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_info(repo_root: Path) -> Dict[str, Any]:
    def _run(args: List[str]) -> str:
        proc = subprocess.run(
            args,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        return (proc.stdout or "").strip()

    commit = _run(["git", "rev-parse", "HEAD"])
    short = _run(["git", "rev-parse", "--short", "HEAD"])
    status = _run(["git", "status", "--porcelain"])
    return {
        "commit": commit,
        "commit_short": short,
        "is_dirty": bool(status.strip()),
        "status_porcelain": status.splitlines(),
    }


def _dependency_versions(packages: Iterable[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for pkg in packages:
        try:
            out[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            out[pkg] = "not_installed"
    return out


def _copy_if_exists(src: Path, dst: Path) -> Optional[Path]:
    if not src.exists() or not src.is_file():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def _archive_dir(snapshot_dir: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(snapshot_dir, arcname=snapshot_dir.name)


def create_reproducibility_package(
    config: PipelineConfig,
    output_files: Iterable[Path],
    command: str,
) -> ReproducibilityArtifacts:
    now = _utc_now()
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    runtime_dir = config.out_dir / "runtime"
    snapshot_dir = runtime_dir / f"reproducibility_snapshot_{run_id}"
    outputs_dir = snapshot_dir / "outputs"
    inputs_dir = snapshot_dir / "inputs"

    outputs_dir.mkdir(parents=True, exist_ok=True)
    inputs_dir.mkdir(parents=True, exist_ok=True)

    copied_outputs: List[Path] = []
    for fpath in sorted(set(Path(p) for p in output_files), key=lambda p: str(p)):
        copied = _copy_if_exists(fpath, outputs_dir / fpath.name)
        if copied is not None:
            copied_outputs.append(copied)

    if config.fixture_path:
        _copy_if_exists(Path(config.fixture_path), inputs_dir / Path(config.fixture_path).name)
    if config.adjudication_path:
        _copy_if_exists(Path(config.adjudication_path), inputs_dir / Path(config.adjudication_path).name)

    repo_root = Path(__file__).resolve().parents[2]
    manifest: Dict[str, Any] = {
        "run_id": run_id,
        "generated_utc": now.isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "command": command,
        "config": {
            "start_year": config.start_year,
            "grace_months": config.grace_months,
            "baseline_risks": list(config.baseline_risks),
            "mnar_deltas": list(config.mnar_deltas),
            "use_pubmed": config.use_pubmed,
            "use_openalex": config.use_openalex,
            "clinically_meaningful_arr": config.clinically_meaningful_arr,
            "validation_sample_size": config.validation_sample_size,
            "validation_seed": config.validation_seed,
        },
        "git": _git_info(repo_root),
        "dependencies": _dependency_versions(
            [
                "requests",
                "pandas",
                "numpy",
                "scipy",
                "tqdm",
                "python-dateutil",
                "rapidfuzz",
            ]
        ),
        "files": [],
    }

    for copied in copied_outputs:
        manifest["files"].append(
            {
                "path": str(copied.relative_to(snapshot_dir)),
                "sha256": _sha256(copied),
                "size_bytes": copied.stat().st_size,
            }
        )

    manifest["files"] = sorted(manifest["files"], key=lambda x: x["path"])

    manifest_path = snapshot_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")

    latest_manifest = runtime_dir / "reproducibility_manifest_latest.json"
    latest_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")

    archive_path = runtime_dir / f"reproducibility_snapshot_{run_id}.tar.gz"
    _archive_dir(snapshot_dir, archive_path)

    return ReproducibilityArtifacts(
        run_id=run_id,
        snapshot_dir=snapshot_dir,
        archive_path=archive_path,
        manifest_path=manifest_path,
    )
