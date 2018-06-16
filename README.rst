# PyStatsBomb

This is a python client to grab StatsBomb Free Match Data from the StatsBomb github repository. https://github.com/statsbomb/open-data

To run:

```python
import pystatsbomb as sb
import pandas as pd
```

Initialize the client
Optional source to local directory with match data

```python
c = sb.Client(source=None)
```

Data for competitions, lineups, matches, events is stored in JSON format
Optional call to grab all at once. Also optional to put into pandas dataframes

```python
c.get_all_sb_data(comp_id=None, match_id=None, toPandas=False)
```


# There is a first attempt at plotting as well in StatsBombAnalysis.ipynb
