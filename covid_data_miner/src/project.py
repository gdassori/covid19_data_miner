class ProjectionsReactor:
    def __init__(self, interval=10):
        self._projections = []
        self.interval = interval

    def add_projection(self, detonator, projector):
        self._projections.append([detonator, projector])

    def on_new_data(self, data):
        for detonator, projector in self._projections:
            projector.project(detonator(data))

    def rewind(self):
        for detonator, projector in self._projections:
            projector.rewind()
