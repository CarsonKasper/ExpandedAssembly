import adsk.core

def run_operation():
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox("You clicked the Unlinked Copy button!")
    
def on_command_created(command: adsk.core.Command, inputs: adsk.core.CommandInputs):
    select_input = inputs.addSelectionInput('target_component', 'Select Component', 'Choose the component to copy')
    select_input.addSelectionFilter('Occurrences')
    select_input.setSelectionLimits(1, 1)