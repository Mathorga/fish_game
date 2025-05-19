class Grabbable:
    def __init__(self):
        self.grabbed = False

    def toggle_grab(self, toggle: bool) -> None:
        self.grabbed = toggle