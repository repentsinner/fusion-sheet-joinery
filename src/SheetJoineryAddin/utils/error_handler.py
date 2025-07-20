"""
Error handling utilities with enhanced debugging capabilities
"""

import adsk.core
import traceback
import sys
from .debug_logger import get_logger

class ErrorHandler:
    """Centralized error handling for the add-in"""
    
    def __init__(self, component_name="Unknown"):
        self.component_name = component_name
        self.logger = get_logger()
    
    def handle_exception(self, operation_name, exception=None):
        """Handle an exception with comprehensive logging"""
        try:
            # Get exception info if not provided
            if exception is None:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = exc_value
            
            # Create detailed error message
            error_msg = f"Error in {self.component_name}.{operation_name}"
            
            if exception:
                error_msg += f": {str(exception)}"
            
            # Log with full traceback
            self.logger.error(error_msg, exception)
            
            # Show user-friendly message
            self._show_user_error(operation_name, str(exception) if exception else "Unknown error")
            
        except Exception as e:
            # Fallback error handling
            print(f"CRITICAL: Error handler failed: {e}")
            print(f"Original error in {self.component_name}.{operation_name}")
            traceback.print_exc()
    
    def _show_user_error(self, operation, error_details):
        """Show a user-friendly error message"""
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            message = (
                f"An error occurred in {operation}.\n\n"
                f"Details: {error_details}\n\n"
                "Check the Text Commands window (UTILITIES → TEXT COMMANDS) "
                "for detailed error information."
            )
            
            ui.messageBox(
                message,
                f"{self.component_name} Error",
                adsk.core.MessageBoxButtonTypes.OKButtonType,
                adsk.core.MessageBoxIconTypes.CriticalIconType
            )
            
        except:
            # Last resort
            print(f"Failed to show error dialog for {operation}: {error_details}")

def safe_execute(component_name, operation_name):
    """Decorator for safe execution with error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler(component_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_exception(operation_name, e)
                return None
        return wrapper
    return decorator

# Context manager for safe execution
class SafeExecutionContext:
    """Context manager for safe execution with automatic error handling"""
    
    def __init__(self, component_name, operation_name):
        self.error_handler = ErrorHandler(component_name)
        self.operation_name = operation_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback_obj):
        if exc_type is not None:
            self.error_handler.handle_exception(self.operation_name, exc_value)
        return True  # Suppress the exception