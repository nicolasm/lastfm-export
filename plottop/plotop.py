import io
from enum import Enum

import colorlover as cl
import matplotlib.pyplot as plt
from pywaffle import Waffle

colors = cl.to_numeric(cl.scales['12']['qual']['Set3'])

int_colors = []
for color in colors:
    int_colors.append((int(color[0]), int(color[1]), int(color[2])))

selected_colors = []
for color in int_colors:
    selected_colors.append('#%02x%02x%02x' % color)


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
    ax = df.plot.barh(x=xcolumn, y='PlayCount', figsize=(20, 5), rot=0,
                      color=selected_colors)


def plot_waffle(df, xcolumn):
    play_dict = dict(zip(df[xcolumn], df['PlayCount']))
    plt.figure(
        FigureClass=Waffle,
        dpi=600,
        rows=30,
        columns=90,
        values=play_dict,
        figsize=(20, 10),
        legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1), 'framealpha': 0},
    )
