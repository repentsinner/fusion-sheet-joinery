import os

import adsk.core
import adsk.fusion

from ... import config
from ...lib import fusionAddInUtils as futil
from ...lib.utils.version_check import perform_startup_version_check

app = adsk.core.Application.get()
ui = app.userInterface


# Create command
CREATE_CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_create"
CREATE_CMD_NAME = "Join Sheets"
CREATE_CMD_Description = "Sheet Joinery"

# Edit command
EDIT_CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_edit"
EDIT_CMD_NAME = "Edit Join Sheets"
EDIT_CMD_Description = "Edit Sheet Joinery Feature"

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SolidModifyPanel"
COMMAND_BESIDE_ID = "FusionPartingLineSplitCmd"  # Empty string places at end of panel
# Specify that the command will be promoted to the panel.
IS_PROMOTED = False

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


def get_sheet_metal_thickness(body):
    """
    Get sheet metal thickness from the body's parent component sheet metal rule.
    Falls back to geometric calculation if rule access fails.
    Returns thickness in cm (Fusion's internal units).
    """
    try:
        # Try to get thickness from parent component's activeSheetMetalRule
        if hasattr(body, 'parentComponent') and body.parentComponent:
            component = body.parentComponent
            if hasattr(component, 'activeSheetMetalRule') and component.activeSheetMetalRule:
                rule = component.activeSheetMetalRule
                if hasattr(rule, 'thickness') and rule.thickness:
                    return rule.thickness.value
        
        # Fallback: calculate from geometry using bounding box
        bbox = body.boundingBox
        width = bbox.maxPoint.x - bbox.minPoint.x
        height = bbox.maxPoint.y - bbox.minPoint.y
        depth = bbox.maxPoint.z - bbox.minPoint.z
        return min(width, height, depth)
        
    except Exception as e:
        futil.log(f"Error determining sheet metal thickness: {e!s}")
        return None



# Global custom feature definition - created once when add-in loads
custom_feature_definition = None

# Global variable to store the custom feature being edited
_edited_custom_feature = None


