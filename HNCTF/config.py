#encoding: utf-8
import os
import pymysql

DEBUG = True

SECRET_KEY = os.urandom(24)
pymysql.install_as_MySQLdb()
DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'HNCTF2018'
PASSWORD = 'HNCTF2018'
HOST = '47.95.13.227'
PORT = '3306'
DATABASE = 'HNCTF'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME,
                                              PASSWORD, HOST, PORT, DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False