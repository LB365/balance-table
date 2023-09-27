from flask import render_template, Blueprint
import pandas as pd
import numpy as np
from balances.table import (
    _extract_by_series_id,
    _extract_by_series_id_series,
    reshape_to_balance_table,
    CELL_HOVER,
    CELL_HOVER_2,
    CSS_LEVEL_0,
    CSS_LEVEL_1,
    CSS_LEVEL_2,
    LEVEL_0_CSS,
    LEVEL_2_CSS,
    TODAY_CSS,
    pandas_dep_graph,
    pandas_parent_graph,
)

import jinja2
from viz.graphs.balances import TEMPLATE_LOCATION


def render_jinja_html(file_name, **context):
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_LOCATION) + '/template')
    ).get_template(file_name).render(context)


balance_table = Blueprint('table', __name__, template_folder='template')


def format_row_wise(styler, formatter):
    for row, row_formatter in formatter.items():
        row_num = styler.index.get_loc(row)
        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler


def __table_to_html(
    config, frame, is_today, predicted, diff_mode):
    levels = _extract_by_series_id_series(config, 'level', 'label')
    precision = _extract_by_series_id(config, 'precision', 'label')
    tol_diff = _extract_by_series_id(config, 'tol_diff', 'label')

    # Define precision and hovering per cell
    fn_precision = {
        k: lambda x: f"{x:,.{v}f}" if not pd.isna(x) else "-"
        for k, v in precision.items()
    }
    style = format_row_wise(frame.style, fn_precision).set_table_styles(
        [CELL_HOVER, CELL_HOVER_2]
    )
    # Today is highlighted
    style.set_properties(**TODAY_CSS, subset=style.columns[is_today])
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
    style.set_properties(**LEVEL_0_CSS, subset=level_0, axis=1)
    style.set_properties(**LEVEL_2_CSS, subset=level_2, axis=1)
    style.applymap_index(
        lambda v: CSS_LEVEL_0 if v in _level_0 else None, axis=0)
    style.applymap_index(
        lambda v: CSS_LEVEL_1 if v in _level_1 else None, axis=0)
    style.applymap_index(
        lambda v: CSS_LEVEL_2 if v in _level_2 else None, axis=0)

    def color_current(s):
        current = "background-color: #add8e6;border-left:1pt solid black;border-right:1pt solid black"
        return current if s == frame.columns[is_today] else None

    style.applymap_index(color_current, axis=1)

    def diff_colors(series):
        colors ={
            -1: "color:rgba(220, 20, 60, 1);",
             0: "color:rgba(0, 0, 0, 0.0);",
             1: "color:rgba(34, 139, 34, 1);",
        }
        tolerance = tol_diff[series.name]
        print(series.name, tolerance)
        greater = (series > tolerance)
        lower = (series < - tolerance)
        indicator = np.where(greater, 1, 0) - np.where(lower,1, 0)
        colors = pd.Series(indicator).map(colors)
        return colors.values

    if diff_mode:
        style.apply(diff_colors, axis=1)
    return style

from collections import namedtuple

JinjaBalance = namedtuple('JinjaBalance', ['data', 'html'])

def table_to_html_for_jinja(
    data, config, freq, start, end, diff_mode=False):
    frame, config, is_today, predicted = reshape_to_balance_table(
        data,
        config,
        start,
        end,
        freq
    )
    style = __table_to_html(config, frame, is_today, predicted, diff_mode)
    styled = style.to_html()
    # Define the hierarchy graph for user interation
    hierarchy = pandas_dep_graph(config)
    parents = pandas_parent_graph(config)
    return JinjaBalance(
        frame, render_jinja_html(
        "table.html",
        table=styled,
        hierarchy=hierarchy,
        parents=parents,
        dims=frame.shape,
    ))


def _table_to_html(
    data, config, table_id, freq, start, end):
    frame, config, is_today, predicted = reshape_to_balance_table(
        data,
        config.xs(table_id),
        start,
        end,
        freq
    )
    style = __table_to_html(config, frame, is_today, predicted)
    styled = style.to_html()
    # Define the hierarchy graph for user interation
    hierarchy = pandas_dep_graph(config)
    parents = pandas_parent_graph(config)
    return render_template(
        "table.html",
        table=styled,
        hierarchy=hierarchy,
        parents=parents,
        dims=frame.shape,
    )


@balance_table.route('/table/<table_id>/<freq>/<start>/<end>')
def table_to_html(table_id, freq, start, end):
    flasky = _table_to_html(
        balance_table.data,
        balance_table.CONFIG,
        table_id,
        freq,
        start,
        end
    )
    return flasky
