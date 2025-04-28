import adsk.core
import adsk.fusion

def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    inputs = args.command.commandInputs
    selected_input = inputs.itemById('target_components')
    name_input = inputs.itemById('new_component_name')

    if not selected_input or selected_input.selectionCount == 0:
        ui.messageBox('No components selected.')
        return

    if not name_input or not name_input.text.strip():
        ui.messageBox('No name provided for new component.')
        return

    new_name = name_input.text.strip()

    # Create an empty new component
    new_occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    new_occurrence.component.name = new_name

    # Move selected components into the new component
    for i in range(selected_input.selectionCount):
        occ = adsk.fusion.Occurrence.cast(selected_input.selection(i).entity)
        if occ:
            occ.transform = adsk.core.Matrix3D.create()  # Reset transform so it can move cleanly
            occ.reparent(new_occurrence)

    ui.messageBox(f'✅ Created new component "{new_name}" and moved {selected_input.selectionCount} items into it.')
