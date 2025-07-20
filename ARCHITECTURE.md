# System Architecture

## Overview

The Fusion 360 Sheet Goods Joinery Add-in implements a dual-workspace architecture that bridges Fusion's Design and Manufacturing environments. The system uses Fusion's Custom Features API for parametric timeline integration while working around CAM API limitations through geometry modification and metadata tagging approaches.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fusion 360 Document                         │
├─────────────────────────────────────────────────────────────────┤
│  Design Workspace                    │  CAM Workspace           │
│  ┌─────────────────────────────────┐  │  ┌─────────────────────┐ │
│  │     Design Module               │  │  │   CAM Module        │ │
│  │  ┌─────────────────────────────┐│  │  │ ┌─────────────────┐ │ │
│  │  │   Custom Feature            ││  │  │ │ Geometry        │ │ │
│  │  │   (Sheet Joinery)           ││  │  │ │ Override        │ │ │
│  │  │                             ││  │  │ │ Engine          │ │ │
│  │  │ - Intersection Detection    ││  │  │ │                 │ │ │
│  │  │ - Joint Generation          ││  │  │ │ - Read Metadata │ │ │
│  │  │ - Metadata Tagging          ││  │  │ │ - Modify Ops    │ │ │
│  │  │ - Parametric Regeneration   ││  │  │ │ - Dogbone Logic │ │ │
│  │  └─────────────────────────────┘│  │  │ └─────────────────┘ │ │
│  └─────────────────────────────────┘  │  └─────────────────────┘ │
│              │                        │              │           │
│              │    Face Attributes     │              │           │
│              └────────────────────────┼──────────────┘           │
│                                       │                          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Design Module Components

#### 1. Custom Feature Engine
**File**: `design/custom_feature.py`

Implements Fusion's Custom Features API to create parametric timeline integration.

```python
class SheetJoineryFeature(adsk.fusion.CustomFeature):
    def __init__(self):
        self.intersection_detector = IntersectionDetector()
        self.joint_generator = JointGenerator()
        self.metadata_manager = MetadataManager()
    
    def compute(self, args):
        # Called automatically when upstream geometry changes
        intersections = self.intersection_detector.find_all()
        joints = self.joint_generator.create_joints(intersections)
        self.metadata_manager.tag_faces(joints)
```

**Responsibilities**:
- Timeline integration and parametric regeneration
- Custom compute event handling
- Feature editing and parameter management
- Dependency tracking with source geometry

#### 2. Intersection Detection Engine
**File**: `design/intersection_detector.py`

Analyzes sheet body geometry to identify potential joint locations, leveraging Fusion's sheet metal BRep types for efficient filtering.

```python
class IntersectionDetector:
    def find_all(self, bodies: List[BRepBody]) -> List[Intersection]:
        # Filter for sheet metal bodies first - major performance optimization
        sheet_bodies = self._filter_sheet_metal_bodies(bodies)
        
        intersections = []
        for i, body1 in enumerate(sheet_bodies):
            for body2 in sheet_bodies[i+1:]:
                if intersection := self._analyze_intersection(body1, body2):
                    intersections.append(intersection)
        return intersections
    
    def _filter_sheet_metal_bodies(self, bodies: List[BRepBody]) -> List[BRepBody]:
        """Filter for sheet metal BRep types - enforces sheet goods semantics"""
        sheet_bodies = []
        for body in bodies:
            # Leverage Fusion's sheet metal classification
            if (body.objectType == adsk.fusion.BRepBody.classType() and 
                hasattr(body, 'sheetMetalProperties') and 
                body.sheetMetalProperties):
                # Check if thickness is in our tested range (2mm to 20mm) for warnings
                thickness = body.sheetMetalProperties.thickness
                if self._validate_thickness_range(thickness):
                    sheet_bodies.append(body)
        return sheet_bodies
    
    def _analyze_intersection(self, body1, body2) -> Optional[Intersection]:
        # BRep geometry analysis with sheet metal context
        # Access actual sheet thickness from sheetMetalProperties
        thickness1 = body1.sheetMetalProperties.thickness
        thickness2 = body2.sheetMetalProperties.thickness
        # Calculate intersection volume, type, orientation
        pass
```

**Responsibilities**:
- **Sheet Metal Filtering**: Leverage Fusion's sheet metal BRep classification for semantic correctness
- **Thickness Validation**: Check tested range (2mm to 20mm) for user warnings, don't enforce limits
- **Performance Optimization**: Dramatically reduce intersection candidates by filtering non-sheet bodies
- **Intersection Analysis**: BRep geometry analysis with sheet metal context
- **Classification**: Intersection type determination (T-joint, cross-joint, edge-to-edge)

#### 3. Joint Generation Engine
**File**: `design/joint_generator.py`

Creates appropriate joint geometry based on intersection analysis.

