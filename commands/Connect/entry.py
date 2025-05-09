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

    selection_input = inputs.addSelectionInput(
        'selection_input', 'Selections', 'Select two points from different bodies'
    )
    selection_input.addSelectionFilter('Vertices')
    selection_input.addSelectionFilter('SketchPoints')
    selection_input.addSelectionFilter('ConstructionPoints')
    selection_input.addSelectionFilter('CircularEdges')
    selection_input.setSelectionLimits(0, 2)

    inputs.addBoolValueInput('flip_direction', 'Flip', False, '', False)
    inputs.addBoolValueInput('rotate_90', 'Rotate 90°', False, '', False)
    inputs.addBoolValueInput('capture_position', 'Capture Position', True, '', True)

    futil.add_handler(command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(command.destroy, command_destroy, local_handlers=local_handlers)
    futil.add_handler(command.inputChanged, command_input_changed, local_handlers=local_handlers)

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    try:
        inputs = args.inputs
        selection_input = inputs.itemById('selection_input')

        if not selection_input:
            return

        if selection_input.selectionCount == 2:
            entity1 = selection_input.selection(0).entity
            entity2 = selection_input.selection(1).entity

            body1 = get_owning_body(entity1)
            body2 = get_owning_body(entity2)

            if body1 and body2 and body1 == body2:
                ui.messageBox('Selections must be on different bodies.')
                selection_input.clearSelection()
                selection_input.addSelection(entity1)

    except:
        futil.handle_error('command_input_changed')

def get_owning_body(entity):
    try:
        return entity.body
    except:
        return None

def command_execute(args: adsk.core.CommandEventArgs):
    operation.run_operation(args)

def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroyed')
    global local_handlers
    local_handlers = []
