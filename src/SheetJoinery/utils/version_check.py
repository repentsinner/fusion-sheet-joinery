"""
Version checking utilities for Fusion 360 and Python compatibility
"""

import sys
import adsk.core

def get_fusion_version():
    """Get the current Fusion 360 version"""
    try:
        app = adsk.core.Application.get()
        return app.version
    except:
        return "Unknown"

def get_python_version():
    """Get the current Python version info"""
    return {
        'version': sys.version,
        'version_info': sys.version_info,
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
        'micro': sys.version_info.micro
    }

def check_python_compatibility():
    """Check if current Python version is compatible with our requirements"""
    version_info = sys.version_info
    
    # We require Python 3.9+ (Fusion 360's current standard)
    min_major = 3
    min_minor = 9
    
    if version_info.major < min_major or (version_info.major == min_major and version_info.minor < min_minor):
        return False, f"Python {min_major}.{min_minor}+ required, found {version_info.major}.{version_info.minor}"
    
    return True, f"Python {version_info.major}.{version_info.minor} is compatible"

def get_system_info():
    """Get comprehensive system information for debugging"""
    compatible, compatibility_msg = check_python_compatibility()
    
    return {
        'fusion_version': get_fusion_version(),
        'python_version': get_python_version(),
        'compatibility': {
            'is_compatible': compatible,
            'message': compatibility_msg
        },
        'platform': sys.platform
    }