# Executed when add-in is run.
def start():
    try:
        futil.log(f"Starting {CREATE_CMD_NAME}...")

        # Perform version compatibility check
        if not perform_startup_version_check():
            futil.log("ERROR: Version check failed, aborting add-in startup")
            return

        # Create the main command definition for creating new features
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CREATE_CMD_ID, CREATE_CMD_NAME, CREATE_CMD_Description, ICON_FOLDER
        )
        futil.log(f"Created create command definition: {CREATE_CMD_ID}")
        futil.add_handler(cmd_def.commandCreated, command_created)

        # Create the edit command definition for editing existing features
        edit_cmd_def = ui.commandDefinitions.addButtonDefinition(
            EDIT_CMD_ID, EDIT_CMD_NAME, EDIT_CMD_Description, ICON_FOLDER
        )
        futil.log(f"Created edit command definition: {EDIT_CMD_ID}")
        futil.add_handler(edit_cmd_def.commandCreated, edit_command_created)

        # Now create the custom feature definition with the edit command ID
        create_custom_feature_definition()

        # ******** Add a button into the UI so the user can run the command. ********
        # Get the target workspace the button will be created in.
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if not workspace:
            futil.log(f"ERROR: Could not find workspace: {WORKSPACE_ID}")
            return
        futil.log(f"Found workspace: {WORKSPACE_ID}")

        # Get the panel the button will be created in.
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if not panel:
            futil.log(f"ERROR: Could not find panel: {PANEL_ID}")
            return
        futil.log(f"Found panel: {PANEL_ID}")

        # Create the button command control in the UI after the specified existing command.
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
        if not control:
            futil.log("ERROR: Failed to add command to panel")
            return
        futil.log("Added command control to panel")

        # Specify if the command is promoted to the main toolbar.
        control.isPromoted = IS_PROMOTED
        futil.log(f"Command setup complete - promoted: {IS_PROMOTED}")

    except Exception as e:
        futil.log(f"ERROR in start(): {e!s}")
        ui.messageBox(f"Failed to start Hello World command: {e!s}")


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
    futil.log(f"{CREATE_CMD_NAME} Command Created Event")

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Add selection input for sheet metal bodies only
    body_selection = inputs.addSelectionInput(
        "target_bodies", 
        "Sheet Metal Bodies", 
        "Select sheet metal bodies to process for joinery (minimum 2 required)"
    )
    # Use SolidBodies filter as base, custom handler will filter to sheet metal only
    body_selection.addSelectionFilter("SolidBodies")
    body_selection.setSelectionLimits(2, 0)  # Require at least 2 bodies, no maximum
    
    # Add tab width parameter
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_tab_width = adsk.core.ValueInput.createByString("10 mm")
    inputs.addValueInput("tab_width", "Tab Width", defaultLengthUnits, default_tab_width)
    
    # Add tolerance parameter  
    default_tolerance = adsk.core.ValueInput.createByString("0.1 mm")
    inputs.addValueInput("tolerance", "Joint Tolerance", defaultLengthUnits, default_tolerance)

    # Connect to the events that are needed by this command.
    futil.add_handler(
        args.command.execute, command_execute, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.inputChanged, command_input_changed, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.executePreview, command_preview, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.validateInputs,
        command_validate_input,
        local_handlers=local_handlers,
    )
    futil.add_handler(
        args.command.destroy, command_destroy, local_handlers=local_handlers
    )
    
    # Add custom selection handler to filter for sheet metal bodies only
    def sheet_metal_selection_handler(args):
        try:
            eventArgs = adsk.core.SelectionEventArgs.cast(args)
            selection = eventArgs.selection
            entity = selection.entity
            
            # Check if it's a BRepBody
            if entity.objectType == adsk.fusion.BRepBody.classType():
                body = adsk.fusion.BRepBody.cast(entity)
                
                # Only allow sheet metal bodies
                if not body.isSheetMetal:
                    eventArgs.isSelectable = False
                    futil.log(f"Rejected non-sheet-metal body: {body.name if hasattr(body, 'name') else 'unnamed'}")
                    return
            else:
                # Reject non-body selections
                eventArgs.isSelectable = False
                futil.log("Rejected non-body selection")
                return
                
        except Exception as e:
            futil.log(f"Error in sheet metal selection handler: {e!s}")
            eventArgs.isSelectable = False

    futil.add_handler(
        args.command.selectionEvent, sheet_metal_selection_handler, local_handlers=local_handlers
    )


