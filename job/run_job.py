import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "PAYROLL.cob"
BIN = ROOT / "out" / "PAYROLL.exe"   # works on Windows; on mac/linux it's still ok as a filename
OUTDIR = ROOT / "out"
EMP_OUT = OUTDIR / "EMPOUT.dat"
EMP_SORTED = OUTDIR / "EMPOUT_sorted.dat"
REPORT = OUTDIR / "REPORT.txt"


def run_step(name: str, cmd: list[str]) -> int:
    print(f"\n//STEP {name}")
    print("CMD:", " ".join(cmd))
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), check=False)
        rc = p.returncode
    except FileNotFoundError:
        print(f"ERROR: command not found: {cmd[0]}")
        return 127

    print(f"//STEP {name} RC={rc}")
    return rc


def ensure_outdir():
    OUTDIR.mkdir(exist_ok=True)


def sort_empout():
    print("\n//STEP SORTOUT")
    if not EMP_OUT.exists():
        print("ERROR: Missing EMPOUT.dat (previous step failed?)")
        return 8

    lines = EMP_OUT.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Extract employee id after "EMPID="
    def key(line: str):
        try:
            start = line.index("EMPID=") + len("EMPID=")
            empid = line[start:start+5]
            return int(empid)
        except Exception:
            return 999999

    lines_sorted = sorted(lines, key=key)
    EMP_SORTED.write_text("\n".join(lines_sorted) + "\n", encoding="utf-8")
    print(f"Wrote: {EMP_SORTED}")
    return 0


def main():
    ensure_outdir()

    # STEP1: compile
    # cobc -x => build executable
    rc = run_step("COMPILE", ["cobc", "-free", "-x", str(SRC.relative_to(ROOT)), "-o", str(BIN.relative_to(ROOT))])
    if rc != 0:
        sys.exit(rc)

    # STEP2: execute
    # On mac/linux, may need chmod, but cobc usually outputs runnable binary
    exe_path = str(BIN)
    if os.name != "nt":
        exe_path = exe_path  # same path
    rc = run_step("RUNPAY", [exe_path])
    if rc != 0:
        sys.exit(rc)

    # STEP3: sort output
    rc = sort_empout()
    if rc != 0:
        sys.exit(rc)

    # STEP4: display outputsc
    print("\n//STEP RESULTS RC=0")
    print("Generated files:")
    print(" -", EMP_OUT)
    print(" -", EMP_SORTED)
    print(" -", REPORT)
    print("\nDone.")


if __name__ == "__main__":
    main()
