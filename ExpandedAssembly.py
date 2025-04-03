# Assuming you have not changed the general structure of the template no modification is needed in this file.
print("In File")

from . import commands
from .lib import fusionAddInUtils as futil

print("In File")
def run(context):
    print("In Run")
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()
        print("In start")

    except:
        futil.handle_error('run')

def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')