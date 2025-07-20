import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_helloWorld'
CMD_NAME = 'Join Sheets'
CMD_Description = 'Sheet Joinery'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidModifyPanel'
COMMAND_BESIDE_ID = 'FusionPartingLineSplitCmd'  # Empty string places at end of panel

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    try:
        futil.log(f'Starting {CMD_NAME}...')
        
        # Create a command Definition.
        cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
        futil.log(f'Created command definition: {CMD_ID}')

        # Define an event handler for the command created event. It will be called when the button is clicked.
        futil.add_handler(cmd_def.commandCreated, command_created)

        # ******** Add a button into the UI so the user can run the command. ********
        # Get the target workspace the button will be created in.
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if not workspace:
            futil.log(f'ERROR: Could not find workspace: {WORKSPACE_ID}')
            return
        futil.log(f'Found workspace: {WORKSPACE_ID}')

        # Get the panel the button will be created in.
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if not panel:
            futil.log(f'ERROR: Could not find panel: {PANEL_ID}')
            return
        futil.log(f'Found panel: {PANEL_ID}')

        # Create the button command control in the UI after the specified existing command.
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
        if not control:
            futil.log(f'ERROR: Failed to add command to panel')
            return
        futil.log(f'Added command control to panel')

        # Specify if the command is promoted to the main toolbar. 
        control.isPromoted = IS_PROMOTED
        futil.log(f'Command setup complete - promoted: {IS_PROMOTED}')
        
    except Exception as e:
        futil.log(f'ERROR in start(): {str(e)}')
        ui.messageBox(f'Failed to start Hello World command: {str(e)}')


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Create a simple text box input.
    inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Enter some text.', 1, False)

    # Create a value input field and set the default using 1 unit of the default length unit.
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')
    inputs.addValueInput('value_input', 'Some Value', defaultLengthUnits, default_value)

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    try:
        # Get a reference to your command's inputs.
        inputs = args.command.commandInputs
        text_box: adsk.core.TextBoxCommandInput = inputs.itemById('text_box')
        value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

        # Get input values
        text = text_box.text
        expression = value_input.expression
        
        # Get the active design
        design = app.activeProduct
        if not design:
            ui.messageBox('No active design found')
            return
            
        # Create a "Join Sheets" custom feature in the timeline
        create_join_sheets_feature(design, text, expression)
        
        # Show success message
        ui.messageBox(f'Created "Join Sheets" feature in timeline!<br>Text: {text}<br>Value: {expression}')
        
    except Exception as e:
        futil.log(f'Error in command_execute: {str(e)}')
        ui.messageBox(f'Error creating feature: {str(e)}')


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


def create_join_sheets_feature(design, description_text, tolerance_value):
    """Create a Join Sheets custom feature in the timeline"""
    try:
        # Get the root component
        root_comp = design.rootComponent
        
        # Create a custom feature definition
        custom_features = root_comp.features.customFeatures
        
        # Create the custom feature definition with required parameters
        feature_id = 'JoinSheetsFeature'
        default_name = 'Join Sheets'
        icon_folder = ICON_FOLDER  # Use the same icon folder as the command
        
        custom_feature_def = adsk.fusion.CustomFeatureDefinition.create(feature_id, default_name, icon_folder)
        
        # Set additional properties
        custom_feature_def.description = f'Join Sheets: {description_text} | Tolerance: {tolerance_value}mm'
        
        # Add the compute handler to the definition before creating the feature
        futil.add_handler(custom_feature_def.customFeatureCompute, compute_join_sheets_feature, local_handlers=local_handlers)
        
        # Create the custom feature input and add it to the timeline
        custom_feature_input = custom_features.createInput(custom_feature_def)
        custom_feature = custom_features.add(custom_feature_input)
        
        futil.log(f'Successfully created Join Sheets custom feature: {custom_feature.name}')
        return custom_feature
        
    except Exception as e:
        futil.log(f'Error creating Join Sheets feature: {str(e)}')
        raise


def compute_join_sheets_feature(args):
    """Compute handler for the Join Sheets custom feature"""
    try:
        custom_feature = args.customFeature
        futil.log(f'Computing Join Sheets feature: {custom_feature.name}')
        
        # For now, just mark the compute as successful
        # This is where we would implement the actual joinery generation logic
        futil.log(f'Feature ID: {custom_feature.definition.id}')
        futil.log(f'Feature name: {custom_feature.name}')
        
        # Mark the compute as successful
        args.isComputed = True
        futil.log('Join Sheets feature compute completed successfully')
        
    except Exception as e:
        futil.log(f'Error computing Join Sheets feature: {str(e)}')
        # Just mark as failed, don't try to set computeStatus
        args.isComputed = False
