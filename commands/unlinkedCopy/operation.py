import adsk.core
import adsk.fusion
import os
import tempfile

def sanitize_filename(name: str) -> str:
    # Remove characters that are not allowed in filenames
    invalid_chars = '<>:"/\\|?*'
    return ''.join(c for c in name if c not in invalid_chars)

def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    inputs = args.command.commandInputs
    selected_input = inputs.itemById('target_component')
    name_input = inputs.itemById('copy_name')

    if not selected_input or selected_input.selectionCount == 0:
        ui.messageBox('No component selected.')
        return

    selected_entity = selected_input.selection(0).entity
    occ = adsk.fusion.Occurrence.cast(selected_entity)
    if not occ:
        ui.messageBox('Selected entity is not an occurrence.')
        return

    # Create safe name
    custom_name = name_input.text.strip()
    if not custom_name:
        custom_name = f"{occ.name} UC"

    component = occ.component

    # Export the component
    export_mgr = design.exportManager
    temp_dir = tempfile.gettempdir()
    safe_name = sanitize_filename(custom_name)
    temp_path = os.path.join(temp_dir, f'{safe_name}_temp.f3d')

    options = export_mgr.createFusionArchiveExportOptions(temp_path, component)
    if not export_mgr.execute(options):
        ui.messageBox('Failed to export component.')
        return

    # Count how many components before import
    before_count = root_comp.occurrences.count

    # Import the file
    import_mgr = app.importManager
    import_options = import_mgr.createFusionArchiveImportOptions(temp_path)
    if not import_mgr.importToTarget(import_options, root_comp):
        ui.messageBox('Failed to import unlinked component.')
        return

    # Identify the newly added occurrence
    after_count = root_comp.occurrences.count
    if after_count <= before_count:
        ui.messageBox('Import succeeded but no new occurrence found.')
        return

    new_occ = root_comp.occurrences.item(after_count - 1)
    new_occ.component.name = custom_name

    # Cleanup temp file
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        ui.messageBox(f"Warning: Could not delete temp file: {str(e)}")

    ui.messageBox(f'✅ Unlinked copy created: {new_occ.name}')
