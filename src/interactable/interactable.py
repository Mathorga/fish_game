class Interactable:
    """
    Base class for interactable objects.
    Interactable objects can extend this class to inherit its features.
    """

    def __init__(self):
        self.interacting: bool = False

    def interact(self) -> None:
        """
        Toggles the interacting state on or of.
        """

        if not self.interacting:
            self.interacting = True