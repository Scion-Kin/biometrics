#!/usr/bin/env python3
# All patches will be included in here
import os
import shutil

os.execv("pip3", ["pip3", "install", "--upgrade", "logmachine"])
os.execv("git", ["git", "restore", "ZKTeco/main.py"])

# First, we need to find the pycaches in the ZKTeco directory
zkteco_dir = os.path.join(os.path.dirname(__file__), '..', 'ZKTeco')
pycache_dirs = [os.path.join(root, '__pycache__') for root, dirs, files in os.walk(zkteco_dir) if '__pycache__' in dirs]
# Now, we remove the __pycache__ directories
for pycache_dir in pycache_dirs:
    try:
        shutil.rmtree(pycache_dir)
        print(f"Removed {pycache_dir}")
    except OSError as e:
        print(f"Error removing {pycache_dir}: {e}")

print("Patches applied!")
