import adsk.core
import adsk.fusion
from ..unlinkedCopy.operation import run_operation as unlinkedCopy

def run_make_component(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    # Get command inputs
    inputs = args.command.commandInputs
    select_input = inputs.itemById('target_components')
    name_input = inputs.itemById('new_component_name')

    if not select_input or select_input.selectionCount == 0:
        ui.messageBox('No components selected to copy.')
        return

    selected_occs = [adsk.fusion.Occurrence.cast(select_input.selection(i).entity) for i in range(select_input.selectionCount)]

    # Create the new parent component
    new_occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    new_comp = new_occurrence.component
    new_comp.name = name_input.text.strip()

    # Use Unlinked Copy to duplicate the selected components
    copied_occs = unlinkedCopy(args, selected_occs)

    # Move the copied components into the new component
    for occ in copied_occs:
        transform = occ.transform
        moved = new_comp.occurrences.addExistingComponent(occ.component, transform)
        occ.deleteMe()

    ui.messageBox(f'✅ New grouped component created: {new_comp.name}')
