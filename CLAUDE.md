# Claude Memory for Fusion Sheet Joinery Project

## Project Context
- **Project**: Autodesk Fusion 360 Sheet Goods Joinery Add-in
- **Purpose**: Automate tab-and-slot joinery for sheet goods fabrication
- **Target**: Flat-pack furniture prototyping and CNC router manufacturing
- **Materials**: Plywood, MDF, composite sheets (tested 2mm to 20mm, but not thickness-limited)

## Requirements Standards
**IMPORTANT**: This project uses RFC 2119 primary modal verbs for all requirements:
- **MUST** - Absolute requirement
- **MUST NOT** - Absolute prohibition  
- **SHOULD** - Strong recommendation
- **SHOULD NOT** - Strong recommendation against
- **MAY** - Optional or permissible

**Never use "SHALL" in requirements** - always use "MUST" instead.

## Measurement Standards
**IMPORTANT**: This project uses metric/SI units as the primary measurement system:
- **Primary Units**: Metric/SI (mm, cm, m for length; kg for mass)
- **Derived Units**: Imperial units are derived from metric when needed
- **Documentation**: All specifications use metric units first
- **User Interface**: Support both metric and imperial, but default to user's Fusion preference
- **Example**: "2mm to 20mm (tested range)" - metric first, imperial in parentheses when helpful

## Material Thickness Support
**Testing Range**: 2mm to 20mm (roughly 1 order of magnitude)
- **Tested/Validated**: Joint algorithms verified within this range
- **Outside Range**: Add-in should still function but not developer-tested
- **No Hard Limits**: Don't enforce thickness constraints - let users experiment
- **Warning Approach**: Inform users when outside tested range rather than blocking

## Key Technical Decisions
- **Custom Features API**: MUST use for parametric timeline integration
- **Sheet Metal BRep Filtering**: Use Fusion's sheet metal body types for performance
- **CAM Limitations**: Work around lack of custom operations with geometry overrides
- **Cross-Platform**: MUST support Windows and macOS
- **Metadata Strategy**: Face attributes for Design-to-CAM communication

## API Constraints
- Custom Features API is preview status (breaking changes possible)
- CAM API cannot create setups or custom operations
- No preGenerate/postGenerate hooks available
- Must use geometry modification approach in CAM

## Performance Targets
- 100+ intersections: <10 seconds
- Parameter updates: <1 second  
- Memory usage: <100MB typical assemblies
- Timeline regeneration: <5 seconds
- Precision: ±0.05mm joint accuracy, ±0.01mm detection precision

## Development Timeline
- 12 weeks total
- Phase 1-2: Foundation & Custom Features (Weeks 1-5)
- Phase 3-4: Joint Types & CAM Integration (Weeks 6-9)  
- Phase 5-6: Polish & Release (Weeks 10-12)

## Post-MVP Enhancements
### Material-Aware Cutting Direction Intelligence
- **Wood/Anisotropic Materials**: Validate or enforce conventional milling
  - Wood grain direction affects cutting forces
  - Plywood layers can cause tear-out with climb milling
  - MDF and composite sheets benefit from conventional milling
- **Metal/Isotropic Materials**: Validate or enforce climb milling
  - Uniform material properties allow climb milling benefits
  - Better surface finish and tool life
  - Aluminum, steel, brass sheet goods
- **Implementation**: Check `sidewaysCompensation` parameter in CAM operations
  - Read material type from Design module metadata
  - Warn or auto-correct cutting direction based on material properties
  - Integration with dogbone placement optimization