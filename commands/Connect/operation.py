import adsk.core
import adsk.fusion
import traceback


def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)

    inputs = args.command.commandInputs

    try:
        from_input = inputs.itemById('from_selection')
        to_input = inputs.itemById('to_selection')
        flip = inputs.itemById('flip_direction').value
        rotate = inputs.itemById('rotate_90').value
        capture_position = inputs.itemById('capture_position').value

        if from_input.selectionCount != 1 or to_input.selectionCount != 1:
            ui.messageBox('You must select both a FROM and TO point.')
            return

        from_entity = from_input.selection(0).entity
        to_entity = to_input.selection(0).entity

        # Get the transforms
        from_point = get_point(from_entity)
        to_point = get_point(to_entity)

        if not from_point or not to_point:
            ui.messageBox('Could not determine positions.')
            return

        from_occ = get_owning_occurrence(from_entity)
        to_occ = get_owning_occurrence(to_entity)

        if not from_occ or not to_occ or from_occ == to_occ:
            ui.messageBox('Selections must be from different components.')
            return

        # Transform from_occ so that from_point aligns to to_point
        vector = to_point.vectorTo(from_point)
        move_matrix = adsk.core.Matrix3D.create()
        move_matrix.translation = vector

        if flip:
            flip_matrix = adsk.core.Matrix3D.create()
            flip_matrix.setToRotation(math.pi, adsk.core.Vector3D.create(0, 0, 1), from_point)
            move_matrix.transformBy(flip_matrix)

        if rotate:
            rot_matrix = adsk.core.Matrix3D.create()
            rot_matrix.setToRotation(math.pi / 2, adsk.core.Vector3D.create(0, 0, 1), from_point)
            move_matrix.transformBy(rot_matrix)

        from_occ.transform2 = move_matrix

        if capture_position:
            from_occ.isGrounded = False
            from_occ.component.isGrounded = False

        # Create a rigid group
        root_comp = design.rootComponent
        rigid_input = root_comp.assemblyConstraints.createRigidGroupInput()
        rigid_input.addOccurrence(from_occ)
        rigid_input.addOccurrence(to_occ)
        root_comp.assemblyConstraints.addRigidGroup(rigid_input)

    except Exception as e:
        ui.messageBox(f'Error: {str(e)}')


def get_point(entity):
    try:
        if isinstance(entity, adsk.fusion.BRepVertex):
            return entity.geometry
        elif isinstance(entity, adsk.fusion.SketchPoint):
            return entity.geometry
        elif isinstance(entity, adsk.fusion.ConstructionPoint):
            return entity.geometry
        elif isinstance(entity, adsk.fusion.BRepEdge) and entity.geometry.curveType == adsk.core.Curve3DTypes.Circle3DCurveType:
            return entity.geometry.center
        else:
            return None
    except:
        return None


def get_owning_occurrence(entity):
    try:
        return entity.assemblyContext
    except:
        return None