```python
class JointGenerator:
    def create_joints(self, intersections: List[Intersection]) -> List[Joint]:
        joints = []
        for intersection in intersections:
            joint_type = self._determine_joint_type(intersection)
            joint = self._create_joint(intersection, joint_type)
            joints.append(joint)
        return joints
    
    def _create_joint(self, intersection: Intersection, joint_type: JointType) -> Joint:
        if joint_type == JointType.FINGER:
            return self._create_finger_joint(intersection)
        elif joint_type == JointType.BOX:
            return self._create_box_joint(intersection)
        # ... other joint types
```

**Joint Type Implementations**:
- `FingerJointGenerator`: Alternating tab/slot patterns
- `BoxJointGenerator`: Corner connection strategies
- `TSlotJointGenerator`: Perpendicular insertion logic
- `MortiseTenonGenerator`: Sheet goods variations

#### 4. Metadata Management System
**File**: `design/metadata_manager.py`

Manages face attribute tagging for cross-workspace communication.

```python
class MetadataManager:
    GROUP_NAME = 'JoineryAddin'
    
    def tag_face(self, face: BRepFace, metadata: Dict[str, str]):
        for key, value in metadata.items():
            face.attributes.add(self.GROUP_NAME, key, value)
    
    def read_face_metadata(self, face: BRepFace) -> Dict[str, str]:
        metadata = {}
        attrs = face.attributes.itemsByGroup(self.GROUP_NAME)
        for attr in attrs:
            metadata[attr.name] = attr.value
        return metadata
```

**Metadata Schema**:
```python
# Joint identification
face.attributes.add('JoineryAddin', 'JointType', 'FingerJoint')
face.attributes.add('JoineryAddin', 'JointID', 'joint_001')

# Manufacturing hints
face.attributes.add('JoineryAddin', 'DogboneHint', 'CornerDogbone')
face.attributes.add('JoineryAddin', 'DogboneReason', 'TabClearance')

# Dimensional data
face.attributes.add('JoineryAddin', 'NominalThickness', '9.0')
face.attributes.add('JoineryAddin', 'ToleranceClass', 'Precision')
```

### CAM Module Components

#### 1. Geometry Override Engine
**File**: `cam/geometry_override.py`

Modifies CAM operation geometry selections based on manufacturing parameters.

```python
class GeometryOverrideEngine:
    def prepare_for_manufacturing(self, measured_thickness: float):
        for setup in self._get_cam_setups():
            for operation in setup.operations:
                if self._is_contour_operation(operation):
                    self._override_operation_geometry(operation, measured_thickness)
    
    def _override_operation_geometry(self, operation, thickness):
        # Modify geometry selection for measured stock
        model_param = operation.parameters.itemByName('model')
        adjusted_faces = self._calculate_adjusted_geometry(thickness)
        model_param.value.value = adjusted_faces
```

**Responsibilities**:
- Read Design module metadata from face attributes
- Calculate geometry adjustments for measured stock thickness
- Override CAM operation geometry selections
- Maintain operation parameter consistency

#### 2. Dogbone Automation Engine
**File**: `cam/dogbone_engine.py`

Processes tagged faces to add appropriate corner relief for CNC routing.

```python
class DogboneEngine:
    def process_dogbones(self, tool_diameter: float):
        tagged_faces = self._find_dogbone_tagged_faces()
        for face in tagged_faces:
            hint = face.attributes.itemByName('JoineryAddin', 'DogboneHint').value
            if hint == 'CornerDogbone':
                self._add_corner_dogbone(face, tool_diameter)
            elif hint == 'FaceDogbone':
                self._add_face_dogbone(face, tool_diameter)
```

**Dogbone Strategies**:
- Corner dogbones for sharp internal corners
- Face dogbones for slot sidewall clearance
- Tool-diameter-specific sizing
- Joint-type-aware placement logic

### Cross-Workspace Communication

#### Data Flow Architecture
```
Design Module                          CAM Module
     ↓                                      ↑
Face Attributes ←→ Fusion Document ←→ Geometry Override
     ↓                                      ↑
Metadata Tags   ←→   Persistence    ←→  Manufacturing Logic
```

#### Attribute Persistence Strategy
- Attributes survive timeline regeneration
- Cross-workspace data integrity maintained
- Version compatibility through structured metadata
- Error recovery for missing/corrupted attributes

## API Integration Points

### Fusion 360 API Dependencies

#### Design Workspace APIs
```python
# Core APIs
import adsk.core
import adsk.fusion

# Custom Features (Preview API)
from adsk.fusion import CustomFeature, CustomFeatureDefinition

# Geometry Analysis
from adsk.fusion import BRepBody, BRepFace, BRepEdge
```

#### CAM Workspace APIs
```python
# CAM-specific APIs
import adsk.cam

# Operation Modification
from adsk.cam import Operation, GeometrySelection, Setup
```

