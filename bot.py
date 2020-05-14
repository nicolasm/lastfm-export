from datetime import datetime
from math import ceil

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from lfmconf.lfmconf import get_lastfm_conf
from lfmpandas.lfmpandas import AggregationType, DataFrameColumn, Top, \
    OverType
from plottop.plotop import Duration, Year, PlotType
from plot.plot import plot_top

ENTITY, TIME_PERIOD_TYPE, TIME_PERIOD, PLOT_TYPE, COLUMN = range(5)

conf = get_lastfm_conf()
my_chat_id = conf['telegram']['chatId']


def start(update, context):
    reply_keyboard = [[e.name for e in Top]]

    chat_id = update.message['chat']['id']
    if chat_id == my_chat_id:
        update.message.reply_text('Choose an entity',
                                  reply_markup=ReplyKeyboardMarkup(
                                      reply_keyboard,
                                      one_time_keyboard=True))
        return ENTITY
    else:
        update.message.reply_text('Access denied')
        return ConversationHandler.END


def entity(update, context):
    context.user_data['entity'] = update.message['text']
    reply_keyboard = [[e.name for e in OverType]]

    update.message.reply_text('Choose an time period type',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return TIME_PERIOD_TYPE


def time_period_type(update, context):
    def build_period_type_keyboard(type_in):
        keyboard = []
        if type_in == OverType.Duration.name:
            keyboard = build_duration_keyboard()
        elif type_in == OverType.Year.name:
            keyboard = build_year_keyboard()
        return keyboard

    def build_duration_keyboard():
        return [['7', '30', '90'],
                ['180', '365', 'All-time']]

    def build_year_keyboard():
        year_keyboard = []
        now = datetime.now()
        years = range(now.year, 2005, -1)
        nb_cols = 3
        nb_rows = ceil(len(years) / nb_cols)
        year_index = 0
        for i in range(0, nb_rows):
            year_row = []
            for j in range(0, nb_cols):
                if year_index < len(years):
                    year_row.append(str(years[year_index]))
                    year_index = year_index + 1

            year_keyboard.append(year_row)
        return year_keyboard

    type = update.message['text']

    context.user_data['time_period_type'] = type

    reply_keyboard = build_period_type_keyboard(type)

    update.message.reply_text('Choose a value',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return TIME_PERIOD


def time_period(update, context):
    context.user_data['time_period'] = update.message['text']

    reply_keyboard = [[e.name for e in PlotType]]

    update.message.reply_text('Choose a plot type',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return PLOT_TYPE


def plot_type(update, context):
    def build_data_frame_column_keyboard(context):
        entity = context.user_data['entity']
        top = Top.from_value(entity)
        return [[e.name for e in top.columns]]

    context.user_data['plot_type'] = update.message['text']

    reply_keyboard = build_data_frame_column_keyboard(context)

    update.message.reply_text('Choose a DataFrame column',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))

    return COLUMN


def column(update, context):
    context.user_data['column'] = update.message['text']

    time_period_type = context.user_data['time_period_type']
    time_period = context.user_data['time_period']
    entity = context.user_data['entity']
    agg_type = AggregationType.from_value(time_period_type + entity)
    plot_type = PlotType.from_value(context.user_data['plot_type'])
    data_frame_column = DataFrameColumn.from_value(context.user_data['column'])

    tp_value = None
    if time_period_type == OverType.Duration.name:
        tp_value = Duration.from_value(time_period)
    elif time_period_type == OverType.Year.name:
        tp_value = Year(time_period)

    bio = plot_top(tp_value, agg_type, plot_type, data_frame_column)
    bio.seek(0)

    update.message.reply_photo(bio)
    bio.close()
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('Canceled.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater(conf['telegram']['token'], use_context=True)

    dp = updater.dispatcher

    entities = '|'.join([e.name for e in Top])
    period_types = '|'.join([e.name for e in OverType])

    now = datetime.now()
    years = range(conf['lastfm']['service']['startYear'], now.year + 1)
    time_periods = [e.get_value() for e in Duration]
    time_periods.extend(str(y) for y in years)
    allowed_periods = '|'.join(time_periods)

    plot_types = '|'.join([e.name for e in PlotType])

    columns = '|'.join([c.name for c in DataFrameColumn])

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ENTITY: [
                MessageHandler(Filters.regex('^(%s)$' % entities),
                               entity)],

            TIME_PERIOD_TYPE: [
                MessageHandler(Filters.regex('^(%s)$' % period_types),
                               time_period_type)],

            TIME_PERIOD: [
                MessageHandler(Filters.regex('^(%s)$' % allowed_periods),
                               time_period)],

            PLOT_TYPE: [
                MessageHandler(Filters.regex('^(%s)$' % plot_types),
                               plot_type)],

            COLUMN: [
                MessageHandler(Filters.regex('^(%s)$' % columns),
                               column)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
