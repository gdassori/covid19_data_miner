import typing


class DailySummaryProjection:
    def __init__(self, measurement, repository):
        self.measurement = measurement
        self.projection_name = "{}_daily_summary"
        self.repository = repository

    def _get_latest_projection(self, measurement):
        pass

    def _save_projection(self, projection: typing.Dict):
        pass

    def _make_projection(self, previous: typing.Dict, points: typing.List[typing.Dict]):
        pass

    def project(self):
        pass

    def rewind(self, since: int):
        pass
