from pathlib import Path

from hfpef_registry_synth.config import PipelineConfig
from hfpef_registry_synth.reproducibility import create_reproducibility_package


def test_create_reproducibility_package_creates_manifest_and_archive(tmp_path):
    out_dir = tmp_path / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    f1 = out_dir / "trial_universe.csv"
    f2 = out_dir / "summary_report.md"
    f1.write_text("nct_id\nNCT1\n", encoding="utf-8")
    f2.write_text("# report\n", encoding="utf-8")

    config = PipelineConfig(
        out_dir=out_dir,
        cache_dir=tmp_path / "cache",
        run_command="python3 -m scripts.run_hfpef --out_dir outputs",
        build_repro_package=True,
    )
    config.ensure_dirs()

    artifacts = create_reproducibility_package(
        config=config,
        output_files=[f1, f2],
        command=config.run_command,
    )

    assert artifacts.snapshot_dir.exists()
    assert artifacts.manifest_path.exists()
    assert artifacts.archive_path.exists()
    manifest_text = artifacts.manifest_path.read_text(encoding="utf-8")
    assert "trial_universe.csv" in manifest_text
