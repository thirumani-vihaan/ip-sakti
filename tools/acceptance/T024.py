"""T024 acceptance: run_eval and smoke_demo both pass on fixtures."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main() -> int:
    py = sys.executable
    r1 = subprocess.run([py, str(ROOT / "eval" / "run_eval.py")]).returncode
    assert r1 == 0, "run_eval gates failed"
    r2 = subprocess.run([py, str(ROOT / "backend" / "tests" / "smoke_demo.py")]).returncode
    assert r2 == 0, "smoke_demo failed"
    print("T024 OK: run_eval gates met + smoke_demo full-path passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