# This event handler is called when the user clicks the OK button in the command dialog or
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f"{CREATE_CMD_NAME} Command Execute Event")

    try:
        # Get a reference to your command's inputs.
        inputs = args.command.commandInputs
        body_selection = inputs.itemById("target_bodies")
        tab_width_input = inputs.itemById("tab_width")
        tolerance_input = inputs.itemById("tolerance")

        # Type check the inputs
        if not isinstance(body_selection, adsk.core.SelectionCommandInput):
            raise TypeError("target_bodies is not a SelectionCommandInput")
        if not isinstance(tab_width_input, adsk.core.ValueCommandInput):
            raise TypeError("tab_width is not a ValueCommandInput")
        if not isinstance(tolerance_input, adsk.core.ValueCommandInput):
            raise TypeError("tolerance is not a ValueCommandInput")

        # Get selected bodies
        selected_bodies = []
        for i in range(body_selection.selectionCount):
            selected_bodies.append(body_selection.selection(i).entity)

        # Get parameter values
        tab_width = tab_width_input.value
        tolerance = tolerance_input.value

        # Get the active design
        design = app.activeProduct
        if not design:
            ui.messageBox("No active design found")
            return

        # Create a new feature (this is the "create" command)
        create_join_sheets_feature(design, selected_bodies, tab_width, tolerance)

    except Exception as e:
        futil.log(f"Error in command_execute: {e!s}")
        ui.messageBox(f"Error creating feature: {e!s}")


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f"{CREATE_CMD_NAME} Command Preview Event")
    _ = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    _ = args.inputs

    # General logging for debug.
    futil.log(
        f"{CREATE_CMD_NAME} Input Changed Event fired from a change to {changed_input.id}"
    )


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f"{CREATE_CMD_NAME} Validate Input Event")

    inputs = args.inputs

    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    body_selection = inputs.itemById("target_bodies")
    tab_width_input = inputs.itemById("tab_width")
    tolerance_input = inputs.itemById("tolerance")
    
    # Check that we have at least 2 bodies selected and valid parameters
    valid_selection = (isinstance(body_selection, adsk.core.SelectionCommandInput) and 
                      body_selection.selectionCount >= 2)
    
    # Validate thickness ranges (selection handler ensures only sheet metal bodies)
    thickness_warnings = []
    if valid_selection:
        for i in range(body_selection.selectionCount):
            body = adsk.fusion.BRepBody.cast(body_selection.selection(i).entity)
            if body and body.isSheetMetal:
                thickness = get_sheet_metal_thickness(body)
                if thickness and (thickness < 0.2 or thickness > 2.0):  # 2mm to 20mm in cm
                    thickness_warnings.append(f"Body {i+1}: {thickness*10:.1f}mm thickness outside tested range (2-20mm)")
                
    valid_tab_width = (isinstance(tab_width_input, adsk.core.ValueCommandInput) and 
                      tab_width_input.value > 0)
    valid_tolerance = (isinstance(tolerance_input, adsk.core.ValueCommandInput) and 
                      tolerance_input.value >= 0)
    
    args.areInputsValid = valid_selection and valid_tab_width and valid_tolerance
    
    # Log thickness warnings (but don't invalidate inputs)
    if thickness_warnings:
        for warning in thickness_warnings:
            futil.log(f"THICKNESS WARNING: {warning}")


# This event handler is called when the command terminates.
def command_destroy(_: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f"{CREATE_CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []


# Edit command handlers
def edit_command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f"{EDIT_CMD_NAME} Command Created Event")

    # Get the specific custom feature being edited (per API documentation)
    global _edited_custom_feature
    _edited_custom_feature = None

    try:
        futil.log(f"ActiveSelections count: {ui.activeSelections.count}")

        if ui.activeSelections.count > 0:
            _edited_custom_feature = ui.activeSelections.item(0).entity
            if _edited_custom_feature:
                try:
                    name = _edited_custom_feature.name  # type: ignore
                    futil.log(f"Successfully found custom feature to edit: {name}")

                    try:
                        token = _edited_custom_feature.entityToken  # type: ignore
                        futil.log(f"Custom feature entity token: {token}")
                    except AttributeError:
                        futil.log("Custom feature has no entityToken attribute")

                except AttributeError:
                    futil.log("Custom feature has no name attribute")
            else:
                futil.log("activeSelections.item(0).entity is None")
        else:
            futil.log("No active selections found")

    except Exception as e:
        futil.log(f"Error getting edited custom feature: {e!s}")
        _edited_custom_feature = None

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Create the same inputs as the create command
    # Note: Selection inputs for editing are more complex - for now use value inputs to show stored data
    
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    default_tab_width = adsk.core.ValueInput.createByString("10 mm")
    tab_width_input = inputs.addValueInput("tab_width", "Tab Width", defaultLengthUnits, default_tab_width)
    
    default_tolerance = adsk.core.ValueInput.createByString("0.1 mm")
    tolerance_input = inputs.addValueInput("tolerance", "Joint Tolerance", defaultLengthUnits, default_tolerance)
    
    # Add info display for selected entities (read-only for now)
    body_info = inputs.addTextBoxCommandInput("body_info", "Selected Bodies", "Loading...", 2, True)

    # Populate with current values from the feature being edited
    if _edited_custom_feature:
        body_count, tab_width, tolerance = get_feature_parameters(_edited_custom_feature)
        tab_width_input.expression = str(tab_width)
        tolerance_input.expression = str(tolerance)
        body_info.text = f"Bodies: {body_count} selected"
        futil.log(
            f'Populated edit dialog with: bodies={body_count}, tab_width={tab_width}, tolerance={tolerance}'
        )

    # Connect to the edit-specific event handlers
    futil.add_handler(
        args.command.execute, edit_command_execute, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.inputChanged,
        edit_command_input_changed,
        local_handlers=local_handlers,
    )
    futil.add_handler(
        args.command.executePreview, edit_command_preview, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.validateInputs,
        edit_command_validate_input,
        local_handlers=local_handlers,
    )
    futil.add_handler(
        args.command.destroy, edit_command_destroy, local_handlers=local_handlers
    )


