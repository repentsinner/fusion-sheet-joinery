# Fusion 360 Sheet Goods Joinery Add-in Requirements

## Executive Summary

This document specifies requirements for an Autodesk Fusion 360 add-in that automates the creation of tab-and-slot joinery for sheet goods fabrication. The add-in targets flat-pack furniture prototyping, design validation, and production fabrication workflows with CNC router manufacturing.

### Project Scope
- **Primary Use Case**: Flat-pack furniture prototyping and fabrication
- **Material Target**: Plywood, MDF, and composite sheets (1/8" to 3/4" nominal thickness)
- **Manufacturing Process**: CNC router 3-axis machining
- **Assembly Method**: Glued/welded joints or external fasteners
- **MVP Focus**: Automatic joint generation with manual override capabilities

## Functional Requirements

### FR-001: Automatic Intersection Detection
**Priority**: High

The add-in SHALL automatically detect overlapping sheet body volumes and identify potential joint locations.

**Acceptance Criteria**:
- Scan assembly for all sheet body intersections
- Classify intersection types (T-joints, cross-joints, edge-to-edge)
- Calculate intersection angles and orientations
- Support batch processing of 100+ intersections efficiently
- Detect intersection regions with sub-millimeter precision

### FR-002: Joint Type Generation
**Priority**: High

The add-in SHALL generate appropriate joint types based on intersection geometry.

**Supported Joint Types**:
- **Finger Joints**: Alternating tab/slot pattern for edge-to-edge connections
- **Box Joints**: Corner connections with configurable tab count
- **T-Slot Joints**: Perpendicular sheet insertion
- **Mortise and Tenon**: Variations suitable for sheet goods

**Acceptance Criteria**:
- Automatically select optimal joint type based on intersection geometry
- Generate complementary tabs and slots between mating components
- Maintain material thickness-driven joint sizing
- Support configurable tolerance and clearance values
- Handle material thickness variations (1/8" to 3/4")

### FR-003: Parametric Timeline Integration
**Priority**: High

The add-in MUST use Fusion's Custom Features API (or the most advanced parametric API capability available) to create true parametric timeline integration with automatic regeneration.

**API Requirement**: This feature SHALL be implemented using `adsk.fusion.CustomFeature` to ensure full parametric behavior equivalent to native Fusion features.

**Acceptance Criteria**:
- Create single "Sheet Joinery" node in timeline using Custom Features API
- Automatically regenerate when upstream geometry changes (leverage CustomFeature compute events)
- Maintain associative relationships with source sheet bodies through feature dependencies
- Support timeline rollback and feature editing via standard Fusion feature editing patterns
- Update joint positions, sizes, and clearances dynamically when base geometry modifications occur
- Implement custom compute functionality for base features, sketches, and combine operations

### FR-004: Cross-Workspace Material Adjustment
**Priority**: Medium

The add-in SHALL support material thickness adjustments in CAM workspace.

**Acceptance Criteria**:
- Generate joints using nominal sheet thickness in Design
- Allow measured material thickness override in CAM
- Update slot dimensions for actual stock in manufacturing
- Maintain design intent while accommodating real-world materials
- Preserve joint functionality across thickness variations

### FR-005: CNC Router Dogbone Integration
**Priority**: Medium

The add-in SHALL provide intelligent dogbone placement for CNC router compatibility.

**Design Module Requirements**:
- Tag corner types: CriticalSharp, BestEffort, Decorative
- Mark faces with dogbone placement hints
- Store joint geometry context and clearance requirements

**CAM Module Requirements**:
- Read Design module metadata for corner classification
- Automatically place dogbones based on tool diameter
- Support corner dogbones and face dogbones
- Respect CriticalSharp constraints for joint functionality

## User Interface Requirements

### UI-001: Selection Workflows
**Priority**: High

The add-in SHALL provide intuitive selection methods following Fusion patterns.

**Default Workflow - Auto-Detection**:
- "Process All Intersections" mode (default)
- One-click processing of entire assembly
- Progress indicator for large assemblies
- Summary report of joints created and warnings

**Manual Workflow - Selection-Based**:
- Body-pair selection for specific intersections
- Face-pair selection for precise control
- Real-time preview with assembly animation
- Visual highlighting of intersection zones

### UI-002: Parameter Configuration
**Priority**: Medium

The add-in SHALL provide comprehensive joint parameterization.

**Global Settings Panel**:
- Material type presets (Plywood, MDF, Hardwood, Custom)
- Default tolerance and clearance values
- Assembly method preferences
- Units preference (inherit from Fusion settings)

**Joint-Specific Parameters**:

*Finger Joints*:
- Finger count (3-20, default: Auto)
- Finger width (default: MaterialThickness × 1.5)
- Finger ratio (0.3-2.0, default: 1.0)
- End condition (FullFinger, HalfFinger, Symmetric)
- Minimum length (default: MaterialThickness × 3)

*Box Joints*:
- Tab width (default: MaterialThickness × 2)
- Tab count (min: 1, default: Auto)
- Corner type (Flush, Proud, Recessed)
- Tab alignment (Centered, EdgeAligned)

