import json

from kafka import KafkaProducer
from rtmbot.core import Plugin

import datetime


class Token(object):
    valid_tokens = ['git', 'svn', 'kibana', 'jira', 'confluence',
                    'hi', 'hello', 'good', 'evening', 'morning', 'afternoon',
                    'adduser', 'addrepo', 'addpermission', 'addproject',
                    'help']

    def __init__(self, word):
        self.me = word.strip()

    def __str__(self):
        return str(self.me)

    def __repr__(self):
        return str(self.me)

    def __contains__(self, item):
        return item in self.valid_tokens

    @classmethod
    def tokenize_command_subcommand(cls, text):
        words = [w.lower().replace('!', '') for w in text.split(' ') if w.strip()]
        for word in words[:2]:
            if word in cls(word):
                yield word


class DevopsPlugin(Plugin):
    topic = 'chat-bot-topic-devops'
    users_white_list = ['U8LTWHG67']
    token_class = Token

    def ingest(self, key, value):
        value['ts'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%s')
        producer = KafkaProducer(bootstrap_servers='10.10.114.174:9092',
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(self.topic, key=key, value=value)
        producer.flush()
        producer.close()
