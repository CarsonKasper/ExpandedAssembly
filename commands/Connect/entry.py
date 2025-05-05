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
CMD_DESCRIPTION = 'Aligns two points and automatically creates a rigid group.'
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

    except Exception as e:
        futil.handle_error(f'start: {str(e)}')

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

    except Exception as e:
        futil.handle_error(f'stop: {str(e)}')

def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{CMD_NAME} Command Created')
    command = args.command
    inputs = command.commandInputs

    select_input = inputs.addSelectionInput(
        'target_points',
        'Select Two Points',
        'Select exactly two points to align and group'
    )
    select_input.addSelectionFilter('Vertices')
    select_input.setSelectionLimits(2, 2)

    futil.add_handler(command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(command.destroy, command_destroy, local_handlers=local_handlers)

def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    point_input = inputs.itemById('target_points')

    if point_input.selectionCount != 2:
        ui.messageBox('Please select exactly two points.')
        return

    points = [point_input.selection(i).entity for i in range(2)]
    operation.run_operation(args, points)

def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroyed')
    global local_handlers
    local_handlers = []
