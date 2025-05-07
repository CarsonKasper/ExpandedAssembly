import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from . import operation

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = 'connect'
CMD_NAME = 'Connect'
CMD_DESCRIPTION = 'Align two components and lock them with a rigid group'
IS_PROMOTED = True

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'ExpandedAssemblyPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(__file__), 'resources', '')

local_handlers = []

def start():
    try:
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()

        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_DESCRIPTION, ICON_FOLDER
        )

        futil.add_handler(cmd_def.commandCreated, command_created)

        panel = ui.allToolbarPanels.itemById(PANEL_ID)
        if panel and not panel.controls.itemById(CMD_ID):
            control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
            control.isPromoted = IS_PROMOTED

    except:
        futil.handle_error('start')

def stop():
    try:
        panel = ui.allToolbarPanels.itemById(PANEL_ID)
        if panel:
            control = panel.controls.itemById(CMD_ID)
            if control:
                control.deleteMe()

        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()

    except:
        futil.handle_error('stop')

def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{CMD_NAME} Command Created')
    command = args.command
    inputs = command.commandInputs

    from_input = inputs.addSelectionInput('from_selection', 'From', 'Select the FROM point')
    from_input.addSelectionFilter('Vertices')
    from_input.addSelectionFilter('SketchPoints')
    from_input.addSelectionFilter('ConstructionPoints')
    from_input.addSelectionFilter('CircularEdges')
    from_input.setSelectionLimits(1, 1)

    to_input = inputs.addSelectionInput('to_selection', 'To', 'Select the TO point')
    to_input.addSelectionFilter('Vertices')
    to_input.addSelectionFilter('SketchPoints')
    to_input.addSelectionFilter('ConstructionPoints')
    to_input.addSelectionFilter('CircularEdges')
    to_input.setSelectionLimits(1, 1)

    inputs.addBoolValueInput('flip_direction', 'Flip', False, '', False)
    inputs.addBoolValueInput('rotate_90', 'Rotate 90°', False, '', False)
    inputs.addBoolValueInput('capture_position', 'Capture Position', True, '', True)

    # Preselect logic
    selections = ui.activeSelections
    if selections.count == 2:
        entity1 = selections.item(0).entity
        entity2 = selections.item(1).entity
        comp1 = get_owning_component(entity1)
        comp2 = get_owning_component(entity2)

        if comp1 != comp2:
            from_input.addSelection(entity1)
            to_input.addSelection(entity2)
        else:
            ui.messageBox('Cannot select two points from the same component.')

    futil.add_handler(command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(command.destroy, command_destroy, local_handlers=local_handlers)
    futil.add_handler(command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(command.validateInputs, command_validate_inputs, local_handlers=local_handlers)

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    try:
        changed = args.input
        inputs = args.inputs

        from_input = inputs.itemById('from_selection')
        to_input = inputs.itemById('to_selection')

        if changed.id == 'to_selection' and to_input.selectionCount == 1:
            from_entity = from_input.selection(0).entity
            to_entity = to_input.selection(0).entity

            if get_owning_component(from_entity) == get_owning_component(to_entity):
                ui.messageBox('Selections must be from different components.')
                to_input.clearSelection()
    except:
        futil.handle_error('command_input_changed')

    def command_validate_inputs(args: adsk.core.ValidateInputsEventArgs):
        inputs = args.inputs
        from_input = inputs.itemById('from_selection')
        to_input = inputs.itemById('to_selection')

        if from_input.selectionCount == 0:
            args.areInputsValid = False
            ui.messageBox('Please select the FROM point.')
        elif to_input.selectionCount == 0:
            args.areInputsValid = False
            ui.messageBox('Please select the TO point.')
        else:
            args.areInputsValid = True

def get_owning_component(entity):
    try:
        return entity.assemblyContext or entity.parentComponent
    except:
        return None

def command_execute(args: adsk.core.CommandEventArgs):
    operation.run_operation(args)

def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroyed')
    global local_handlers
    local_handlers = []
