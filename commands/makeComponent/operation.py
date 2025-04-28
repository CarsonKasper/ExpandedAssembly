import adsk.core
import adsk.fusion
import os
import tempfile

def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    inputs = args.command.commandInputs
    select_input = inputs.itemById('target_components')
    name_input = inputs.itemById('new_assembly_name')

    if not select_input or select_input.selectionCount == 0:
        ui.messageBox('No components selected.')
        return

    if not name_input or not name_input.text.strip():
        ui.messageBox('No name provided for new assembly.')
        return

    new_name = name_input.text.strip()

    # Create a new empty component in the root
    all_occurrences = root_comp.occurrences
    transform = adsk.core.Matrix3D.create()
    new_occurrence = all_occurrences.addNewComponent(transform)
    new_comp = new_occurrence.component
    new_comp.name = new_name

    # Move selected occurrences into the new component
    for i in range(select_input.selectionCount):
        selected_entity = select_input.selection(i).entity
        occ = adsk.fusion.Occurrence.cast(selected_entity)

        if occ:
            try:
                occ.moveToComponent(new_comp)
            except Exception as e:
                ui.messageBox(f"⚠ Failed to move occurrence: {occ.name}\n{str(e)}")

    ui.messageBox(f'✅ Created new assembly: {new_name}')
