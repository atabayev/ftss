import datetime
import email
import imaplib
import os
from time import sleep
from zipfile import ZipFile
import psycopg2
import shutil
import random

db_name = "db_fts"
db_user = "db_admin"
db_pswd = "admin_1357S"


def reform_date(in_date):
    tmp = in_date.strftime('%d.%m.%Y %H:%M')
    return datetime.datetime.strptime(tmp, '%d.%m.%Y %H:%M')


def logging(func_name, msg):
    log_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + 'logs'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_fl = os.path.join(log_path, 'log.txt')
    key = 'w'
    if os.path.isfile(log_fl):
        key = 'a'
    message = '[{0}] <{1}> : {2} \n'.format(datetime.datetime.now().strftime('%d.%m.%Y %H:%M'), func_name, msg)
    with open(log_fl, key) as fl:
        fl.write(message)


def run():
    try:
        datetime_now = datetime.datetime.strptime(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), "%d.%m.%Y %H:%M")
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pswd, host='127.0.0.1', port=5432) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM orders_order WHERE status=%s OR status=%s", ('25', '26'))
                orders = cursor.fetchall()
                cursor.close()
        conn.close()
        for order in orders:
            orders_date_difference = datetime_now - datetime.datetime.strptime(order[19], "%d.%m.%Y %H:%M")
            deadline_limit = datetime.timedelta(days=1)
            if orders_date_difference > deadline_limit:
                try:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pswd, host='127.0.0.1',
                                          port=5432) as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("UPDATE orders_order SET status = %s WHERE id = %s", ("0", order[0]))
                        cursor.close()
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging('Deadline checker', 'Ошибка при UPDATE: ' + str(e))
    except Exception as e:
        logging('Deadline checker', 'Ошибка: ' + str(e))


run()
