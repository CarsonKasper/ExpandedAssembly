import adsk.core
import adsk.fusion
import os
import tempfile

def sanitize_filename(name: str) -> str:
    """Sanitize the component name to remove invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    return ''.join(c for c in name if c not in invalid_chars)

def run_operation(args, occurrences):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    export_mgr = design.exportManager
    import_mgr = app.importManager
    temp_dir = tempfile.gettempdir()

    for occ in occurrences:
        try:
            # Generate a safe filename
            safe_name = sanitize_filename(occ.component.name + " UC")
            temp_path = os.path.join(temp_dir, f'{safe_name}_temp.f3d')

            # Export the component to an .f3d file
            export_options = export_mgr.createFusionArchiveExportOptions(temp_path, occ.component)
            export_options.isComponentNative = True

            if not export_mgr.execute(export_options):
                ui.messageBox(f'❌ Failed to export component: {occ.component.name}')
                continue

            if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 1000:
                ui.messageBox(f"⚠ Exported file is missing or invalid for {occ.component.name}: {temp_path}")
                continue

            before_count = root_comp.occurrences.count

            # Import the component back into the root
            import_options = import_mgr.createFusionArchiveImportOptions(temp_path)
            result = import_mgr.importToTarget(import_options, root_comp)

            if not result:
                ui.messageBox(f"❌ Import returned False for {occ.component.name}")
                continue

            # Get the new occurrence
            after_count = root_comp.occurrences.count
            if after_count <= before_count:
                ui.messageBox(f'⚠ Import succeeded but no new component found for {occ.component.name}')
                continue

            new_occ = root_comp.occurrences.item(after_count - 1)

            if new_occ.isReferencedComponent:
                new_occ.breakLink()

            new_occ.component.name = safe_name

            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            ui.messageBox(f"❌ Error during processing {occ.component.name}:\n{e}")
