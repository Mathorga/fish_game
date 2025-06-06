class Grabbable:
    """
    Base class for grabbable objects.
    Grabbable objects can extend this class to inherit its features.
    """

    def __init__(self):
        self.grabbed = False

    def toggle_grab(self, toggle: bool) -> None:
        """
        Toggles the grabbable state on or of.
        """

        self.grabbed = toggle

    def move_to(
        self,
        position: tuple[float, float],
    ) -> None:
        """

        """