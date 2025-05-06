import adsk.core
import adsk.fusion
import traceback

def run_operation(args):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        inputs = args.command.commandInputs
        selA = inputs.itemById('compA')
        selB = inputs.itemById('compB')

        if not selA or not selB or selA.selectionCount == 0 or selB.selectionCount == 0:
            ui.messageBox('Please select two components to connect.')
            return

        occA = adsk.fusion.Occurrence.cast(selA.selection(0).entity)
        occB = adsk.fusion.Occurrence.cast(selB.selection(0).entity)

        if not occA or not occB:
            ui.messageBox('Selections must be component occurrences.')
            return

        root = design.rootComponent

        rigid_groups = root.assemblyContext.rigidGroups if root.assemblyContext else root.rigidGroups

        new_group = rigid_groups.add(adsk.core.ObjectCollection.create())
        new_group.occurrences.add(occA)
        new_group.occurrences.add(occB)

        ui.messageBox('✅ Rigid group created between selected components.')

    except:
        if ui:
            ui.messageBox('Failed:{}'.format(traceback.format_exc()))
