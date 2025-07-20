"""
Configuration constants and settings for the Sheet Joinery Add-in
"""

# Add-in metadata
import os

ADDIN_ID = "SheetJoineryAddin"
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = "Ritchie Industries"

# Python version requirements
REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 12

# Debug mode - when True, prints information to the TEXT window during development
# Set to False when distributing the add-in (per official Autodesk template)
DEBUG = True

# Material thickness constraints (in mm)
# These are the tested ranges - add-in may work outside but not guaranteed
MIN_TESTED_THICKNESS = 2.0   # 2mm minimum tested thickness
MAX_TESTED_THICKNESS = 20.0  # 20mm maximum tested thickness

# Default joint parameters
DEFAULT_TOLERANCE = 0.1  # 0.1mm default clearance
DEFAULT_FINGER_RATIO = 1.0  # 1:1 finger to slot ratio
DEFAULT_MIN_FINGER_COUNT = 3  # Minimum 3 fingers per joint

# Material type constants
MATERIAL_TYPES = {
    'PLYWOOD': 'Plywood',
    'MDF': 'MDF', 
    'COMPOSITE': 'Composite',
    'WOOD': 'Wood',
    'ALUMINUM': 'Aluminum',
    'STEEL': 'Steel',
    'CUSTOM': 'Custom'
}

# Joint type constants  
JOINT_TYPES = {
    'FINGER': 'FingerJoint',
    'BOX': 'BoxJoint', 
    'T_SLOT': 'TSlotJoint',
    'MORTISE_TENON': 'MortiseTenon'
}

# Dogbone type constants
DOGBONE_TYPES = {
    'CORNER': 'CornerDogbone',
    'FACE': 'FaceDogbone',
    'NONE': 'NoDogbone'
}

# Metadata storage uses ADDIN_ID as the attribute group name
