### Adding sources

Is easy to add more sources.

As it can be seen into an already implemented class [here](https://github.com/gdassori/covid19_data_miner/blob/master/covid_data_miner/src/sources/dpc_ita_github_points_service.py)


The class structure must be compliant to the following:

```python
class DPCItaGithubPointsService:

    tags = ['region']
    country = 'Italy'
    source_type = 'regional'
    source_name = 'Dipartimento Protezione Civile'
    
    def __init__(self, authentication_key):
       ...
       
    def get_points_since(self, timestamp: int) -> typing.List[CovidPoint]:
       ...

    def get_last_update(self) -> int:       
       ...      
```

A service is a class with the `authentication_key` argument and two methods: `get_points_since(timestamp)` and `get_last_update`.

- The constructor must accept the "authentication_key" parameter even if not used in the service.
- The method get_points_since MUST return a list of CovidPoint objects (namedtuple), and MUST take an integer epoch timestamp.
- The method get_last_update doesn't take any argument and MUST return an interger (or 0) as epoch timestamp.

What is a [CovidPoint](https://github.com/gdassori/covid19_data_miner/blob/master/covid_data_miner/src/domain.py) ?

Just a named tuple representing a time-serie point:
```
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
```

Remember that all the parameters MUST be populated with the proper type, even if empty (i.e. some sources doesn't return data on severes, so the value must be set to 0).

Once a service is created, it must be add to the [sources factory](https://github.com/gdassori/covid19_data_miner/blob/master/covid_data_miner/src/sources/factory.py#L10):

```python
  {
    'worldometers': WorldometersGithubPointsService,
    'csse': CSSEGISandDataPointsService,
    'dpc_ita': DPCItaGithubPointsService,
    'covidtracking_usa': CovidTrackingUSAPointsService,
    'rki_de': RkiDeGithubPointsService
  }
```

So just add to the dictionary in the constructor the new source.

If everything is ok, the source will be available in the client:

```bash
(env) guido@flatline:~$ covid19 sources ls

Available sources:

name               tags     country    type      description
-----------------  -------  ---------  --------  ------------------------------
covidtracking_usa  region   USA        regional  covidtracking.com (CDC)
csse               country  World      global    CSSE (JHU)
dpc_ita            region   Italy      regional  Dipartimento Protezione Civile
rki_de             region   Germany    regional  Robert Koch Institute
worldometers       country  World      global    worldometers.info (many)

(env) guido@flatline:~$ 

```
