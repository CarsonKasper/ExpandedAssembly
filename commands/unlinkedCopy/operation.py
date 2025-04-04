import adsk.core

def run_operation():
    inputs = args.command.commandInputs
    selected_input = inputs.itemById('target_component')
    selected_occurrence = selected_input.selection(0)
    
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox("You clicked the Unlinked Copy button!")