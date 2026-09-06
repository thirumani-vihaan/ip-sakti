"""Run a task's acceptance script: python tools/run_acceptance.py T001"""
import pathlib
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run_acceptance.py T0XX")
        return 2
    task = sys.argv[1]
    script = pathlib.Path(__file__).parent / "acceptance" / f"{task}.py"
    if not script.exists():
        print(f"no acceptance script: {script}")
        return 2
    return subprocess.run([sys.executable, str(script)]).returncode


if __name__ == "__main__":
    sys.exit(main())