def edit_command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f"{EDIT_CMD_NAME} Command Execute Event")

    try:
        # Get a reference to your command's inputs.
        inputs = args.command.commandInputs
        tab_width_input = inputs.itemById("tab_width")
        tolerance_input = inputs.itemById("tolerance")

        # Type check the inputs
        if not isinstance(tab_width_input, adsk.core.ValueCommandInput):
            raise TypeError("tab_width is not a ValueCommandInput")
        if not isinstance(tolerance_input, adsk.core.ValueCommandInput):
            raise TypeError("tolerance is not a ValueCommandInput")

        # Get input values
        tab_width = tab_width_input.value
        tolerance = tolerance_input.value

        # Get the active design
        design = app.activeProduct
        if not design:
            ui.messageBox("No active design found")
            return

        # Use the global edited feature
        global _edited_custom_feature
        if _edited_custom_feature:
            try:
                token = _edited_custom_feature.entityToken  # type: ignore
                # Update the existing feature using the global reference
                update_join_sheets_feature(design, token, tab_width, tolerance)

                try:
                    name = _edited_custom_feature.name  # type: ignore
                    futil.log(f"Successfully updated feature: {name}")
                except AttributeError:
                    futil.log("Successfully updated feature (name unavailable)")

            except AttributeError:
                futil.log("_edited_custom_feature has no entityToken attribute")
        else:
            futil.log("_edited_custom_feature is None in execute handler")

    except Exception as e:
        futil.log(f"Error in edit_command_execute: {e!s}")
        ui.messageBox(f"Error updating feature: {e!s}")


def edit_command_preview(_: adsk.core.CommandEventArgs):
    futil.log(f"{EDIT_CMD_NAME} Command Preview Event")


def edit_command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    futil.log(
        f"{EDIT_CMD_NAME} Input Changed Event fired from a change to {changed_input.id}"
    )


def edit_command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f"{EDIT_CMD_NAME} Validate Input Event")
    inputs = args.inputs
    tab_width_input = inputs.itemById("tab_width")
    tolerance_input = inputs.itemById("tolerance")
    
    # Check that parameters are valid
    valid_tab_width = (isinstance(tab_width_input, adsk.core.ValueCommandInput) and 
                      tab_width_input.value > 0)
    valid_tolerance = (isinstance(tolerance_input, adsk.core.ValueCommandInput) and 
                      tolerance_input.value >= 0)
    
    args.areInputsValid = valid_tab_width and valid_tolerance


def edit_command_destroy(_: adsk.core.CommandEventArgs):
    futil.log(f"{EDIT_CMD_NAME} Command Destroy Event")


def create_custom_feature_definition():
    """Create the CustomFeatureDefinition when add-in loads (best practice)"""
    global custom_feature_definition
    try:
        # Use company name in ID as recommended
        feature_id = f"{config.COMPANY_NAME}.JoinSheets"
        default_name = "Join Sheets"
        icon_folder = ICON_FOLDER

        custom_feature_definition = adsk.fusion.CustomFeatureDefinition.create(
            feature_id, default_name, icon_folder
        )

        # Set the edit command ID to enable "Edit Feature" functionality
        custom_feature_definition.editCommandId = EDIT_CMD_ID

        # Add the compute handler to the definition
        futil.add_handler(
            custom_feature_definition.customFeatureCompute,
            compute_join_sheets_feature,
            local_handlers=local_handlers,
        )

        futil.log(f"Created CustomFeatureDefinition: {feature_id}")

    except Exception as e:
        futil.log(f"Error creating CustomFeatureDefinition: {e!s}")
        raise


