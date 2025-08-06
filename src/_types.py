from typing import Literal


OperatorReturnItems = Literal[
    "RUNNING_MODAL",  # Running Modal.Keep the operator running with blender.
    # Cancelled.The operator exited without doing anything, so no undo entry should be pushed.
    "CANCELLED",
    "FINISHED",  # Finished.The operator exited after completing its action.
    "PASS_THROUGH",  # Pass Through.Do nothing and pass the event on.
    "INTERFACE",  # Interface.Handled but not executed (popup menus).
]