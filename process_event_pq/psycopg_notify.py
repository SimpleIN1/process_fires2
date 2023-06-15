import asyncio
import datetime
import json

import psycopg2

from process_fire.base.log import Log
from process_fire.config import db_name, db_host, db_user, db_password, db_port, db_listen_event
from process_fire_value import ProcessFirePoint


class Psycopg2Notify:
    conn = None
    cursor = None

    def __init__(self):
        self.conn = psycopg2.connect(
            host=db_host,
            dbname=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
        )
        self.cursor = self.conn.cursor()
        self.loop = None

        self.process_fire_point = ProcessFirePoint()
        self.count = 0
        self.logger = Log('logs')

    def listen_events(self):
        self.cursor.execute(f'LISTEN {db_listen_event};')

    def set_autocommit(self):
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def display_upload_status(self, id_obj):
        if self.count == 0:
            print('\033[39m{} '.format(datetime.datetime.now()), end='')
            print('\033[32m{}'.format('Load'), end='')

        self.count += 1
        if self.count % 50 == 0:
            print('\033[39m{}'.format('.'), end='')
        if self.count % 200 == 0:
            self.logger.logger.info('The written 200 has been insert...')
        if self.count == 1000:
            self.count = 0
            print('\033[32m{}'.format('| '), end='')
            print('\033[39m{}'.format(f' Extreme identifier - {id_obj}'))

    def display_failed_status(self, message):
        print('\033[31m{} {}'.format('Failed!', message))

    def handle_notify(self):
        try:
            self.conn.poll()
            # print('\033[32m{}'.format('Load'), end='')
            for notify in self.conn.notifies:
                # print(notify.payload)
                json_obj = json.loads(notify.payload)
                #print(json_obj)
                self.process_fire_point.run_process(
                    json_obj['id'],
                    json_obj['longitude'],
                    json_obj['latitude']
                )

                # self.display_upload_status(json_obj['id'])

            self.conn.notifies.clear()
        except psycopg2.OperationalError:
            self.display_failed_status('OperationError')
            self.loop.stop()

    def run_event_loop(self):
        self.set_autocommit()
        self.listen_events()
        self.loop = asyncio.get_event_loop()
        print('Run event loop...')
        self.loop.add_reader(self.conn, self.handle_notify)
        self.loop.run_forever()