### API Constraints and Workarounds

#### Custom Features API Limitations
- **Preview Status**: API subject to breaking changes
- **Compute Scope**: Limited to base features, sketches, combine operations
- **Development Overhead**: ~3x development time vs standard add-ins

#### CAM API Limitations
- **No Setup Creation**: Cannot create setups programmatically
- **Limited Operation Types**: Cannot create custom operation strategies
- **No Lifecycle Events**: No `preGenerate`/`postGenerate` hooks
- **Geometry Override Only**: Must work with existing operation framework

## Performance Architecture

### Optimization Strategies

#### Intersection Detection
```python
class OptimizedIntersectionDetector:
    def __init__(self):
        self._spatial_index = SpatialIndex()
        self._cache = IntersectionCache()
    
    def find_intersections(self, bodies):
        # Spatial indexing for O(n log n) vs O(n²) complexity
        candidates = self._spatial_index.query_intersections(bodies)
        
        # Cached results for repeated queries
        for candidate in candidates:
            if cached := self._cache.get(candidate):
                yield cached
            else:
                result = self._compute_intersection(candidate)
                self._cache.store(candidate, result)
                yield result
```

#### Memory Management
- Lazy evaluation for large assemblies
- Incremental processing with progress feedback
- Cached geometry analysis results
- Efficient attribute storage patterns

### Scalability Targets
- **100+ intersections**: <10 second processing
- **Parameter updates**: <1 second response time
- **Timeline regeneration**: <5 seconds for typical assemblies
- **Memory usage**: <100MB for standard furniture projects

## Error Handling Architecture

### Error Categories and Responses

#### Geometric Validation Errors
```python
class GeometricValidator:
    def validate_intersection(self, intersection) -> ValidationResult:
        errors = []
        
        if intersection.material_thickness < MIN_THICKNESS:
            errors.append(ValidationError.MATERIAL_TOO_THIN)
        
        if intersection.angle < MIN_JOINT_ANGLE:
            errors.append(ValidationError.INVALID_ORIENTATION)
        
        return ValidationResult(errors)
```

#### Error Recovery Strategies
- **Skip and Warn**: Continue processing valid intersections
- **Graceful Degradation**: Fall back to simpler joint types
- **User Feedback**: Detailed error messages with suggested solutions
- **State Recovery**: Rollback to last known good configuration

### Logging and Diagnostics
```python
class JoineryLogger:
    def __init__(self):
        self.log_level = LogLevel.INFO
        self.handlers = [ConsoleHandler(), FileHandler('joinery.log')]
    
    def log_intersection_analysis(self, intersections, errors):
        self.info(f"Processed {len(intersections)} intersections")
        for error in errors:
            self.warning(f"Skipped intersection: {error.reason}")
```

## Security and Data Integrity

### Attribute Security
- Namespace isolation using group names
- Validation of attribute data types and ranges
- Protection against attribute injection attacks
- Graceful handling of corrupted metadata

### Data Versioning
```python
class MetadataVersioning:
    CURRENT_VERSION = "1.0"
    
    def tag_with_version(self, face, metadata):
        metadata['_version'] = self.CURRENT_VERSION
        metadata['_timestamp'] = datetime.now().isoformat()
        self.metadata_manager.tag_face(face, metadata)
    
    def migrate_legacy_attributes(self, face):
        # Handle older attribute formats
        pass
```

## Testing Architecture

### Unit Testing Strategy
- Component isolation with mock Fusion APIs
- Geometric algorithm validation with known test cases
- Metadata persistence testing across workspace switches
- Error condition simulation and recovery validation

### Integration Testing
- Full workflow testing in Fusion environment
- Performance benchmarking with large assemblies
- Cross-workspace data integrity verification
- UI interaction and user experience testing

## Deployment Architecture

### Add-in Package Structure
```
SheetJoineryAddin/
├── manifest.yaml                 # Add-in configuration
├── __init__.py                  # Entry point
├── design/                      # Design workspace components
│   ├── custom_feature.py
│   ├── intersection_detector.py
│   ├── joint_generator.py
│   └── metadata_manager.py
├── cam/                         # CAM workspace components
│   ├── geometry_override.py
│   └── dogbone_engine.py
├── ui/                          # User interface components
│   ├── commands.py
│   ├── dialogs.py
│   └── event_handlers.py
├── utils/                       # Shared utilities
│   ├── geometry_utils.py
│   ├── validation.py
│   └── logging.py
└── tests/                       # Test suite
    ├── unit/
    ├── integration/
    └── fixtures/
```

### Configuration Management
- User preferences stored in Fusion settings
- Material presets and joint templates
- Performance tuning parameters
- Debug and logging configuration

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-19  
**Status**: Architecture Specification