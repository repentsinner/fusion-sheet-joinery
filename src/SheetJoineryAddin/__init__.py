# Fusion 360 Sheet Goods Joinery Add-in
# Entry point for the add-in

import adsk.core
import adsk.fusion
import traceback
import sys
import os

# Add the current directory to sys.path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .commands.hello_world_command import HelloWorldCommand

# Global list to keep all event handlers in scope
_handlers = []
_app = None
_ui = None

def run(context):
    """Entry point when the add-in is loaded"""
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Check Python version for compatibility
        _check_python_version()
        
        # Create and register the hello world command
        hello_cmd = HelloWorldCommand()
        hello_cmd.on_create()
        
        _ui.messageBox('Sheet Joinery Add-in loaded successfully!\nPython version: {}'.format(sys.version))
        
    except:
        if _ui:
            _ui.messageBox('Failed to load Sheet Joinery Add-in:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Entry point when the add-in is unloaded"""
    try:
        # Clean up command definitions
        cmd_def = _ui.commandDefinitions.itemById('SheetJoineryHelloWorld')
        if cmd_def:
            cmd_def.deleteMe()
            
        # Clean up any UI elements
        # (Add cleanup for panels, toolbars, etc. when implemented)
        
        _ui.messageBox('Sheet Joinery Add-in unloaded successfully!')
        
    except:
        if _ui:
            _ui.messageBox('Failed to unload Sheet Joinery Add-in:\n{}'.format(traceback.format_exc()))

def _check_python_version():
    """Check that we're running on a supported Python version"""
    version_info = sys.version_info
    
    # We target Python 3.9+ (Fusion 360's current version)
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 9):
        _ui.messageBox(
            'Warning: This add-in requires Python 3.9 or later.\n'
            f'Current version: {sys.version}\n'
            'Some features may not work correctly.'
        )