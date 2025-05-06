import adsk.core
import adsk.fusion
import math


def run_operation(args):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    inputs = args.command.commandInputs
    from_input = inputs.itemById('from_selection')
    to_input = inputs.itemById('to_selection')
    flip = inputs.itemById('flip_direction').value
    rotate = inputs.itemById('rotate_90').value
    capture_position = inputs.itemById('capture_position').value

    if from_input.selectionCount < 1 or to_input.selectionCount < 1:
        ui.messageBox('You must select both FROM and TO points.')
        return

    from_entity = from_input.selection(0).entity
    to_entity = to_input.selection(0).entity

    from_comp = from_entity.assemblyContext or from_entity.parentComponent
    to_comp = to_entity.assemblyContext or to_entity.parentComponent

    if from_comp == to_comp:
        ui.messageBox('Selected points must belong to different components.')
        return

    from_pos = from_entity.geometry.center if hasattr(from_entity.geometry, 'center') else from_entity.geometry
    to_pos = to_entity.geometry.center if hasattr(to_entity.geometry, 'center') else to_entity.geometry

    translation = adsk.core.Vector3D.create(
        to_pos.x - from_pos.x,
        to_pos.y - from_pos.y,
        to_pos.z - from_pos.z
    )

    if flip:
        translation.scaleBy(-1)

    transform = adsk.core.Matrix3D.create()
    transform.translation = translation

    if rotate:
        z_axis = adsk.core.Vector3D.create(0, 0, 1)
        angle_rad = math.radians(90)
        rot_matrix = adsk.core.Matrix3D.create()
        rot_matrix.setToRotation(angle_rad, z_axis, to_pos)
        transform.transformBy(rot_matrix)

    # Apply the transform
    from_occ = get_occurrence(from_entity)
    if not from_occ:
        ui.messageBox('Failed to get occurrence of FROM selection.')
        return

    current_transform = from_occ.transform
    current_transform.transformBy(transform)
    from_occ.transform = current_transform

    # Create rigid joint
    joints = root_comp.joints
    geo1 = adsk.fusion.JointGeometry.createByPoint(from_entity)
    geo2 = adsk.fusion.JointGeometry.createByPoint(to_entity)
    joint_input = joints.createInput(geo1, geo2)
    joint_input.setAsRigidJointMotion()
    joint = joints.add(joint_input)

    if capture_position:
        joint.isFlipped = flip
        joint.isSuppressed = False

    ui.messageBox('✅ Components connected with a rigid joint.')

def get_occurrence(entity):
    try:
        return entity.assemblyContext if entity.assemblyContext else None
    except:
        return None
