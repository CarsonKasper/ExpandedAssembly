import adsk.core
import adsk.fusion
import os
import tempfile

def sanitize_filename(name: str) -> str:
    """Sanitize the component name to remove invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    return ''.join(c for c in name if c not in invalid_chars)

def capture_joints(occurrences):
    joint_mapping = {}

    for occ in occurrences:
        # Iterate through all joints in the occurrence
        for joint in occ.joints:
            # Use the joint's name as the key
            joint_mapping[joint.name] = occ

    return joint_mapping

def run_operation(args, occurrences):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    export_mgr = design.exportManager
    import_mgr = app.importManager
    temp_dir = tempfile.gettempdir()

    # Get joints before proceeding
    joint_mapping = capture_joints(occurrences)

    # Loop through each occurrence and process them
    for occ in occurrences:
        # Create a safe filename for each component copy
        safe_name = sanitize_filename(occ.component.name + " UC")
        temp_path = os.path.join(temp_dir, f'{safe_name}_temp.f3d')

        # Export as .f3d
        export_options = export_mgr.createFusionArchiveExportOptions(temp_path, occ.component)
        export_options.isComponentNative = True

        if not export_mgr.execute(export_options):
            ui.messageBox(f'❌ Failed to export component: {occ.component.name}')
            continue

        # Check if the file exists and is valid
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 1000:
            ui.messageBox(f"⚠ Exported file is missing or invalid for {occ.component.name}: {temp_path}")
            continue

        before_count = root_comp.occurrences.count

        # Try importing the exported component file
        import_options = import_mgr.createFusionArchiveImportOptions(temp_path)

        try:
            result = import_mgr.importToTarget(import_options, root_comp)
            if not result:
                raise RuntimeError("Import returned False.")
        except Exception as e:
            ui.messageBox(f"❌ Import failed for {occ.component.name}:\n{e}\n\nFile path:\n{temp_path}")
            continue

        # Locate the new occurrence
        after_count = root_comp.occurrences.count
        if after_count <= before_count:
            ui.messageBox(f'⚠ Import succeeded but no new component found for {occ.component.name}.')
            continue

        new_occ = root_comp.occurrences.item(after_count - 1)
        
        if new_occ.isReferencedComponent:
            new_occ.breakLink()

        new_occ.component.name = safe_name

        # Remap joints (using the joint_mapping to find the original occurrence)
        for joint_name, orig_occ in joint_mapping.items():
            try:
                # Loop through original occurrence's joints
                for i in range(orig_occ.joints.count):
                    original_joint = orig_occ.joints.item(i)

                    # Create a new joint for the copied component
                    new_joint = new_occ.joints.addJoint(
                        original_joint.type,
                        original_joint.parentComponent,
                        original_joint.childComponent
                    )

                    # Add any additional properties if necessary
                    new_joint.jointType = original_joint.jointType
                    new_joint.isRigid = original_joint.isRigid

            except Exception as e:
                ui.messageBox(f"⚠ Error when remapping joint {joint_name}:\n{e}")

        # Cleanup temporary file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            ui.messageBox(f"⚠ Warning: Could not delete temp file for {occ.component.name}:\n{str(e)}")

        ui.messageBox(f'✅ Unlinked copy created for: {new_occ.name}')
