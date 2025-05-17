class Interactable:
    def __init__(self):
        self.interacting: bool = False

    def interact(self) -> None:
        if not self.interacting:
            self.interacting = True