import pandas as pd
from flask import render_template, Blueprint
import pandas as pd
from table import (
    _extract_by_series_id,
    _extract_by_series_id_series,
    reshape_to_balance_table,
    cell_hover,
    cell_hover_2,
    css_level_0,
    css_level_1,
    css_level_2,
    level_0_css,
    level_2_css,
    today_css,
    pandas_dep_graph,
)

balance_table = Blueprint('table', __name__, template_folder='template')

def format_row_wise(styler, formatter):
    for row, row_formatter in formatter.items():
        row_num = styler.index.get_loc(row)
        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler

@balance_table.route('/table/<table_id>/<freq>/<start>/<end>')
def table_to_html(table_id, freq, start, end):
    frame, _config, is_today, predicted = reshape_to_balance_table(
        balance_table.data, 
        balance_table.CONFIG.xs(table_id), 
        start, 
        end, 
        freq
    )
    levels = _extract_by_series_id_series(_config, 'level', 'label')
    precision = _extract_by_series_id(_config, 'precision', 'label')
    # Define precision and hovering per cell
    fn_precision = {
        k:lambda x:f"{x:0.{v}f}" if not pd.isna(x) else "-" 
        for k, v in precision.items()
    }
    style = format_row_wise(frame.style, fn_precision).set_table_styles(
        [cell_hover, cell_hover_2]
    )
    # Today is highlighted
    style.set_properties(**today_css, subset=style.columns[is_today])
    # Define hierchical style
    idx = pd.IndexSlice
    _level_0 = levels[levels == 0].index
    _level_1 = levels[levels == 1].index
    _level_2 = levels[levels == 2].index
    level_0 = idx[idx[_level_0], idx[style.columns]]
    level_2 = idx[idx[_level_2], idx[style.columns]]
    style.set_table_styles([  # create internal CSS classes
    {'selector': '.true', 'props': 'background-color: #ffffbc;'},
    {'selector': '.false', 'props': 'background-color: #ffffff;'},
    ], overwrite=False)
    style.set_td_classes(predicted)
    style.set_properties(**level_0_css, subset=level_0, axis=1)
    style.set_properties(**level_2_css, subset=level_2, axis=1)
    style.applymap_index(lambda v: css_level_0 if v in _level_0 else None, axis=0)
    style.applymap_index(lambda v: css_level_1 if v in _level_1 else None, axis=0)
    style.applymap_index(lambda v: css_level_2 if v in _level_2 else None, axis=0)
    def color_current(s):
        current = "background-color: #add8e6;border-left:1pt solid black;border-right:1pt solid black"
        return current if s == frame.columns[is_today] else None
    style.applymap_index(color_current, axis=1)
    styled = style.to_html()
    # Define the hierarchy graph for user interation 
    hierarchy = pandas_dep_graph(_config)
    return render_template(
        "table.html", 
        table=styled,
        hierarchy=hierarchy,
        dims = frame.shape,
        )