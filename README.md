# Fusion 360 Sheet Goods Joinery Add-in

An Autodesk Fusion 360 add-in that automates tab-and-slot joinery creation for sheet goods fabrication, targeting flat-pack furniture prototyping and CNC router manufacturing.

## Overview

This add-in automatically detects intersecting sheet bodies and generates appropriate joinery (finger joints, box joints, T-slots, etc.) with intelligent dogbone placement for CNC router compatibility. It bridges Design and CAM workflows by preserving design intent while accommodating real-world manufacturing constraints.

## Key Features

- **Automatic Joint Detection**: Scans assemblies for sheet intersections and suggests optimal joint types
- **Parametric Integration**: Uses Fusion's Custom Features API for timeline integration and automatic regeneration
- **CNC Router Ready**: Intelligent dogbone placement with Design-to-CAM metadata flow
- **Material Flexibility**: Supports plywood, MDF, and composite sheets (tested 2-20mm range)
- **Manufacturing Workflow**: Nominal dimensions in Design, measured stock adjustments in CAM

## Installation

### Prerequisites
- Autodesk Fusion 360 (latest version recommended)
- Fusion 360 Personal or Commercial license with CAM workspace access

### Install Steps
1. Download the latest release from [Releases](../../releases)
2. Extract the add-in files to your Fusion 360 add-ins directory:
   - **Windows**: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - **macOS**: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
3. Launch Fusion 360
4. Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins**
5. Select the **Add-Ins** tab, find "Sheet Goods Joinery", and click **Run**
6. Check **Run on Startup** for automatic loading

## Usage

### Basic Workflow

#### 1. Design Phase
1. Create your sheet goods assembly in Fusion's Design workspace
2. Ensure sheet bodies intersect where you want joints
3. Access **SOLID** → **Sheet Joinery** → **Auto-Generate Joints**
4. Configure joint parameters in the dialog:
   - Material type (Plywood, MDF, Custom)
   - Nominal thickness
   - Tolerance settings
   - Joint type preferences
5. Click **OK** to generate joints automatically

The add-in creates a single "Sheet Joinery" feature in your timeline that regenerates automatically when upstream geometry changes.

#### 2. Manufacturing Phase (CAM Workspace)
1. Switch to **MANUFACTURE** workspace
2. Create your CAM setup normally
3. Before generating toolpaths, run **CAM** → **Sheet Joinery** → **Prepare for Manufacturing**
4. Enter measured material thickness (if different from nominal)
5. Review dogbone placement suggestions
6. Click **Apply** to update geometry for CNC routing

### Manual Override Options

- **Edit Timeline Feature**: Right-click the "Sheet Joinery" feature → **Edit Feature**
- **Individual Joint Control**: Select joint geometry → Properties panel for fine-tuning
- **Joint Type Override**: Right-click joint → **Override Joint Type** → Select from dropdown
- **Reset to Auto**: Use "Reset to Auto" button to return to algorithmic settings

### Joint Types Supported

- **Finger Joints**: Alternating tabs/slots for edge-to-edge connections
- **Box Joints**: Corner connections with configurable tab count
- **T-Slot Joints**: Perpendicular sheet insertion
- **Mortise & Tenon**: Sheet goods variations

## Known Limitations (MVP)

⚠️ **CAM API Constraints**: Due to current Fusion 360 CAM API limitations, the manufacturing workflow requires manual intervention:
- No automatic `preGenerate`/`postGenerate` operation hooks available
- Users must manually run "Prepare for Manufacturing" when Design changes
- Cannot create custom CAM operations - uses geometry modification approach instead

🔄 **Future Improvements**: When Autodesk expands CAM API capabilities, we plan to add:
- Automatic CAM sync with Design changes
- Custom CAM operation types for dogbone placement
- Assembly sequence optimization

## Technical Architecture

### Design Module
- **Custom Features API**: Creates parametric timeline integration
- **Intersection Detection**: BRep geometry analysis for joint placement
- **Metadata Tagging**: Face attributes for manufacturing hints

### CAM Module  
- **Geometry Override**: Modifies operation selections for measured stock
- **Dogbone Automation**: Processes tagged faces for corner relief
- **Cross-Workspace Sync**: Reads Design module metadata

## Development Status

- ✅ Requirements Complete
- 🔄 Implementation In Progress
- ⏳ Testing Phase
- ⏳ Beta Release

## Contributing

See [REQUIREMENTS.md](./REQUIREMENTS.md) for detailed specifications and development guidelines.

## License

[MIT License](./LICENSE)
