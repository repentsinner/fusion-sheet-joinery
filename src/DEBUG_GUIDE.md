# Debugging Fusion 360 Add-ins

## Multiple Ways to Access Error Information

### 1. Text Commands Window (Recommended)
**Access**: **UTILITIES** → **TEXT COMMANDS** (or **Shift + Alt + C**)

**Benefits**:
- ✅ **Copyable text** - Unlike error dialogs, you can select and copy from here
- ✅ **Real-time output** - Shows `print()` statements and errors as they happen
- ✅ **Full error details** - Complete tracebacks and exception information
- ✅ **Persistent** - Keeps history of all output

**Usage**:
```python
# In your add-in code, use print() for debugging
print("Debug: Starting intersection detection...")
print(f"Found {len(intersections)} intersections")
```

### 2. Enhanced Debug Logger (Built into this Add-in)
Our add-in includes comprehensive logging utilities:

```python
from utils.debug_logger import log_info, log_error, log_warning

# Use throughout your code
log_info("Processing started")
log_warning("Material thickness outside tested range")
log_error("Failed to create joint", exception)
```

**Features**:
- **Multiple outputs**: Text Commands + log files + error dialogs
- **Automatic timestamps**: All messages include time stamps
- **Exception handling**: Automatic traceback capture
- **File logging**: Saves to `~/Documents/Fusion360_AddIn_Logs/`

### 3. System Log Files

#### Windows Locations:
```
# Main Fusion logs
%LOCALAPPDATA%\Autodesk\webdeploy\production\[version]\log\

# Specific files:
- Fusion360.log          # Main application log
- API.log               # API-specific errors  
- Python.log            # Python interpreter errors
```

#### macOS Locations:
```
# Main Fusion logs
~/Library/Logs/Autodesk/Fusion360/

# Application Support logs
~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/
```

### 4. Our Custom Log Files
The add-in creates its own log files at:

**Windows**: `%USERPROFILE%\Documents\Fusion360_AddIn_Logs\`
**macOS**: `~/Documents/Fusion360_AddIn_Logs/`

**Log files**:
- `SheetJoineryAddin_YYYY-MM-DD.log` - Daily log files
- Contains all debug output with timestamps
- Safe fallback when Text Commands window isn't available

## Debugging Workflow

### Step 1: Enable Text Commands Window
1. Go to **UTILITIES** → **TEXT COMMANDS**
2. Keep this window open while developing
3. All `print()` statements and errors will appear here

### Step 2: Use Debug Logging in Code
```python
from utils.debug_logger import get_logger, log_info, log_error
from utils.error_handler import SafeExecutionContext

# Safe execution with automatic error handling
def my_function():
    with SafeExecutionContext("MyComponent", "my_function"):
        log_info("Starting operation...")
        # Your code here
        log_info("Operation completed successfully")

# Manual logging
logger = get_logger()
logger.system_info()  # Log system information
logger.debug("Detailed debug information")
logger.error("Something went wrong", exception)
```

### Step 3: Error Investigation Process
1. **Check Text Commands window first** - Most immediate and detailed
2. **Review custom log files** - For historical information
3. **Check Fusion system logs** - For deep system issues
4. **Use system info logging** - To understand environment

## Common Error Scenarios

### Import Errors
```python
# Bad - will fail silently in some cases
import my_module

# Good - with error handling
try:
    import my_module
    log_info("Successfully imported my_module")
except ImportError as e:
    log_error("Failed to import my_module", e)
```

### API Call Errors
```python
# Bad - no error context
result = some_fusion_api_call()

# Good - with context and logging
try:
    log_info("Calling Fusion API...")
    result = some_fusion_api_call()
    log_info(f"API call successful: {result}")
except Exception as e:
    log_error("Fusion API call failed", e)
    return None
```

### Custom Feature Compute Errors
```python
def _on_custom_feature_compute(self, args):
    """Handle custom feature compute events with proper error handling"""
    try:
        log_info("Starting custom feature compute...")
        
        # Your compute logic here
        
        args.isComputed = True
        log_info("Custom feature compute completed successfully")
        
    except Exception as e:
        log_error("Custom feature compute failed", e)
        args.isComputed = False
        args.computeStatus = f"Compute failed: {str(e)}"
```

## Debug Configuration

### Enable Debug Mode
In `config.py`:
```python
DEBUG_MODE = True          # Enable verbose logging
LOG_TO_FILE = True        # Enable file logging
LOG_FILENAME = 'debug.log' # Custom log filename
```

### System Information Logging
```python
# Get comprehensive system info
from utils.debug_logger import get_logger
logger = get_logger()
logger.system_info()  # Logs Python version, Fusion version, platform, etc.
```

## Tips for Effective Debugging

### 1. Use Descriptive Log Messages
```python
# Bad
log_info("Processing")

# Good  
log_info(f"Processing {len(intersections)} intersections for material thickness {thickness}mm")
```

### 2. Log Entry and Exit Points
```python
def complex_function():
    log_info("Entering complex_function")
    try:
        # Function logic
        log_info("complex_function completed successfully")
        return result
    except Exception as e:
        log_error("complex_function failed", e)
        raise
```

### 3. Use Context Managers for Safety
```python
# Automatically handles exceptions and logging
with SafeExecutionContext("JointGenerator", "create_finger_joint"):
    # Your code here - exceptions automatically logged
    pass
```

### 4. Progressive Detail Levels
```python
log_info("Starting intersection detection")           # High level
log_debug(f"Analyzing body pair: {body1.name}, {body2.name}")  # Detailed
log_debug(f"Intersection volume: {volume}")          # Very detailed
```

## Troubleshooting Common Issues

### Text Commands Window Not Showing Output
- Restart Fusion 360
- Check if window is docked/hidden
- Use file logging as backup

### Log Files Not Created
- Check file permissions
- Verify Documents folder exists
- Check disk space

### Exceptions Not Being Caught
- Use `SafeExecutionContext` context manager
- Wrap all API calls in try/catch blocks
- Check that error handlers are imported correctly

### Performance Issues with Logging
- Set `DEBUG_MODE = False` in production
- Use `log_debug()` for verbose output that can be disabled
- Avoid logging in tight loops

## Python Version Notes

**Current Fusion 360**: Python 3.12.4 (confirmed 2025-01-19)
- Add-in maintains compatibility with Python 3.9+ for backward compatibility
- Version checking performed automatically on add-in load
- All debugging tools work with Python 3.12.4

Remember: The Text Commands window is your best friend for debugging Fusion 360 add-ins!