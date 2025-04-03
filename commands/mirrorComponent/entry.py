import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from . import operation

app = adsk.core.Application.get()
ui = app.userInterface

# Unique command ID and metadata
CMD_ID = 'mirrorComponent'
CMD_NAME = 'Mirror Component'
CMD_DESCRIPTION = 'Mirrors the selected component'
IS_PROMOTED = True

# Panel was created in commands/__init__.py
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'ExpandedAssemblyPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(__file__), 'resources', '')

# Local list to prevent garbage collection
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

    futil.add_handler(command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(command.destroy, command_destroy, local_handlers=local_handlers)

def command_execute(args: adsk.core.CommandEventArgs):
    operation.run_operation()

def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroyed')
    global local_handlers
    local_handlers = []
