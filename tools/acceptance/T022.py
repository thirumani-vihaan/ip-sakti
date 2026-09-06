"""T022 acceptance: frontend wizard suite passes (npm test covers chat + wizard)."""
import pathlib
import subprocess
import sys

FRONTEND = pathlib.Path(__file__).resolve().parents[2] / "frontend"


def main() -> int:
    r = subprocess.run("npm test", cwd=str(FRONTEND), shell=True)
    assert r.returncode == 0, "frontend vitest failed"
    print("T022 OK: ABS + classification wizard vitest passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
