import io
from enum import Enum

import matplotlib.pyplot as plt
from pywaffle import Waffle

# https://sashamaps.net/docs/resources/20-colors/
selected_colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                   '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4',
                   '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000',
                   '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9',
                   '#ffffff', '#000000']


class TimePeriod:
    def get_value(self):
        pass

    def get_label(self):
        pass


class Duration(TimePeriod, Enum):
    WEEK = ('7', False)
    MONTH = ('30', False)
    QUARTER = ('90', False)
    SEMESTER = ('180', False)
    YEAR = ('365', False)
    OVERALL = ('All-time', True)

    def __init__(self, duration, label_value):
        self.duration = duration
        self.label = duration if label_value else 'last-%s-days' % duration

    def get_value(self):
        return self.duration

    def get_label(self):
        return self.label

    @staticmethod
    def from_value(val):
        for e in Duration:
            if e.duration == val:
                return e


class Year(TimePeriod, object):
    def __init__(self, year):
        self.year = year

    def get_label(self):
        return str(self.year)

    def get_value(self):
        return str(self.year)


class PlotType(Enum):
    Pie = 'plot_pie'
    BarH = 'plot_barh'
    Waffle = 'plot_waffle'

    def __init__(self, method):
        self.method = method

    def plot(self, df, column):
        eval(self.method)(df, column.name)
        bio = io.BytesIO()
        plt.savefig(bio, format='png', dpi=150, bbox_inches='tight')
        return bio

    def get_name(self):
        return self.name.lower()

    @staticmethod
    def from_value(str):
        for e in PlotType:
            if e.name == str:
                return e


def plot_pie(df, legend_column):
    df.plot.pie(y='PlayCount', labels=df['PlayCount'], figsize=(12, 5),
                legend=True, colors=selected_colors)
    plt.legend(df[legend_column], loc="center left",
               bbox_to_anchor=(1, 0, 0.5, 1))


def plot_barh(df, xcolumn):
    ax = df.plot.barh(x=xcolumn, y='PlayCount', figsize=(20, 10),
                      rot=0)
    plt.yticks(fontsize=16)


def plot_waffle(df, xcolumn):
    num_colors = len(df)
    play_dict = dict(zip(df[xcolumn], df['PlayCount']))

    plt.figure(
        FigureClass=Waffle,
        dpi=600,
        rows=50,
        columns=50,
        values=play_dict,
        labels=[f"{k} ({v})" for k, v in play_dict.items()],
        colors=selected_colors[:num_colors],
        figsize=(20, 10),
        legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1), 'framealpha': 0}
    )