def create_join_sheets_feature(design, selected_bodies, tab_width, tolerance):
    """Create a Join Sheets custom feature instance in the timeline"""
    try:
        if not custom_feature_definition:
            raise Exception("CustomFeatureDefinition not initialized")

        # Get the root component
        root_comp = design.rootComponent
        custom_features = root_comp.features.customFeatures

        # Create the custom feature input using the pre-created definition
        custom_feature_input = custom_features.createInput(custom_feature_definition)
        
        # Add dependencies on the selected bodies
        for i, body in enumerate(selected_bodies):
            custom_feature_input.addDependency(f"body_{i}", body)
        
        custom_feature = custom_features.add(custom_feature_input)

        # Store the parameters in the feature for later retrieval
        store_feature_parameters(custom_feature, selected_bodies, tab_width, tolerance)

        futil.log(
            f"Successfully created Join Sheets custom feature: {custom_feature.name}"
        )
        return custom_feature

    except Exception as e:
        futil.log(f"Error creating Join Sheets feature: {e!s}")
        raise


def update_join_sheets_feature(design, feature_token, tab_width, tolerance):
    """Update an existing Join Sheets custom feature (parameters only)"""
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
            futil.log(f"Could not find existing feature with token: {feature_token}")
            ui.messageBox("Could not find feature to update")
            return None

        # Get current parameters to preserve body selections
        body_count, current_tab_width, current_tolerance = get_feature_parameters(existing_feature)
        
        # Update only the tab width and tolerance parameters
        attrs = existing_feature.attributes
        group_name = config.ADDIN_ID
        
        # Update the attributes
        tab_width_attr = attrs.itemByName(group_name, "tab_width")
        tolerance_attr = attrs.itemByName(group_name, "tolerance")
        
        if tab_width_attr:
            tab_width_attr.value = str(tab_width)
        else:
            attrs.add(group_name, "tab_width", str(tab_width))
            
        if tolerance_attr:
            tolerance_attr.value = str(tolerance)
        else:
            attrs.add(group_name, "tolerance", str(tolerance))

        # The feature will automatically recompute when parameters change
        # No need to rollTo which moves the timeline marker

        futil.log(
            f"Successfully updated Join Sheets custom feature: {existing_feature.name}"
        )
        return existing_feature

    except Exception as e:
        futil.log(f"Error updating Join Sheets feature: {e!s}")
        raise


def store_feature_parameters(custom_feature, selected_bodies, tab_width, tolerance):
    """Store parameters in the custom feature for later retrieval"""
    try:
        # Use attributes to store our parameters
        attrs = custom_feature.attributes
        group_name = config.ADDIN_ID

        # Store the parameters as attributes
        attrs.add(group_name, "body_count", str(len(selected_bodies)))
        attrs.add(group_name, "tab_width", str(tab_width))
        attrs.add(group_name, "tolerance", str(tolerance))
        
        # Store entity tokens for bodies (for edit functionality)
        for i, body in enumerate(selected_bodies):
            attrs.add(group_name, f"body_{i}_token", body.entityToken)

        futil.log(
            f'Stored parameters in feature: bodies={len(selected_bodies)}, tab_width={tab_width}, tolerance={tolerance}'
        )

    except Exception as e:
        futil.log(f"Error storing feature parameters: {e!s}")


