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
    selected_input = inputs.itemById('target_component')

    if not selected_input or selected_input.selectionCount == 0:
        ui.messageBox('No component selected.')
        return

    selected_entity = selected_input.selection(0).entity
    occ = adsk.fusion.Occurrence.cast(selected_entity)

    if not occ:
        ui.messageBox('Selected entity is not an occurrence.')
        return

    component = occ.component

    # Export the component to a temporary .f3d file
    export_mgr = design.exportManager
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f'{component.name}_temp.f3d')

    options = export_mgr.createFusionArchiveExportOptions(temp_path, component)
    success = export_mgr.execute(options)

    if not success:
        ui.messageBox('Failed to export component.')
        return

    # Import the .f3d file back in to create a fully unlinked copy
    import_mgr = app.importManager
    import_options = import_mgr.createFusionArchiveImportOptions(temp_path)
    new_occ = import_mgr.importToTarget(import_options, root_comp)

    if not new_occ:
        ui.messageBox('Failed to import unlinked component.')
        return

    # Clean up the temp file
    try:
        os.remove(temp_path)
    except Exception as e:
        ui.messageBox(f"Warning: Could not delete temp file: {str(e)}")

    ui.messageBox(f'✅ Unlinked copy created successfully')
