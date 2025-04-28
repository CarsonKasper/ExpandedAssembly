# Here you define the commands that will be added to your add-in.

# TODO Import the modules corresponding to the commands you created.
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry".
import adsk.core
from .mirrorComponent import entry as mirror_Component
from .unlinkedCopy import entry as unlinked_copy
from .flipComponent import entry as flip_component
from .makeComponent import entry as make_Component

# TODO add your imported modules to this list.
# Fusion will automatically call the start() and stop() functions.

commands = [
    mirror_Component,
    unlinked_copy,
    flip_component,
    make_Component
]

def create_shared_panel():
    ui = adsk.core.Application.get().userInterface
    workspace = ui.workspaces.itemById('FusionSolidEnvironment')
    panels = workspace.toolbarPanels
    panel_id = 'ExpandedAssemblyPanel'

    if not panels.itemById(panel_id):
        panels.add(panel_id, 'Expanded Assembly', 'ToolsTab', False)

# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    create_shared_panel()
    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()