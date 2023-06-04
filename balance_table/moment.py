from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser

import pandas as pd

from psyl.lisp import evaluate, Env


def lastoccurrenceof(ref_date, month, day):
    pseudo_date = datetime(year=ref_date.year, month=month, day=day)
    if pseudo_date > ref_date:
        last_occurrence = pseudo_date.replace(year=pseudo_date.year - 1)
    else:
        last_occurrence = pseudo_date
    return last_occurrence


def nextoccurrenceof(ref_date, month, day):
    pseudo_date = datetime(year=ref_date.year, month=month, day=day)
    if pseudo_date <= ref_date:
        next_occurrence = pseudo_date.replace(year=pseudo_date.year + 1)
    else:
        next_occurrence = pseudo_date
    return next_occurrence


def date_to_datetime(dat):
    if hasattr(dat, 'hour'):
        return datetime(dat.year, dat.month, dat.day, dat.hour)
    else:
        return datetime(dat.year, dat.month, dat.day)


def datenow():
    return date_to_datetime(datetime.now())


def datetoday():
    return date_to_datetime(datetime.now().date())


ENV = Env({
    'now': datenow,
    'today': datetoday,
    'monthstart': lambda dt: dt.replace(day=1),
    'yearstart': lambda dt: dt.replace(day=1, month=1),
    'yearend': lambda dt: dt.replace(day=31, month=12),
    'deltahours': lambda dt, hours: dt + relativedelta(hours=hours),
    'deltadays': lambda dt, days: dt + relativedelta(days=days),
    'deltamonths': lambda dt, months: dt + relativedelta(months=months),
    'deltayears': lambda dt, years: dt + relativedelta(years=years),
    'date': lambda strdate: parser.parse(strdate),
    'lastoccurrenceof': lastoccurrenceof,
    'nextoccurrenceof': nextoccurrenceof
})


def evaluate_not_none(expr):
    if pd.isnull(expr):
        return None
    return pd.to_datetime(evaluate(expr, ENV))
