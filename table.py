import pandas as pd
from moment import evaluate_not_none
from dep_graph import find_dep_graph

PRETTY_DATES = {
    'MS': '%b-%y',
    'W-FRI': '%d-%b',
    'D': '%d-%m',
    'Q': 'Q%q-%y',
    'A': '%Y',
}

today = {
    True: 'today',
    False: '',
}
df_today = {
    True: 'true',
    False: 'false',
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
    'color': 'black',
    'border-bottom': '1pt solid black',
    'border-top': '1pt solid black',
}
level_2_css = {
    'font-size': 'small',
}
css_level_0 = "background-color:#ecebea;border-bottom:1pt solid black;border-top:1pt solid black;color:black"
css_level_1 = 'text-indent:10%;font-size:smaller;'
css_level_2 = 'text-indent:20%;font-size:x-small;'


def pandas_dep_graph(config):
    _config = config.reset_index().reset_index()
    dependants = _extract_by_series_id(_config, 'parent', 'series_id')
    rows = _extract_by_series_id(_config, 'index', 'series_id')
    clean_dependants = {k: [v] if not pd.isna(
        v) else [] for k, v in dependants.items()}
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


def define_predicted_cells(data, config):
    predicted_data = data.copy()
    predicted = _extract_by_series_id(config, 'last_series')
    for series in data:
        predicted_data[series] = pd.isna(data[predicted[series]]).map(df_today)
    return predicted_data


def _reshape_balance(data, config, freq):
    data.index = data.index.strftime(PRETTY_DATES[freq])
    pretty_names = _extract_by_series_id(config, 'label', 'series_id')
    data = data.rename(columns=pretty_names)[list(pretty_names.values())]
    data = data.T
    return data


def compute_nodes(data, config):
    _series = [
        x for x in config.sort_values('level', ascending=False)['series_id']
        if x not in data.columns
    ]
    for parent in _series:
        child_series = config[config.parent == parent]['series_id'].values
        agg_operation = config[config.series_id ==
                               parent]['parent_agg'].values[0]
        data[parent] = data[child_series].agg(agg_operation, axis=1)
    return data


def reshape_to_balance_table(data, config, start, end, freq, today=None):
    today = today or pd.Timestamp.now()
    start, end = evaluate_not_none(start), evaluate_not_none(end)
    data = compute_nodes(data, config)
    aggs = _extract_by_series_id(config, 'freq_agg')
    data = data.resample(freq).agg(aggs)
    data.index = data.index.to_period()
    data = data[(data.index.start_time >= start)
                & (data.index.end_time <= end)]
    predicted = _reshape_balance(
        define_predicted_cells(data, config),
        config,
        freq,
    )
    is_today = (data.index.start_time < today) & (today < data.index.end_time)
    data = _reshape_balance(data, config, freq)
    return data, config, is_today, predicted
