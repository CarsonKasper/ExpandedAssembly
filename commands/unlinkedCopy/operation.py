import adsk.core
import adsk.fusion
import os
import tempfile

def sanitize_filename(name: str) -> str:
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
    export_mgr = design.exportManager
    import_mgr = app.importManager
    temp_dir = tempfile.gettempdir()
    safe_name = sanitize_filename(custom_name)
    temp_path = os.path.join(temp_dir, f'{safe_name}_temp.f3d')

    # ✅ Export as .f3d
    export_options = export_mgr.createFusionArchiveExportOptions(temp_path, component)
    export_options.isComponentNative = True

    if not export_mgr.execute(export_options):
        ui.messageBox('❌ Failed to export component.')
        return

    # ✅ Confirm file is valid
    if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 1000:
        ui.messageBox(f"⚠ Exported file is missing or invalid:\n{temp_path}")
        return

    before_count = root_comp.occurrences.count

    # ✅ Try importing the file
    import_options = import_mgr.createFusionArchiveImportOptions(temp_path)

    try:
        result = import_mgr.importToTarget(import_options, root_comp)
        if not result:
            raise RuntimeError("Import returned False.")
    except Exception as e:
        ui.messageBox(f"❌ Import failed:\n{e}\n\nFile path:\n{temp_path}")
        return

    # ✅ Locate the new occurrence
    after_count = root_comp.occurrences.count
    if after_count <= before_count:
        ui.messageBox('⚠ Import succeeded but no new component found.')
        return

    new_occ = root_comp.occurrences.item(after_count - 1)
    
    if new_occ.isReferencedComponent:
        new_occ.breakLink()

    new_occ.component.name = custom_name

    # ✅ Cleanup
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        ui.messageBox(f"⚠ Warning: Could not delete temp file:\n{str(e)}")

    ui.messageBox(f'✅ Unlinked copy created: {new_occ.name}')
