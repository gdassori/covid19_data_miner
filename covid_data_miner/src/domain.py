import datetime
import typing

CovidPoint = typing.NamedTuple(
    "CovidPoint", (
        ("source", str),
        ("timestamp", datetime.datetime),
        ("last_update", int),
        ("country", str),
        ("region", str),
        ("city", str),
        ("confirmed_cumulative", int),
        ("hospitalized_cumulative", int),
        ("severe_cumulative", int),
        ("death_cumulative", int),
        ("recovered_cumulative", int),
        ("tests_cumulative", int)
    )
)


IstatDeathRatePoint = typing.NamedTuple(
    "IstatDeathRate", (
        ("timestamp", datetime.datetime),
        ("country", str),
        ("province", str),
        ("region", str),
        ("city", str),
        ("age_range", str),
        ("females_deaths", int),
        ("males_deaths", int),
        ("total_deaths", int),
        ("source", str)
    )
)
