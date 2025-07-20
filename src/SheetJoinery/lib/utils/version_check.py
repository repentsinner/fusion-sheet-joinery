"""
Version checking utilities for Fusion 360 and Python compatibility
"""

import sys

import adsk.core

from ... import config


def get_fusion_version():
    """Get the current Fusion 360 version"""
    try:
        app = adsk.core.Application.get()
        return app.version
    except Exception:
        return "Unknown"


def get_python_version():
    """Get the current Python version info"""
    return {
        "version": sys.version,
        "version_info": sys.version_info,
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro,
    }


def check_python_compatibility():
    """Check if current Python version is compatible with our requirements"""
    version_info = sys.version_info

    # Use constants from config instead of hardcoded values
    min_major = config.REQUIRED_PYTHON_MAJOR
    min_minor = config.REQUIRED_PYTHON_MINOR

    if version_info.major < min_major or (
        version_info.major == min_major and version_info.minor < min_minor
    ):
        return (
            False,
            f"Python {min_major}.{min_minor}+ required, found {version_info.major}.{version_info.minor}",
        )

    return True, f"Python {version_info.major}.{version_info.minor} is compatible"


def get_system_info():
    """Get comprehensive system information for debugging"""
    compatible, compatibility_msg = check_python_compatibility()

    return {
        "fusion_version": get_fusion_version(),
        "python_version": get_python_version(),
        "compatibility": {"is_compatible": compatible, "message": compatibility_msg},
        "platform": sys.platform,
    }


def perform_startup_version_check():
    """Perform version compatibility check during add-in startup"""
    from ...lib import fusionAddInUtils as futil

    # Get system info
    system_info = get_system_info()

    # Log version information
    futil.log(f"Fusion 360 version: {system_info['fusion_version']}")
    futil.log(f"Python version: {system_info['python_version']['version'].strip()}")
    futil.log(f"Platform: {system_info['platform']}")

    # Check compatibility
    if not system_info["compatibility"]["is_compatible"]:
        error_msg = (
            f"Incompatible Python version: {system_info['compatibility']['message']}"
        )
        futil.log(f"ERROR: {error_msg}")

        # Show user-facing error dialog
        ui = adsk.core.Application.get().userInterface
        ui.messageBox(
            f"{error_msg}\n\nThis add-in requires Python {config.REQUIRED_PYTHON_MAJOR}.{config.REQUIRED_PYTHON_MINOR}+ but found {system_info['python_version']['major']}.{system_info['python_version']['minor']}.",
            "Python Version Compatibility Error",
            adsk.core.MessageBoxButtonTypes.OKButtonType,  # type: ignore
            adsk.core.MessageBoxIconTypes.CriticalIconType,  # type: ignore
        )
        return False
    else:
        futil.log(f"Python compatibility: {system_info['compatibility']['message']}")
        return True
