"""
Configuration constants and settings for the Sheet Joinery Add-in
"""

# Add-in metadata
import os

ADDIN_ID = "SheetJoineryAddin"
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = "Ritchie Industries"
ADDIN_VERSION = "0.1.2"
ADDIN_DESCRIPTION = "Automates tab-and-slot joinery creation for sheet goods fabrication"

# Python version requirements
REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 9

DEBUG = True

# Fusion 360 Python version (confirmed)
FUSION_PYTHON_VERSION = "3.12.4"  # Current Fusion 360 embedded Python version

# Material thickness constraints (in mm)
# These are the tested ranges - add-in may work outside but not guaranteed
MIN_TESTED_THICKNESS = 2.0   # 2mm minimum tested thickness
MAX_TESTED_THICKNESS = 20.0  # 20mm maximum tested thickness

# Default joint parameters
DEFAULT_TOLERANCE = 0.1  # 0.1mm default clearance
DEFAULT_FINGER_RATIO = 1.0  # 1:1 finger to slot ratio
DEFAULT_MIN_FINGER_COUNT = 3  # Minimum 3 fingers per joint

# UI Command IDs
CMD_HELLO_WORLD = "SheetJoineryHelloWorld"
CMD_AUTO_GENERATE = "SheetJoineryAutoGenerate"
CMD_PREPARE_CAM = "SheetJoineryPrepareCAM"

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

# Attribute group name for metadata storage
ATTRIBUTE_GROUP = 'JoineryAddin'

# Debug and logging settings
DEBUG_MODE = True  # Set to False for production
LOG_TO_FILE = False  # Set to True to enable file logging
LOG_FILENAME = 'sheet_joinery.log'