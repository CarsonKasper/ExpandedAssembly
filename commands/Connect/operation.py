import adsk.core
import adsk.fusion

def run_operation(args, points):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    try:
        sel1, sel2 = points
        occ1 = sel1.assemblyContext
        occ2 = sel2.assemblyContext

        if not occ1 or not occ2:
            ui.messageBox('❌ Selected points must be in component occurrences.')
            return

        # Trigger the Align command interactively
        ui.commandDefinitions.itemById('AlignCommand').execute()

        # Wait for Align to finish
        app.executeTextCommand('Commands.WaitForCommandDone AlignCommand')

        # Automatically create a Rigid Group
        rigid_input = root.occurrences.createRigidGroupInput([occ1, occ2])
        root.occurrences.createRigidGroup(rigid_input)

    except Exception as e:
        ui.messageBox(f'❌ Error during Align and Rigid Group:\n{e}')
