import logging
import sqlite3

from lfmconf.lfmconf import get_lastfm_conf

conf = get_lastfm_conf()


def create_connection():
    dbName = conf['lastfm']['db']['sqlite']['dbName']
    return sqlite3.connect(dbName)


def select_one(query, params=()):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()


def select(query, params=()):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def insert(connection, cursor, query, tuple_in):
    try:
        cursor.execute(query, tuple_in)
        connection.commit()
    except sqlite3.Error:
        logging.exception('An error occurred when inserting into database')
        connection.rollback()
        raise Exception


def insert_many(query, values):
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        values = list(zip(values))
        cursor.executemany(query, values)
        connection.commit()
    except sqlite3.Error:
        logging.exception('An error occurred when inserting into database')
        connection.rollback()
        raise Exception
