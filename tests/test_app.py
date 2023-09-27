import pandas as pd
import numpy as np
from viz.graphs.balances.blueprint import balance_table
from flask import Flask
from pathlib import Path
HERE = Path(__file__).parent
N_OBS = 1000
WEEKLY_DATE = pd.date_range('2018', freq='W-FRI', periods=N_OBS)

series_name = [f'series_{x}' for x in range(1, 9)]
data = (pd.DataFrame(
    np.random.randn(N_OBS, len(series_name)),
    columns=series_name,
    index=WEEKLY_DATE
) * 100)
data['series_3'] = data['series_3'].fillna(0)
data = data.assign(
    series_3=lambda x: np.where(
        x.index < pd.Timestamp.now(), x['series_3'], np.nan)
)
CONFIG = pd.read_csv(HERE / 'config.csv').set_index('table_id')

if __name__ == '__main__':
    balance_table.CONFIG = CONFIG
    balance_table.data = data
    app = Flask(__name__, template_folder='template')
    app.register_blueprint(balance_table)
    app.run(host='localhost', debug=True, port=8080)
