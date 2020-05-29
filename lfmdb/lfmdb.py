import logging
import sqlite3

import MySQLdb

from lfmconf.lfmconf import get_lastfm_conf

conf = get_lastfm_conf()

dbms = conf['lastfm']['db']['dbms']


def create_connection():
    connection = None
    if dbms == 'mysql':
        connection = MySQLdb.connect(
            user=conf['lastfm']['db'][dbms]['user'],
            passwd=conf['lastfm']['db'][dbms]['password'],
            db=conf['lastfm']['db'][dbms]['dbName'],
            charset='utf8')
    elif dbms == 'sqlite':
        connection = sqlite3.connect(conf['lastfm']['db'][dbms]['dbName'])

    return connection


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
    except (MySQLdb.Error, sqlite3.Error) as e:
        logging.exception('An error occurred when inserting into database')
        connection.rollback()
        raise Exception


def insert_many(query, values):
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        if dbms == 'sqlite':
            values = list(zip(values))
        cursor.executemany(query, values)
        connection.commit()
    except (MySQLdb.Error, sqlite3.Error) as e:
        logging.exception('An error occurred when inserting into database')
        connection.rollback()
        raise Exception
