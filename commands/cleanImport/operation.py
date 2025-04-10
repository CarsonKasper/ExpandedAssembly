import adsk.core
import adsk.fusion
import os

def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    try:
        inputs = args.command.commandInputs
        path_input = inputs.itemById('file_path')
        file_path = path_input.value.strip()

        if not os.path.exists(file_path):
            ui.messageBox('File not found: ' + file_path)
            return

        import_mgr = app.importManager
        import_options = import_mgr.createFusionArchiveImportOptions(file_path)
        import_result = import_mgr.importToTarget(import_options, root_comp)

        if not import_result:
            ui.messageBox('Import failed.')
            return

        # Get the newly imported occurrence
        new_occ = None
        for i in range(root_comp.occurrences.count):
            occ = root_comp.occurrences.item(i)
            if occ.component.isImportedComponent:
                new_occ = occ

        if not new_occ:
            ui.messageBox('Failed to find imported occurrence.')
            return

        # Copy bodies and sketches into a new native component
        new_comp = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        new_comp.name = os.path.splitext(os.path.basename(file_path))[0] + ' (Clean)'

        for body in new_occ.component.bRepBodies:
            if body.isSolid:
                body.copyToComponent(new_comp)

        for sketch in new_occ.component.sketches:
            sketch.copyToComponent(new_comp)

        # Remove the original imported occurrence
        new_occ.deleteMe()

        ui.messageBox(f'Clean import complete: {new_comp.name}')

    except:
        if ui:
            ui.messageBox('An unexpected error occurred in Clean Import.')
