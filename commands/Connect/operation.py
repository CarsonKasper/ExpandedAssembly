import adsk.core
import adsk.fusion
import traceback

def run_operation():
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent

        # Run the Align command manually
        ui.commandDefinitions.itemById('FusionAlignCommand').execute()
        ui.messageBox('After completing Align, click OK to create a Rigid Group.')

        # Grab all top-level occurrences
        occurrences = root.occurrences
        if occurrences.count < 2:
            ui.messageBox('Not enough components to group.')
            return

        # Assume last two components were involved
        occ1 = occurrences.item(occurrences.count - 1)
        occ2 = occurrences.item(occurrences.count - 2)

        # Make sure they aren't the same
        if occ1 == occ2:
            ui.messageBox('Selected components appear to be the same.')
            return

        # Create rigid group
        group_entities = adsk.core.ObjectCollection.create()
        group_entities.add(occ1)
        group_entities.add(occ2)

        root.occurrences.createRigidGroup(group_entities)

        ui.messageBox(f'✅ Rigid group created between:\n- {occ1.name}\n- {occ2.name}')
    except Exception as e:
        ui.messageBox(f'Error in Connect operation:\n{traceback.format_exc()}')
