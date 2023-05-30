import numpy as np
import pandas as pd
import pandas as pd
from moment import evaluate_not_none
from dep_graph import find_dep_graph

WEEKLY_DATE = pd.date_range('2018', freq='W-FRI',periods=300)
MONTHLY_DATE = pd.date_range('2018', freq='MS',periods=30)
DAILY_DATE = pd.date_range('2018', freq='D',periods=30)

PRETTY_DATES = {
    'MS': '%b-%y',
    'W-FRI': '%d-%b',
    'D': '%d-%m',
    'Q': 'Q%q-%y',
    'A': '%Y',
}
series_name = [f'series_{x}' for x in range(1, 8)]
data = (pd.DataFrame(
    np.random.randn(300, len(series_name)), 
    columns=series_name,
    index=WEEKLY_DATE
) * 100)
CONFIG = pd.read_csv('config.csv').set_index(
    ['table_id', 'table_start', 'table_end', 'freq']
    )
today = {
    True: 'today',
    False: '',
}
cell_hover = {
    "selector": "tr:hover",
    "props": [("background-color", "#FFFFE0")]
}
cell_hover_2 = {
    "selector": "td:hover",
    "props": [("background-color", "#858536")]
}
today_css = {
    'border-left': '1px solid black',
    'border-right': '1px solid black'
}
level_0_css = {
    "background-color": '#004275',
    'font-weight': 'bold',
    'color': 'white',
    'border-bottom': '1pt solid black',
    'border-top': '1pt solid black',
}
level_2_css = {
    'font-size':'small',
}
css_level_0 = "background-color:#004275;border-bottom:1pt solid black;border-top:1pt solid black;color:white"
css_level_1 = 'text-indent:10%;font-size:smaller;'
css_level_2 = 'text-indent:20%;font-size:x-small;'

def pandas_dep_graph(config):
    _config = config.reset_index().reset_index()
    dependants = _extract_by_series_id(_config, 'parent', 'series_id')
    rows = _extract_by_series_id(_config, 'index', 'series_id')
    clean_dependants = {k: [v] if not pd.isna(v) else [] for k,v in dependants.items()}
    graph = find_dep_graph(clean_dependants)
    deps = {
        f'row{rows[k]}': [rows[v2] for v2 in v] 
        for k, v in graph.items()
        }
    return deps

def _extract_by_series_id(config, dim, key='series_id'):
    return config[[key, dim]].set_index(key)[dim].to_dict()

def _extract_by_series_id_series(config, dim, key='series_id'):
    return config[[key, dim]].set_index(key)[dim]

def reshape_to_balance_table(data, config, start, end, freq, today=None):
    today = today or pd.Timestamp.now()
    start, end = evaluate_not_none(start), evaluate_not_none(end)
    aggs = _extract_by_series_id(config, 'freq_agg')
    data = data[start:end].resample(freq).agg(aggs)
    data.index = data.index.to_period()
    is_today = (data.index.start_time < today) & (today < data.index.end_time)
    data.index = data.index.strftime(PRETTY_DATES[freq])
    pretty_names = _extract_by_series_id(config, 'label', 'series_id')
    data = data.rename(columns=pretty_names)[list(pretty_names.values())]
    data = data.T
    for col in data.columns:
        data.loc[data.sample(frac=0.1).index, col] = np.nan
    return data, config, is_today