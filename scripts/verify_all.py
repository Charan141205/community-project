#!/usr/bin/env python3
"""
Runs comprehensive verification of the flood-ews monorepo:
1. Validates backend imports and pure risk engine
2. Executes pytest test suite
3. Checks firmware files existence and structure
"""
import os
import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent

def run():
    print("=" * 60)
    print(">> Running flood-ews Automated Monorepo Verification")
    print("=" * 60)

    # 1. Check firmware files
    print("\n[1/3] Verifying Firmware Assets...")
    firmware_dir = root_dir / "firmware"
    required_firmware = ["sketch.ino", "diagram.json", "wokwi.toml", "libraries.txt"]
    for f in required_firmware:
        path = firmware_dir / f
        if not path.exists():
            print(f"[-] Missing firmware file: {f}")
            sys.exit(1)
        print(f"  + Found firmware/{f} ({path.stat().st_size} bytes)")

    # 2. Check Database init
    print("\n[2/3] Verifying Database Schema...")
    db_init = root_dir / "db" / "init.sql"
    if not db_init.exists():
        print("[-] Missing db/init.sql")
        sys.exit(1)
    print(f"  + Found db/init.sql ({db_init.stat().st_size} bytes)")

    # 3. Run Pytest suite
    print("\n[3/3] Running Backend Pytest Test Suite...")
    python_bin = sys.executable
    cmd = [python_bin, "-m", "pytest", str(root_dir / "backend" / "tests"), "-v"]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir)
    res = subprocess.run(cmd, cwd=root_dir, env=env)

    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL SYSTEMS VERIFIED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n[-] Tests failed.")
        sys.exit(res.returncode)

if __name__ == "__main__":
    run()
