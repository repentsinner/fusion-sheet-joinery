# Fusion 360 Sheet Goods Joinery Add-in - Source Code

This directory contains the source code implementation for the Fusion 360 Sheet Goods Joinery Add-in.

## Project Structure

```
src/
├── SheetJoineryAddin/           # Main add-in package
│   ├── __init__.py             # Entry point and add-in lifecycle
│   ├── manifest.yaml           # Add-in metadata and configuration
│   ├── config.py              # Constants and configuration settings
│   ├── requirements.txt        # Python dependencies documentation
│   ├── commands/              # Command implementations
│   │   ├── __init__.py
│   │   └── hello_world_command.py  # Demo Custom Feature command
│   └── utils/                 # Utility functions and helpers
│       ├── __init__.py
│       └── version_check.py   # Python/Fusion version utilities
├── INSTALL.md                 # Installation instructions
└── README.md                  # This file
```

## Python Version Compatibility

This add-in is developed for **Python 3.12.4**, which is the current embedded interpreter in Fusion 360.

### Checking Your Python Version

Run this in Fusion 360 to verify compatibility:

```python
import sys
print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
```

### Version Support Strategy

- **Current**: Python 3.12.4 (Fusion 360 current standard)
- **Minimum**: Python 3.9 (enforced by version check for backward compatibility)
- **Features**: Uses Python 3.9+ language features and type hints (compatible with 3.12.4)
- **Libraries**: Standard library only (no external dependencies in MVP)

## Current Implementation Status

### ✅ Completed (MVP Demo)

- **Project Structure**: Complete Python package structure
- **Entry Point**: Add-in loading and unloading lifecycle
- **Hello World Command**: Demonstrates Custom Features API
- **Version Checking**: Python compatibility validation
- **Basic UI Integration**: Command added to CREATE panel
- **Custom Feature Demo**: Shows timeline integration and compute events

### 🔄 In Development

Following the [12-week development plan](../PLAN.md):

- **Phase 1**: Foundation & Core Detection (Weeks 1-3)
- **Phase 2**: Custom Features Integration (Weeks 4-5)  
- **Phase 3**: Joint Type Expansion (Weeks 6-7)
- **Phase 4**: CAM Integration (Weeks 8-9)
- **Phase 5**: Polish & Testing (Weeks 10-11)
- **Phase 6**: Release Preparation (Week 12)

## Key Components

### Entry Point (`__init__.py`)

- Add-in lifecycle management (run/stop)
- Python version compatibility checking
- Command registration and cleanup
- Error handling and user feedback

### Hello World Command (`commands/hello_world_command.py`)

Demonstrates core Custom Features API concepts:

- **Command Creation**: UI integration and event handling
- **Custom Feature Definition**: Timeline node creation
- **Parameter Management**: User input and persistence
- **Compute Events**: Automatic regeneration on changes
- **Entity Management**: Sketch creation and manipulation

### Configuration (`config.py`)

Centralized settings for:

- Material thickness ranges (2mm-20mm tested)
- Default joint parameters and tolerances  
- UI command identifiers
- Material and joint type constants
- Debug and logging configuration

### Version Utilities (`utils/version_check.py`)

Provides:

- Python version detection and compatibility checking
- Fusion 360 version information
- System information for debugging
- Compatibility validation messaging

## Development Guidelines

### Code Standards

- **Type Hints**: Use Python 3.9+ type annotations
- **Error Handling**: Comprehensive try/catch with user feedback
- **Documentation**: Docstrings for all classes and methods
- **Constants**: Centralized in `config.py`
- **Logging**: Debug information for troubleshooting

### Custom Features Best Practices

Based on Fusion 360 API requirements:

- **Compute Events**: Handle regeneration properly
- **Entity Dependencies**: Track dependent geometry correctly
- **Parameter Validation**: Robust input checking
- **Timeline Integration**: Proper feature lifecycle management
- **Error Recovery**: Graceful failure handling

### Testing Strategy

- **Manual Testing**: Load/unload lifecycle verification
- **Command Testing**: UI interaction and parameter validation
- **Custom Feature Testing**: Timeline regeneration and compute events
- **Error Testing**: Invalid input and edge case handling
- **Version Testing**: Python 3.9 compatibility verification

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Next Steps

1. **Run the Demo**: Install and test the Hello World command
2. **Understand the Structure**: Review the code organization
3. **Follow Development Plan**: Implement features according to [PLAN.md](../PLAN.md)
4. **Check Requirements**: Ensure compliance with [REQUIREMENTS.md](../REQUIREMENTS.md)
5. **Review Architecture**: Understand the design from [ARCHITECTURE.md](../ARCHITECTURE.md)

## Contributing

- Follow the established project structure
- Maintain Python 3.9 compatibility
- Add comprehensive error handling
- Update documentation for new features
- Test thoroughly before committing changes

## Support

- Check version compatibility first
- Review installation instructions
- Test with the Hello World command
- Report issues with system information from `version_check.py`