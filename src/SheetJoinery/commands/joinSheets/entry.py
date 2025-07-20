import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ...lib.utils.version_check import perform_startup_version_check
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# Create command
CREATE_CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_create'
CREATE_CMD_NAME = 'Join Sheets'
CREATE_CMD_Description = 'Sheet Joinery'

# Edit command
EDIT_CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_edit'
EDIT_CMD_NAME = 'Edit Join Sheets'
EDIT_CMD_Description = 'Edit Sheet Joinery Feature'

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidModifyPanel'
COMMAND_BESIDE_ID = 'FusionPartingLineSplitCmd'  # Empty string places at end of panel
# Specify that the command will be promoted to the panel.
IS_PROMOTED = False

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Global custom feature definition - created once when add-in loads
custom_feature_definition = None

# Global variable to store the custom feature being edited
_edited_custom_feature = None


# Executed when add-in is run.
def start():
    try:
        futil.log(f'Starting {CREATE_CMD_NAME}...')
        
        # Perform version compatibility check
        if not perform_startup_version_check():
            futil.log('ERROR: Version check failed, aborting add-in startup')
            return
        
        # Create the main command definition for creating new features
        cmd_def = ui.commandDefinitions.addButtonDefinition(CREATE_CMD_ID, CREATE_CMD_NAME, CREATE_CMD_Description, ICON_FOLDER)
        futil.log(f'Created create command definition: {CREATE_CMD_ID}')
        futil.add_handler(cmd_def.commandCreated, command_created)
        
        # Create the edit command definition for editing existing features
        edit_cmd_def = ui.commandDefinitions.addButtonDefinition(EDIT_CMD_ID, EDIT_CMD_NAME, EDIT_CMD_Description, ICON_FOLDER)
        futil.log(f'Created edit command definition: {EDIT_CMD_ID}')
        futil.add_handler(edit_cmd_def.commandCreated, edit_command_created)
        
        # Now create the custom feature definition with the edit command ID
        create_custom_feature_definition()

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
    panel = workspace.toolbarPanels.itemById(PANEL_ID) if workspace else None
    command_control = panel.controls.itemById(CREATE_CMD_ID) if panel else None
    command_definition = ui.commandDefinitions.itemById(CREATE_CMD_ID)
    edit_command_definition = ui.commandDefinitions.itemById(EDIT_CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definitions
    if command_definition:
        command_definition.deleteMe()
        
    if edit_command_definition:
        edit_command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CREATE_CMD_NAME} Command Created Event')

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
    futil.log(f'{CREATE_CMD_NAME} Command Execute Event')

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
            
        # Create a new feature (this is the "create" command)
        create_join_sheets_feature(design, text, expression)
        
    except Exception as e:
        futil.log(f'Error in command_execute: {str(e)}')
        ui.messageBox(f'Error creating feature: {str(e)}')


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CREATE_CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CREATE_CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CREATE_CMD_NAME} Validate Input Event')

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
    futil.log(f'{CREATE_CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


# Edit command handlers
def edit_command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{EDIT_CMD_NAME} Command Created Event')

    # Get the specific custom feature being edited (per API documentation)
    global _edited_custom_feature
    _edited_custom_feature = None
    
    try:
        futil.log(f'ActiveSelections count: {ui.activeSelections.count}')
        
        if ui.activeSelections.count > 0:
            _edited_custom_feature = ui.activeSelections.item(0).entity
            if _edited_custom_feature:
                futil.log(f'Successfully found custom feature to edit: {_edited_custom_feature.name}')
                futil.log(f'Custom feature entity token: {_edited_custom_feature.entityToken}')
            else:
                futil.log('activeSelections.item(0).entity is None')
        else:
            futil.log('No active selections found')
            
    except Exception as e:
        futil.log(f'Error getting edited custom feature: {str(e)}')
        _edited_custom_feature = None

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Create the same inputs as the create command
    text_input = inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Enter some text.', 1, False)

    # Create a value input field and set the default using 1 unit of the default length unit.
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')
    value_input = inputs.addValueInput('value_input', 'Some Value', defaultLengthUnits, default_value)
    
    # Populate with current values from the feature being edited
    if _edited_custom_feature:
        stored_text, stored_value = get_feature_parameters(_edited_custom_feature)
        text_input.text = stored_text
        value_input.expression = stored_value
        futil.log(f'Populated dialog with: text="{stored_text}", value="{stored_value}"')

    # Connect to the edit-specific event handlers
    futil.add_handler(args.command.execute, edit_command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, edit_command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, edit_command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, edit_command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, edit_command_destroy, local_handlers=local_handlers)


def edit_command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{EDIT_CMD_NAME} Command Execute Event')

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
            
        # Use the global edited feature
        global _edited_custom_feature
        if _edited_custom_feature:
            # Update the existing feature using the global reference
            update_join_sheets_feature(design, _edited_custom_feature.entityToken, text, expression)
            futil.log(f'Successfully updated feature: {_edited_custom_feature.name}')
        else:
            futil.log('_edited_custom_feature is None in execute handler')
        
    except Exception as e:
        futil.log(f'Error in edit_command_execute: {str(e)}')
        ui.messageBox(f'Error updating feature: {str(e)}')


def edit_command_preview(args: adsk.core.CommandEventArgs):
    futil.log(f'{EDIT_CMD_NAME} Command Preview Event')


def edit_command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    futil.log(f'{EDIT_CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


def edit_command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f'{EDIT_CMD_NAME} Validate Input Event')
    inputs = args.inputs
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def edit_command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{EDIT_CMD_NAME} Command Destroy Event')


def create_custom_feature_definition():
    """Create the CustomFeatureDefinition when add-in loads (best practice)"""
    global custom_feature_definition
    try:
        # Use company name in ID as recommended
        feature_id = f'{config.COMPANY_NAME}.JoinSheets'
        default_name = 'Join Sheets'
        icon_folder = ICON_FOLDER
        
        custom_feature_definition = adsk.fusion.CustomFeatureDefinition.create(feature_id, default_name, icon_folder)
        
        # Set the edit command ID to enable "Edit Feature" functionality
        custom_feature_definition.editCommandId = EDIT_CMD_ID
        
        # Add the compute handler to the definition
        futil.add_handler(custom_feature_definition.customFeatureCompute, compute_join_sheets_feature, local_handlers=local_handlers)
        
        futil.log(f'Created CustomFeatureDefinition: {feature_id}')
        
    except Exception as e:
        futil.log(f'Error creating CustomFeatureDefinition: {str(e)}')
        raise


def create_join_sheets_feature(design, description_text, tolerance_value):
    """Create a Join Sheets custom feature instance in the timeline"""
    try:
        if not custom_feature_definition:
            raise Exception("CustomFeatureDefinition not initialized")
            
        # Get the root component
        root_comp = design.rootComponent
        custom_features = root_comp.features.customFeatures
        
        # Create the custom feature input using the pre-created definition
        custom_feature_input = custom_features.createInput(custom_feature_definition)
        custom_feature = custom_features.add(custom_feature_input)
        
        # Store the parameters in the feature for later retrieval
        store_feature_parameters(custom_feature, description_text, tolerance_value)
        
        futil.log(f'Successfully created Join Sheets custom feature: {custom_feature.name}')
        return custom_feature
        
    except Exception as e:
        futil.log(f'Error creating Join Sheets feature: {str(e)}')
        raise


def update_join_sheets_feature(design, feature_token, description_text, tolerance_value):
    """Update an existing Join Sheets custom feature"""
    try:
        # Find the existing feature by its token
        root_comp = design.rootComponent
        custom_features = root_comp.features.customFeatures
        
        existing_feature = None
        for feature in custom_features:
            if feature.entityToken == feature_token:
                existing_feature = feature
                break
                
        if not existing_feature:
            futil.log(f'Could not find existing feature with token: {feature_token}')
            # Fallback to creating a new feature
            return create_join_sheets_feature(design, description_text, tolerance_value)
            
        # Update the stored parameters
        store_feature_parameters(existing_feature, description_text, tolerance_value)
        
        # The feature will automatically recompute when parameters change
        # No need to rollTo which moves the timeline marker
        
        futil.log(f'Successfully updated Join Sheets custom feature: {existing_feature.name}')
        return existing_feature
        
    except Exception as e:
        futil.log(f'Error updating Join Sheets feature: {str(e)}')
        raise


def store_feature_parameters(custom_feature, description_text, tolerance_value):
    """Store parameters in the custom feature for later retrieval"""
    try:
        # Use attributes to store our parameters
        attrs = custom_feature.attributes
        group_name = config.ADDIN_ID
        
        # Store the parameters as attributes
        attrs.add(group_name, 'description_text', description_text)
        attrs.add(group_name, 'tolerance_value', str(tolerance_value))
        
        futil.log(f'Stored parameters in feature: text="{description_text}", value="{tolerance_value}"')
        
    except Exception as e:
        futil.log(f'Error storing feature parameters: {str(e)}')


def get_feature_parameters(custom_feature):
    """Retrieve stored parameters from a custom feature"""
    try:
        attrs = custom_feature.attributes
        group_name = config.ADDIN_ID
        
        description_text = attrs.itemByName(group_name, 'description_text')
        tolerance_value = attrs.itemByName(group_name, 'tolerance_value')
        
        text = description_text.value if description_text else 'Default text'
        value = tolerance_value.value if tolerance_value else '1'
        
        return text, value
        
    except Exception as e:
        futil.log(f'Error retrieving feature parameters: {str(e)}')
        return 'Default text', '1'


def compute_join_sheets_feature(args):
    """Compute handler for the Join Sheets custom feature"""
    try:
        custom_feature = args.customFeature
        futil.log(f'Computing Join Sheets feature: {custom_feature.name}')
        
        # This is where we would implement the actual joinery generation logic
        # For now, just mark the compute as successful
        args.isComputed = True
        
    except Exception as e:
        futil.log(f'Error computing Join Sheets feature: {str(e)}')
        args.isComputed = False