### UI-003: Override and Editing
**Priority**: Medium

The add-in SHALL support manual overrides following Fusion editing patterns.

**Timeline-Based Editing**:
- Right-click Custom Feature → "Edit Joinery Feature"
- Properties panel integration for selected joints
- Context menu joint type overrides
- "Reset to Auto" functionality

**Override Hierarchy**:
1. Global template settings
2. Joint type defaults
3. Individual joint overrides
4. Local parameter adjustments

## Technical Architecture Requirements

### TA-001: API Integration
**Priority**: High

The add-in SHALL leverage appropriate Fusion 360 APIs.

**Design Module APIs**:
- `adsk.fusion.CustomFeature` for parametric timeline integration
- `adsk.fusion.BRepBody.intersect()` for geometry analysis
- `adsk.fusion.Attributes` for metadata tagging
- `adsk.fusion.SelectionCommandInput` for user selections

**CAM Module APIs**:
- `adsk.cam.GeometrySelection` for CAM overrides
- CAM workspace command integration
- Cross-workspace data synchronization

### TA-002: Data Architecture
**Priority**: High

The add-in SHALL implement robust data management.

**Metadata System**:
```python
# Joint metadata example
face.attributes.add('JoineryAddin', 'JointType', 'FingerJoint')
face.attributes.add('JoineryAddin', 'DogboneHint', 'CornerDogbone')
face.attributes.add('JoineryAddin', 'MaterialThickness', '0.75')
face.attributes.add('JoineryAddin', 'ToleranceClass', 'Precision')
```

**Performance Requirements**:
- Handle 100+ sheet intersections efficiently
- Sub-second response for parameter updates
- Memory-efficient attribute storage
- Cached geometry analysis results

### TA-003: Error Handling
**Priority**: Medium

The add-in SHALL implement robust error handling following Fusion patterns.

**Error Scenarios**:
- Material too thin for selected joint type
- Complex intersection geometry
- Geometric conflicts between joints
- Invalid orientations for joint types

**Error Response**:
- Skip problematic intersections with detailed warnings
- Continue processing valid joints
- Require user re-specification for failed cases
- Provide actionable error messages with suggested solutions

## Material and Manufacturing Requirements

### MR-001: Material Support
**Priority**: High

The add-in SHALL support common sheet goods materials.

**Supported Materials**:
- Plywood (various grades and species)
- MDF (Medium Density Fiberboard)
- Composite sheet materials
- Material-agnostic design principles

**Thickness Range**:
- Minimum: 1/8" (3.175mm)
- Maximum: 3/4" (19.05mm)
- Support for both imperial and metric units
- Auto-detection from Fusion user preferences

### MR-002: Manufacturing Integration
**Priority**: High

The add-in SHALL support CNC router manufacturing workflows.

**CNC Compatibility**:
- 3-axis router toolpath compatibility
- Dogbone corner relief for sharp internal corners
- Tool diameter considerations for clearances
- Standard end mill compatibility (1/8", 1/4", 3/8", 1/2")

**Tolerance Management**:
- Configurable clearance values (default: 0.1mm)
- Material thickness variation handling
- Kerf compensation awareness
- Assembly fit optimization

## Quality and Performance Requirements

### QR-001: Accuracy
**Priority**: High

The add-in SHALL maintain high geometric accuracy.

**Precision Requirements**:
- Joint dimensional accuracy: ±0.05mm
- Intersection detection precision: ±0.01mm
- Parametric regeneration consistency: 100%
- Cross-workspace data integrity: 100%

### QR-002: Performance
**Priority**: Medium

The add-in SHALL meet performance benchmarks.

**Performance Targets**:
- Process 100 intersections: <10 seconds
- Parameter update response: <1 second
- Timeline regeneration: <5 seconds
- Memory usage: <100MB for typical assemblies

### QR-003: Usability
**Priority**: High

The add-in SHALL provide excellent user experience.

**Usability Requirements**:
- Intuitive workflow following Fusion patterns
- Comprehensive tooltips and help text
- Progress indicators for long operations
- Undo/redo support for all operations
- Keyboard shortcuts for common actions

## Success Criteria

### Primary Success Metrics
1. **Automation Rate**: >90% of detected intersections successfully automated
2. **Time Savings**: 80% reduction in manual joint creation time
3. **Accuracy**: <1% joint fit failures in test assemblies
4. **User Adoption**: Successful integration into existing Fusion workflows

### Technical Acceptance
1. All functional requirements implemented and tested
2. Performance benchmarks met under typical usage
3. Robust error handling with graceful degradation
4. Full parametric regeneration capability

## Future Considerations

### Post-MVP Enhancements
- Advanced joint types (dovetails, dados, rabbets)
- Assembly sequence optimization
- Structural analysis integration
- Multi-material support
- Cloud-based joint library
- Integration with Fusion's Generative Design

### API Dependencies
- Monitor Custom Features API evolution (currently preview)
- Adapt to Fusion 360 API changes and enhancements
- Leverage new CAM API capabilities as they become available

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-19  
**Status**: Draft for Review