def get_feature_parameters(custom_feature):
    """Retrieve stored parameters from a custom feature"""
    try:
        attrs = custom_feature.attributes
        group_name = config.ADDIN_ID

        # Get parameter counts
        body_count_attr = attrs.itemByName(group_name, "body_count")
        tab_width_attr = attrs.itemByName(group_name, "tab_width") 
        tolerance_attr = attrs.itemByName(group_name, "tolerance")

        body_count = int(body_count_attr.value) if body_count_attr else 0
        tab_width = float(tab_width_attr.value) if tab_width_attr else 10.0
        tolerance = float(tolerance_attr.value) if tolerance_attr else 0.1

        # Note: For edit functionality, we would need to find entities by token
        # This is a simplified version for now
        
        return body_count, tab_width, tolerance

    except Exception as e:
        futil.log(f"Error retrieving feature parameters: {e!s}")
        return 0, 10.0, 0.1


def compute_join_sheets_feature(args):
    """Compute handler for the Join Sheets custom feature"""
    try:
        custom_feature = args.customFeature
        futil.log(f"Computing Join Sheets feature: {custom_feature.name}")

        # Get stored parameters
        body_count, tab_width, tolerance = get_feature_parameters(custom_feature)
        futil.log(f"Feature parameters: bodies={body_count}, tab_width={tab_width}, tolerance={tolerance}")

        # Get dependencies (the selected bodies)
        dependencies = custom_feature.dependencies
        futil.log(f"Feature has {dependencies.count} dependencies")

        if dependencies.count < 2:
            futil.log("WARNING: Feature needs at least 2 body dependencies")
            args.isComputed = True  # Don't fail, just warn
            return

        # Collect the dependent bodies by parameter name
        bodies = []
        
        for i in range(dependencies.count):
            dependency = dependencies.item(i)
            param_name = dependency.parameter
            entity = dependency.entity
            
            futil.log(f"Processing dependency: {param_name}")
            
            if param_name.startswith("body_"):
                bodies.append(entity)

        futil.log(f"Found {len(bodies)} bodies in dependencies")

        if len(bodies) >= 2:
            # Generate slot-and-tab joints between the first two bodies
            success = generate_single_intersection_joint(bodies[0], bodies[1], tab_width, tolerance)
            args.isComputed = success
        else:
            futil.log("ERROR: Need at least 2 bodies to generate joints")
            args.isComputed = False

    except Exception as e:
        futil.log(f"Error computing Join Sheets feature: {e!s}")
        args.isComputed = False


def generate_single_intersection_joint(body1, body2, tab_width, tolerance):
    """Generate slot-and-tab joint between two sheet bodies"""
    try:
        futil.log(f"Generating joint between body1 and body2 with tab_width={tab_width}, tolerance={tolerance}")
        
        # Selection handler guarantees these are sheet metal bodies
        for i, body in enumerate([body1, body2], 1):
            if not body:
                futil.log(f"ERROR: Body {i} is invalid")
                return False
                
            # Cast to BRepBody and verify it's still a sheet metal body
            sheet_body = adsk.fusion.BRepBody.cast(body)
            if not (sheet_body and sheet_body.isSheetMetal):
                futil.log(f"ERROR: Body {i} lost sheet metal classification during processing")
                return False
                
            # Get thickness from sheet metal rule or geometry
            thickness = get_sheet_metal_thickness(sheet_body)
            if not thickness:
                futil.log(f"ERROR: Could not determine thickness for Body {i}")
                return False
            
            # Warn if outside tested range but continue processing
            if thickness < 0.2 or thickness > 2.0:  # 2mm to 20mm in cm
                futil.log(f"WARNING: Body {i} thickness {thickness*10:.1f}mm outside tested range (2-20mm)")
        
        # TODO: Implement actual intersection detection and joint generation
        # This is where the core sheet joinery algorithms would go:
        # - BRep intersection analysis using sheet metal face hierarchy
        # - Leverage sheetMetalProperties.thickness for accurate joint sizing
        # - Tab and slot profile generation with material-aware tolerances
        # - Consider bend radius from sheet metal properties
        
        futil.log("Joint generation placeholder completed successfully")
        return True
        
    except Exception as e:
        futil.log(f"Error in generate_single_intersection_joint: {e!s}")
        return False
