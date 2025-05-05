import adsk.core
import adsk.fusion
import traceback
import os
from . import operation

CMD_ID = 'connect'
CMD_NAME = 'Connect'
CMD_Descr = 'Align two components and then group them rigidly.'

handlers = []

def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create command definition
        cmd_definitions = ui.commandDefinitions
        cmd_def = cmd_definitions.itemById(CMD_ID)
        if not cmd_def:
            cmd_def = cmd_definitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Descr)

        # Create event handler
        on_command_created = ConnectCommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)

        # Execute command
        cmd_def.execute()

    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(f'Connect Error: {traceback.format_exc()}')

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
    except:
        pass

class ConnectCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False

            # Set up execute event handler
            on_execute = ConnectCommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)
        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox(f'Command Setup Error: {traceback.format_exc()}')

class ConnectCommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            operation.run_operation()
        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox(f'Execute Error: {traceback.format_exc()}')
