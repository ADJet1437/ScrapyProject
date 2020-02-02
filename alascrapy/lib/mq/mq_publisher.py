# -*- coding: utf-8 -*-

from alascrapy.lib.mq.mq_object import MQObject

import pika
import json
import socket

class MQPublisher(MQObject):
    
    def publish_message(self, json_message, exchange, routing_key):
        while True:
            if self._connection.is_open:
                message = json.dumps(json_message, indent=4)
                self._channel.basic_publish( exchange=exchange,
                                             routing_key=routing_key,
                                             body=message,
                                             properties=pika.BasicProperties(content_type='application/json',
                                                                             delivery_mode=1)
                                        )

                self.logger.info('Message published: "%s"' % message)
                break
            else:
                self.logger.info('Connection lost. Trying to reconnect')
                self.reconnect()

    def send_load_message(self, filenames):
        exchange = self.project_conf.get("LOAD", "exchange")
        routing_key = self.project_conf.get("LOAD", "routing_key")
        server_name = socket.gethostname()
        message = {"host": server_name,
                   "files": filenames}
        self.publish_message(message, exchange, routing_key)


