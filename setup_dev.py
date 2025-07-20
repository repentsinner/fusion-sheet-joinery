#!/usr/bin/env python3
"""
Setup script for Fusion 360 development environment.
One script to rule them all - creates all necessary development configurations.
"""

import json
import os
import platform
from pathlib import Path


def find_fusion360_defs():
    """Find the Fusion 360 API definitions directory."""
    if platform.system() == "Darwin":  # macOS
        defs_path = Path.home() / "Library/Application Support/Autodesk/Autodesk Fusion 360/API/Python/defs"
    elif platform.system() == "Windows":
        defs_path = Path.home() / "AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Python/defs"
    else:
        print(f"Unsupported platform: {platform.system()}")
        return None
    
    if defs_path.exists():
        return str(defs_path)
    else:
        print(f"Fusion 360 API definitions not found at: {defs_path}")
        return None


def create_pyrightconfig(defs_path):
    """Create pyrightconfig.json with dynamic extraPaths."""
    config = {
        "extraPaths": [
            defs_path,
            "src/SheetJoineryAddin"
        ]
    }
    
    with open("pyrightconfig.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created pyrightconfig.json with extraPaths:")
    print(f"  - {defs_path}")
    print(f"  - src/SheetJoineryAddin")




if __name__ == "__main__":
    print("Setting up Fusion 360 development environment...")
    
    defs_path = find_fusion360_defs()
    if defs_path:
        create_pyrightconfig(defs_path)
        
        print("\n🎉 Setup complete!")
        print("\nWhat was created:")
        print("• pyrightconfig.json - Type checking paths for pyright")
        print("\nStatic configuration is in pyproject.toml")
        
    else:
        print("❌ Setup failed: Could not find Fusion 360 installation")