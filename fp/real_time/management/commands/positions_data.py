# -*- coding: UTF-8 -*-
import signal
import sys
import traceback
import time
import logging
import json
import channels.layers
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from redis.exceptions import ConnectionError
from django.core.management.base import BaseCommand
from django.conf import settings
from django_redis import get_redis_connection
import asyncio
from datetime import datetime


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Opens a connection to Redis and listens for messages, and then whenever it gets one, sends the message onto a channel in the Django channel system'

    def add_arguments(self, parser):
        parser.add_argument("channel", help='pubsub channel to submit (example: "acqvel_broadcast")')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signal.signal(signal.SIGINT, signal_handler)
        self.logger = logger or logging.getLogger(__name__)

    def set_logger(self, verbosity):
        """
        Set logger level based on verbosity option
        """
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s| %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if verbosity == 0:
            self.logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            self.logger.setLevel(logging.INFO)
        elif verbosity > 1:
            self.logger.setLevel(logging.DEBUG)

        # verbosity 3: also enable all logging statements that reach the root logger
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)

    def handle(self, *args, **options):
        self.set_logger(options.get('verbosity'))
        self.channel = options.get('channel')
        self.db = 2
        self.logger.info('Initializing redis listener...[subscribing channel: "%s"]' % self.channel)
        self.redis = None
        self.pubsub = None
        self.loop()

    def connect(self):
        while True:
            self.logger.debug('Trying to connect to redis ...')
            try:
                self.redis = get_redis_connection()
                self.redis.ping()
            except (ConnectionError, ConnectionRefusedError):
                time.sleep(1)
            else:
                break
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel,self.db)
        self.logger.info('Connected to redis.')

    def loop(self):
        self.connect()
        while True:
            try:
                for item in self.pubsub.listen():
                    
                    if item['type'] == 'message':
                        data = json.loads(item['data'].decode('utf-8'))
                        self.broadcast_message(data)

            except ConnectionError:
                self.logger.error('Lost connections to redis.')
                self.connect()

    def broadcast_message(self, data):
        self.logger.info('Broadcast message: timestamp=%s' % (
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        ))
        loop = asyncio.get_event_loop()
        channel_layer = channels.layers.get_channel_layer()
        coroutine =channel_layer.group_send(
            'real_time_data', {
                "type": 'position_message',
                "text": data,
            })
        loop.run_until_complete(coroutine)

def signal_handler(signal, frame):
    sys.exit(0)
