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
        ("females_deaths", int),
        ("males_deaths", int),
        ("total_deaths", int),
        ("females_0_14_deaths", int),
        ("males_0_14_deaths", int),
        ("total_0_14_deaths", int),
        ("females_15_64_deaths", int),
        ("males_15_64_deaths", int),
        ("total_15_64_deaths", int),
        ("females_65_74_deaths", int),
        ("males_65_74_deaths", int),
        ("total_65_74_deaths", int),
        ("females_over75_deaths", int),
        ("males_over75_deaths", int),
        ("total_over75_deaths", int),
        ("source", str)
    )
)
