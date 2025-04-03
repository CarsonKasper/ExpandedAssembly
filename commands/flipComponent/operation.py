import adsk.core

def run_operation():
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox("You clicked the Flip Component button!")