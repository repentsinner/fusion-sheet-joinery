# Fusion 360 Sheet Goods Joinery Add-in
# Main entry point script that matches the add-in folder name

import adsk.core
import adsk.fusion
import traceback
import sys
import os

# Add the current directory to sys.path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands.hello_world_command import HelloWorldCommand
from utils.debug_logger import get_logger, log_info, log_error
from utils.error_handler import SafeExecutionContext

# Global list to keep all event handlers in scope
_handlers = []
_app = None
_ui = None

def run(context):
    """Entry point when the add-in is loaded"""
    with SafeExecutionContext("SheetJoineryAddin", "run"):
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Initialize logging
        logger = get_logger()
        logger.system_info()
        log_info("Starting Sheet Joinery Add-in...")
        
        # Check Python version for compatibility
        _check_python_version()
        
        # Create and register the hello world command
        hello_cmd = HelloWorldCommand()
        hello_cmd.on_create()
        
        success_msg = f'Sheet Joinery Add-in loaded successfully!\nPython version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        log_info("Add-in loaded successfully")
        _ui.messageBox(success_msg)

def stop(context):
    """Entry point when the add-in is unloaded"""
    with SafeExecutionContext("SheetJoineryAddin", "stop"):
        log_info("Stopping Sheet Joinery Add-in...")
        
        # Clean up command definitions
        cmd_def = _ui.commandDefinitions.itemById('SheetJoineryHelloWorld')
        if cmd_def:
            cmd_def.deleteMe()
            log_info("Cleaned up command definitions")
            
        # Clean up any UI elements
        # (Add cleanup for panels, toolbars, etc. when implemented)
        
        log_info("Add-in unloaded successfully")
        _ui.messageBox('Sheet Joinery Add-in unloaded successfully!')

def _check_python_version():
    """Check that we're running on a supported Python version"""
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    log_info(f"Python version check: {version_str}")
    
    # We target Python 3.9+ (Fusion 360 confirmed version: 3.12.4)
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 9):
        warning_msg = (
            'Warning: This add-in requires Python 3.9 or later.\n'
            f'Current version: {version_str}\n'
            'Some features may not work correctly.'
        )
        log_error(f"Python version incompatibility: {version_str}")
        _ui.messageBox(warning_msg)
    else:
        log_info(f"Python version {version_str} is compatible")