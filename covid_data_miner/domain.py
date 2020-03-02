import typing

CovidPoint = typing.NamedTuple(
    "CovidPoint", (
        ("source", str),
        ("timestamp", int),
        ("last_update", int),
        ("country", str),
        ("province", str),
        ("confirmed_cumulative", int),
        ("hospitalized_cumulative", int),
        ("severe_cumulative", int),
        ("death_cumulative", int),
        ("recovered_cumulative", int),
        ("lat", float),
        ("lon", float)
    )
)
