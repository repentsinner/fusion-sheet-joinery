# Installation Instructions

## Prerequisites

- **Autodesk Fusion 360**: Latest version recommended
- **Python Version**: Fusion 360 uses embedded Python 3.12.4
- **License**: Fusion 360 Personal or Commercial with CAM workspace access

## Python Version Verification

To check the Python version in your Fusion 360 installation:

1. Open Fusion 360
2. Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins**
3. Click **Create** → **Create New Script**
4. Paste this code and run:

```python
import sys
print(f"Python version: {sys.version}")
print(f"Version info: {sys.version_info}")
```

You should see Python 3.12.4 (or 3.12.x) for the current Fusion 360 version.

## Installation Steps

### Method 1: Manual Installation

1. **Download the add-in files** to your computer

2. **Locate your Fusion 360 add-ins directory**:
   - **Windows**: `%APPDATA%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\`
   - **macOS**: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`

3. **Create the add-in folder**:
   ```
   [AddIns Directory]/SheetJoineryAddin/
   ```

4. **Copy all files** from `src/SheetJoineryAddin/` to the new folder

5. **Verify the structure**:
   ```
   SheetJoineryAddin/
   ├── SheetJoineryAddin.py         # Main script (matches folder name)
   ├── SheetJoineryAddin.manifest   # Manifest file (matches folder name)
   ├── __init__.py
   ├── config.py
   ├── requirements.txt
   ├── commands/
   │   ├── __init__.py
   │   └── hello_world_command.py
   └── utils/
       ├── __init__.py
       └── version_check.py
   ```

### Method 2: Symlink Installation (Development)

For development, you can create a symbolic link:

**Windows (Run as Administrator)**:
```cmd
mklink /D "%APPDATA%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\SheetJoineryAddin" "C:\\path\\to\\fusion-sheet-joinery\\src\\SheetJoineryAddin"
```

**macOS/Linux**:
```bash
ln -s "/path/to/fusion-sheet-joinery/src/SheetJoineryAddin" "~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/SheetJoineryAddin"
```

## Loading the Add-in

1. **Launch Fusion 360**

2. **Open Scripts and Add-Ins**:
   - Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins**
   - Or press **Shift + S**

3. **Select the Add-Ins tab**

4. **Find "Sheet Goods Joinery"** in the list

5. **Click "Run"** to load the add-in

6. **Optional**: Check **"Run on Startup"** to load automatically

## Verification

After loading, you should see:
- A success message with Python version information
- New command "Hello World Custom Feature" in the CREATE panel
- No error messages in the Text Commands window

## Troubleshooting

### Common Issues

**Add-in not appearing in list**:
- Verify file structure matches exactly
- Check that `__init__.py` exists in the root folder
- Ensure no syntax errors in Python files

**Python version warnings**:
- Update Fusion 360 to latest version
- Verify Python 3.9+ compatibility

**Permission errors**:
- Run Fusion 360 as administrator (Windows)
- Check file permissions on macOS

### Debug Information

Run this script in Fusion 360 to get system information:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/SheetJoineryAddin"))

from utils.version_check import get_system_info
import json
print(json.dumps(get_system_info(), indent=2))
```

### Getting Help

- Check the [Requirements Documentation](../REQUIREMENTS.md)
- Review the [Architecture Documentation](../ARCHITECTURE.md)
- Report issues on the project repository

## Development Setup

For developers working on the add-in:

1. Use the symlink installation method
2. Install development dependencies:
   ```bash
   pip install pytest black mypy
   ```
3. Run tests before committing changes
4. Follow the coding standards in the project documentation