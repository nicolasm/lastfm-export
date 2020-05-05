import io
from enum import Enum

import colorlover as cl
import matplotlib.pyplot as plt

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
    WEEK = '7'
    MONTH = '30'
    QUARTER = '90'
    SEMESTER = '180'
    YEAR = '365'
    OVERALL = None

    def get_value(self):
        if self.value is None:
            return "null"
        else:
            return self.value

    def get_label(self):
        if self.value is None:
            return self.name
        else:
            return self.value

    @staticmethod
    def from_value(str):
        for e in Duration:
            if e.name == str:
                return e


class Year(TimePeriod, object):
    def __init__(self, year):
        self.year = year

    def get_label(self):
        return str(self.year)

    def get_value(self):
        return str(self.year)


class PlotType(Enum):
    PIE = 'plot_pie'
    BARH = 'plot_barh'

    def __init__(self, method):
        self.method = method

    def plot(self, df, column):
        eval(self.method)(df, column.name)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150)
        return buffer

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

    # create a list to collect the plt.patches data
    totals = []

    # find the values and append to list
    for i in ax.patches:
        totals.append(i.get_width())

    for i in ax.patches:
        # get_width pulls left or right; get_y pushes up or down
        ax.text(i.get_width() + .3, i.get_y(), i.get_width(), fontsize=15,
                color='dimgrey')
