import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from . import operation

app = adsk.core.Application.get()
ui = app.userInterface

# Unique command ID and metadata
CMD_ID = 'unlinkedCopy'
CMD_NAME = 'Unlinked Copy'
CMD_DESCRIPTION = 'Creates unlinked copies of the selected components'
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

    # Selection input (allow multiple components to be selected)
    select_input = inputs.addSelectionInput(
        'target_components',
        'Select Components',
        'Choose the components to copy'
    )
    select_input.addSelectionFilter('Occurrences')
    select_input.setSelectionLimits(1, 0)  # Allow multiple selections

    futil.add_handler(command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(command.destroy, command_destroy, local_handlers=local_handlers)

def command_execute(args: adsk.core.CommandEventArgs):
    # Get the selected occurrences from the command inputs
    command = args.command
    inputs = command.commandInputs
    select_input = inputs.itemById('target_components')
    
    if not select_input or select_input.selectionCount == 0:
        ui.messageBox('No components selected to copy.')
        return

    # Extract occurrences
    occurrences = [adsk.fusion.Occurrence.cast(select_input.selection(i).entity) for i in range(select_input.selectionCount)]
    
    # Now call the operation with both arguments
    operation.run_operation(args, occurrences)

def command_destroy(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Destroyed')
    global local_handlers
    local_handlers = []
