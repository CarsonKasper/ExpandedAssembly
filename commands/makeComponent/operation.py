import adsk.core
import adsk.fusion
import traceback
import os
from ..unlinkedCopy import operation as unlinked_copy

def run_operation(args: adsk.core.CommandEventArgs):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    root_comp = design.rootComponent

    try:
        inputs = args.command.commandInputs
        selections_input = inputs.itemById('target_components')
        name_input = inputs.itemById('new_component_name')

        if selections_input.selectionCount == 0:
            ui.messageBox('No components selected.')
            return

        new_name = name_input.text.strip() or 'New Component Group'
        new_occurrence = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        new_component = new_occurrence.component
        new_component.name = new_name

        copied_occurrences = []

        for i in range(selections_input.selectionCount):
            occ = adsk.fusion.Occurrence.cast(selections_input.selection(i).entity)
            if not occ:
                continue

            # Build mock inputs for Unlinked Copy
            class FakeArgs:
                def __init__(self, occ, name):
                    self.command = self
                    self.commandInputs = self
                    self._inputs = {
                        'target_component': FakeSelectionInput(occ),
                        'copy_name': FakeTextBoxInput(name)
                    }

                def itemById(self, id):
                    return self._inputs.get(id)

            class FakeSelectionInput:
                def __init__(self, occ):
                    self._selection = occ

                def selectionCount(self):
                    return 1

                def selection(self, _):
                    return adsk.core.Selection.create(self._selection, None)

            class FakeTextBoxInput:
                def __init__(self, text):
                    self.text = text

            safe_name = f'{occ.name}_UC'
            fake_args = FakeArgs(occ, safe_name)

            before_count = root_comp.occurrences.count
            unlinked_copy.run_operation(fake_args)
            after_count = root_comp.occurrences.count

            if after_count > before_count:
                new_occ = root_comp.occurrences.item(after_count - 1)
                copied_occurrences.append(new_occ)
            else:
                ui.messageBox(f'Failed to copy: {occ.name}')

        for occ in copied_occurrences:
            occ.transform = adsk.core.Matrix3D.create()
            occ.moveToComponent(new_component)

        # Delete original occurrences
        for i in range(selections_input.selectionCount):
            occ = adsk.fusion.Occurrence.cast(selections_input.selection(i).entity)
            occ.deleteMe()

        ui.messageBox(f'✅ Created new component "{new_component.name}" with {len(copied_occurrences)} items.')

    except Exception as e:
        ui.messageBox(f'❌ Operation failed:\n{traceback.format_exc()}')
