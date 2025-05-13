
import adsk.core
import adsk.fusion
import traceback

def run_operation(args):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        root_comp = design.rootComponent

        inputs = args.command.commandInputs
        selection_input = inputs.itemById('selection_input')

        if not selection_input or selection_input.selectionCount != 2:
            ui.messageBox('Please select exactly two points from different components.')
            return

        point1 = selection_input.selection(0).entity
        point2 = selection_input.selection(1).entity

        comp1 = point1.assemblyContext or point1.parentComponent
        comp2 = point2.assemblyContext or point2.parentComponent

        if comp1 == comp2:
            ui.messageBox('Points must be from different components.')
            return

        occ1 = point1.assemblyContext
        occ2 = point2.assemblyContext

        if not occ1 or not occ2:
            ui.messageBox('Both points must be inside occurrences (placed components).')
            return

        # Calculate transformation to align point1 to point2
        vec = adsk.core.Vector3D.create(
            point2.worldGeometry.x - point1.worldGeometry.x,
            point2.worldGeometry.y - point1.worldGeometry.y,
            point2.worldGeometry.z - point1.worldGeometry.z
        )
        transform = adsk.core.Matrix3D.create()
        transform.translation = vec
        occ1.transform = occ1.transform.copy()
        occ1.transform.transformBy(transform)

        # Create rigid group
        rigid_groups = root_comp.assemblyContext.asBuiltJointGroups
        if not rigid_groups:
            rigid_groups = root_comp.asBuiltJointGroups
        group = rigid_groups.add()
        group.addByOccurrences([occ1, occ2])

        ui.messageBox('✅ Components aligned and rigidly connected.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
