"""T025 acceptance: corpus release integrity + deployment artifacts present/valid."""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main() -> int:
    py = sys.executable

    # 1) corpus release integrity
    assert subprocess.run([py, str(ROOT / "scripts" / "verify_release.py")]).returncode == 0, "verify_release failed"

    # 2) deployment artifacts present + well-formed
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for token in ("backend:", "frontend:", "healthcheck:", "expose:"):
        assert token in compose, f"docker-compose missing {token}"
    assert (ROOT / "backend" / "Dockerfile").exists(), "backend Dockerfile missing"
    assert (ROOT / "frontend" / "Dockerfile").exists(), "frontend Dockerfile missing"

    setup = (ROOT / "docs" / "REAL_API_SETUP.md").read_text(encoding="utf-8")
    assert "GEMINI_API_KEY" in setup and "BHASHINI" in setup.upper(), "REAL_API_SETUP incomplete"

    # 3) if docker is available, validate the compose file (no startup needed)
    if shutil.which("docker"):
        rc = subprocess.run("docker compose config", cwd=str(ROOT), shell=True,
                            capture_output=True).returncode
        assert rc == 0, "docker compose config invalid"
        print("T025 OK: corpus integrity + deployment artifacts valid (+ docker compose config)")
    else:
        print("T025 OK: corpus integrity + deployment artifacts valid (docker not present; compose not started)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
