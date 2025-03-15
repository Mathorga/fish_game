class Gravitable:
    def __init__(self):
        self.gravity_enabled = True

    def toggle_gravity(self, toggle: bool) -> None:
        self.gravity_enabled = toggle