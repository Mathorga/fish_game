class Interactable:
    """
    Base class for interactable objects.
    Interactable objects can extend this class to inherit its features.
    """

    def __init__(
        self,
        start_state: bool = False,
        one_shot: bool = True
    ):
        self.on: bool = start_state
        self.__one_shot: bool = one_shot
        self.__state_changed: bool = False

    def interact(
        self,
        tags: list[str]
    ) -> None:
        """
        Toggles the interacting state on or of.
        """

        if self.__one_shot and self.__state_changed:
            return

        self.on = not self.on
        self.__state_changed = True

    def is_active(self) -> bool:
        return not (self.__one_shot and self.__state_changed)