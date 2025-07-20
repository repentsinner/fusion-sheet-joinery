"""
Debug logging utilities for Sheet Joinery Add-in
Provides multiple output methods for debugging add-in issues
"""

import adsk.core
import sys
import traceback
import os
import datetime

class DebugLogger:
    """Enhanced debugging logger for Fusion 360 add-ins"""
    
    def __init__(self, add_in_name="SheetJoineryAddin"):
        self.add_in_name = add_in_name
        self._app = adsk.core.Application.get()
        self._ui = self._app.userInterface if self._app else None
        
        # Try to get text commands palette for console output
        try:
            self._text_commands = self._ui.palettes.itemById('TextCommands')
        except:
            self._text_commands = None
    
    def log(self, message, level="INFO"):
        """Log a message to multiple outputs"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {self.add_in_name} {level}: {message}"
        
        # Output to Text Commands window (most reliable)
        print(formatted_message)
        
        # Try to write to log file
        self._write_to_file(formatted_message)
        
        # For errors, also show in UI
        if level == "ERROR":
            self._show_error_dialog(message)
    
    def error(self, message, exception=None):
        """Log an error with optional exception details"""
        error_msg = message
        if exception:
            error_msg += f"\nException: {str(exception)}"
            error_msg += f"\nTraceback:\n{traceback.format_exc()}"
        
        self.log(error_msg, "ERROR")
    
    def warning(self, message):
        """Log a warning message"""
        self.log(message, "WARNING")
    
    def info(self, message):
        """Log an info message"""
        self.log(message, "INFO")
    
    def debug(self, message):
        """Log a debug message"""
        self.log(message, "DEBUG")
    
    def system_info(self):
        """Log comprehensive system information"""
        try:
            info = []
            info.append(f"Add-in: {self.add_in_name}")
            info.append(f"Python: {sys.version}")
            info.append(f"Platform: {sys.platform}")
            
            if self._app:
                info.append(f"Fusion Version: {self._app.version}")
                info.append(f"Product: {self._app.activeProduct.productType if self._app.activeProduct else 'None'}")
            
            # Log system information
            self.info("System Information:\n" + "\n".join(info))
            
        except Exception as e:
            self.error("Failed to get system info", e)
    
    def _write_to_file(self, message):
        """Write log message to file"""
        try:
            # Get user's documents folder for cross-platform compatibility
            if sys.platform == "win32":
                log_dir = os.path.expanduser("~/Documents/Fusion360_AddIn_Logs")
            else:  # macOS
                log_dir = os.path.expanduser("~/Documents/Fusion360_AddIn_Logs")
            
            # Create log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Write to daily log file
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"{self.add_in_name}_{today}.log")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
                
        except Exception:
            # Silently fail for file logging - don't want to break the add-in
            pass
    
    def _show_error_dialog(self, message):
        """Show error dialog with copyable text"""
        try:
            if self._ui:
                # Create a copyable text box dialog
                self._ui.messageBox(
                    f"Error in {self.add_in_name}:\n\n{message}\n\n"
                    "Check Text Commands window for full details.",
                    f"{self.add_in_name} Error",
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.CriticalIconType
                )
        except:
            # Last resort - print to console
            print(f"CRITICAL ERROR: {message}")

# Global logger instance
_logger = None

def get_logger():
    """Get the global debug logger instance"""
    global _logger
    if _logger is None:
        _logger = DebugLogger()
    return _logger

def log_exception(func):
    """Decorator to automatically log exceptions from functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            get_logger().error(f"Exception in {func.__name__}", e)
            raise
    return wrapper

# Convenience functions
def log_info(message):
    get_logger().info(message)

def log_warning(message):
    get_logger().warning(message)

def log_error(message, exception=None):
    get_logger().error(message, exception)

def log_debug(message):
    get_logger().debug(message)