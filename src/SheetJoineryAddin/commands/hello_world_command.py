"""
Hello World Command - Minimal demonstration of Fusion 360 Custom Feature API

This command creates a simple custom feature that demonstrates:
1. Custom Feature definition and creation
2. Parameter management
3. Timeline integration
4. Basic compute functionality
"""

import adsk.core
import adsk.fusion
import traceback
import sys

class HelloWorldCommand:
    """Hello World command implementation"""
    
    def __init__(self):
        self._app = adsk.core.Application.get()
        self._ui = self._app.userInterface
        self._design = None
        self._command_id = 'SheetJoineryHelloWorld'
        self._command_name = 'Hello World Custom Feature'
        self._command_tooltip = 'Creates a simple custom feature demonstration'
        self._handlers = []  # Keep handlers in scope
        
    def on_create(self):
        """Create the command definition and add it to the UI"""
        try:
            # Get the design workspace
            design_workspace = self._ui.workspaces.itemById('FusionSolidEnvironment')
            if not design_workspace:
                self._ui.messageBox('Could not find Design workspace')
                return
                
            # Get the CREATE toolbar panel
            create_panel = design_workspace.toolbarPanels.itemById('SolidCreatePanel')
            if not create_panel:
                self._ui.messageBox('Could not find CREATE panel')
                return
            
            # Create command definition
            cmd_def = self._ui.commandDefinitions.addButtonDefinition(
                self._command_id,
                self._command_name,
                self._command_tooltip
            )
            
            # Create and connect command created handler
            command_created_handler = CommandCreatedHandler(self)
            cmd_def.commandCreated.add(command_created_handler)
            self._handlers.append(command_created_handler)
            
            # Add the command to the CREATE panel
            create_panel.controls.addCommand(cmd_def)
            
        except:
            self._ui.messageBox('Failed to create Hello World command:\n{}'.format(traceback.format_exc()))
    
    def on_command_created(self, args):
        """Called when the command is created"""
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            # Add command inputs
            inputs.addStringValueInput('feature_name', 'Feature Name', 'Hello World Feature')
            inputs.addStringValueInput('message', 'Message', 'Hello from Sheet Joinery!')
            inputs.addBoolValueInput('create_sketch', 'Create Demo Sketch', True, '', True)
            
            # Create and connect command event handlers
            execute_handler = CommandExecuteHandler(self)
            execute_preview_handler = CommandExecutePreviewHandler(self)
            validate_inputs_handler = CommandValidateInputsHandler(self)
            
            cmd.execute.add(execute_handler)
            cmd.executePreview.add(execute_preview_handler)
            cmd.validateInputs.add(validate_inputs_handler)
            
            # Keep handlers in scope
            self._handlers.extend([execute_handler, execute_preview_handler, validate_inputs_handler])
            
        except:
            self._ui.messageBox('Failed to setup command:\n{}'.format(traceback.format_exc()))
    
    def on_validate_inputs(self, args):
        """Validate command inputs"""
        try:
            inputs = args.command.commandInputs
            
            # Validate feature name is not empty
            name_input = inputs.itemById('feature_name')
            if not name_input.value.strip():
                args.areInputsValid = False
                return
                
            args.areInputsValid = True
            
        except:
            args.areInputsValid = False
    
    def on_execute_preview(self, args):
        """Preview the command execution"""
        # For this demo, we don't need preview functionality
        pass
    
    def on_execute(self, args):
        """Execute the command"""
        try:
            inputs = args.command.commandInputs
            
            # Get input values
            feature_name = inputs.itemById('feature_name').value
            message = inputs.itemById('message').value
            create_sketch = inputs.itemById('create_sketch').value
            
            # Get the active design
            self._design = self._app.activeProduct
            if not self._design:
                self._ui.messageBox('No active design found')
                return
            
            # Create the custom feature
            self._create_hello_world_feature(feature_name, message, create_sketch)
            
        except:
            self._ui.messageBox('Failed to execute command:\n{}'.format(traceback.format_exc()))
    
    def _create_hello_world_feature(self, name, message, create_sketch):
        """Create a Hello World custom feature"""
        try:
            # Get the root component
            root_comp = self._design.rootComponent
            
            # Create a custom feature definition
            custom_features = root_comp.features.customFeatures
            custom_feature_def = adsk.fusion.CustomFeatureDefinition.create()
            
            # Set basic properties
            custom_feature_def.id = 'HelloWorldFeature'
            custom_feature_def.displayName = name
            custom_feature_def.description = f'Demo custom feature: {message}'
            
            # Create custom parameters
            params = custom_feature_def.customParameters
            message_param = params.add('message', adsk.core.ValueInput.createByString(message))
            create_sketch_param = params.add('create_sketch', adsk.core.ValueInput.createByBoolean(create_sketch))
            
            # Create the feature entities (if creating sketch)
            entities = []
            if create_sketch:
                # Create a simple demonstration sketch
                demo_sketch = self._create_demo_sketch(root_comp)
                if demo_sketch:
                    entities.append(demo_sketch)
            
            # Set the entities for the custom feature
            if entities:
                custom_feature_def.dependentEntities = entities
            
            # Create the custom feature
            custom_feature_input = custom_features.createInput(custom_feature_def)
            custom_feature = custom_features.add(custom_feature_input)
            
            # Create and connect custom feature compute handler
            compute_handler = CustomFeatureComputeHandler(self)
            custom_feature.customFeatureCompute.add(compute_handler)
            self._handlers.append(compute_handler)
            
            # Show success message
            self._ui.messageBox(f'Created custom feature: {name}\nMessage: {message}\nPython Version: {sys.version_info.major}.{sys.version_info.minor}')
            
        except:
            self._ui.messageBox('Failed to create custom feature:\n{}'.format(traceback.format_exc()))
    
    def _create_demo_sketch(self, component):
        """Create a simple demonstration sketch"""
        try:
            # Get the XY plane
            xy_plane = component.xYConstructionPlane
            
            # Create a new sketch
            sketches = component.sketches
            sketch = sketches.add(xy_plane)
            sketch.name = 'Hello World Demo Sketch'
            
            # Draw a simple rectangle
            lines = sketch.sketchCurves.sketchLines
            point1 = adsk.core.Point3D.create(0, 0, 0)
            point2 = adsk.core.Point3D.create(10, 10, 0)
            lines.addTwoPointRectangle(point1, point2)
            
            # Add some text
            texts = sketch.sketchTexts
            text_input = texts.createInput2('Hello\nFusion!', 1.0)
            text_input.setAsAlongPath(lines.item(0), False, adsk.fusion.HorizontalAlignments.CenterHorizontalAlignment)
            texts.add(text_input)
            
            return sketch
            
        except:
            self._ui.messageBox('Failed to create demo sketch:\n{}'.format(traceback.format_exc()))
            return None
    
    def on_custom_feature_compute(self, args):
        """Handle custom feature compute events"""
        try:
            # This is where we would implement the actual joint generation logic
            # For now, just demonstrate that the compute event is working
            
            custom_feature = args.customFeature
            
            # Get parameter values
            params = custom_feature.definition.customParameters
            message_param = params.itemById('message')
            
            if message_param:
                message = message_param.expression
                
                # Update the feature description
                custom_feature.definition.description = f'Computed: {message} at {adsk.core.Application.get().executeTextCommand("Timeline.GetCurrentTimeString")}'
            
            # Mark compute as successful
            args.isComputed = True
            
        except:
            # Mark compute as failed
            args.isComputed = False
            args.computeStatus = f'Compute failed: {traceback.format_exc()}'


# Event Handler Classes
class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Handler for command created events"""
    
    def __init__(self, command):
        super().__init__()
        self._command = command
    
    def notify(self, args):
        self._command.on_command_created(args)


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    """Handler for command execute events"""
    
    def __init__(self, command):
        super().__init__()
        self._command = command
    
    def notify(self, args):
        self._command.on_execute(args)


class CommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    """Handler for command execute preview events"""
    
    def __init__(self, command):
        super().__init__()
        self._command = command
    
    def notify(self, args):
        self._command.on_execute_preview(args)


class CommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    """Handler for validate inputs events"""
    
    def __init__(self, command):
        super().__init__()
        self._command = command
    
    def notify(self, args):
        self._command.on_validate_inputs(args)


class CustomFeatureComputeHandler(adsk.fusion.CustomFeatureEventHandler):
    """Handler for custom feature compute events"""
    
    def __init__(self, command):
        super().__init__()
        self._command = command
    
    def notify(self, args):
        self._command.on_custom_feature_compute(args)