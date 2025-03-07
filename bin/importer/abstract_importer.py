#!/usr/bin/env python3
# -*-coding:UTF-8 -*
"""
Importer Class
================

Import Content

"""
import base64
import gzip
import logging
import logging.config
import os
import sys

from abc import ABC, abstractmethod


sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
# from ConfigLoader import ConfigLoader
from lib import ail_logger
from lib.ail_queues import AILQueue

logging.config.dictConfig(ail_logger.get_config(name='modules'))

# TODO Clean queue one object destruct

class AbstractImporter(ABC):  # TODO ail queues
    def __init__(self, queue=False):
        """
        AIL Importer
        :param queue: Allow to push messages to other modules
        """
        # Module name if provided else instance className
        self.name = self._name()
        self.logger = logging.getLogger(f'{self.__class__.__name__}')

        # Setup the I/O queues for one shot importers
        if queue:
            self.queue = AILQueue(self.name, 'importer_manual')

    @abstractmethod
    def importer(self, *args, **kwargs):
        """Importer function"""
        pass

    def _name(self):
        """
        Returns the instance class name (ie. the Exporter Name)
        """
        return self.__class__.__name__

    def add_message_to_queue(self, message, queue_name=None):
        """
        Add message to queue
        :param message: message to send in queue
        :param queue_name: queue or module name

        ex: add_message_to_queue(item_id, 'Mail')
        """
        if message:
            self.queue.send_message(message, queue_name)

    @staticmethod
    def b64(content):
        if isinstance(content, str):
            content = content.encode()
        return base64.b64encode(content).decode()

    @staticmethod
    def create_gzip(content):
        if isinstance(content, str):
            content = content.encode()
        return gzip.compress(content)

    def b64_gzip(self, content):
        try:
            gziped = self.create_gzip(content)
            return self.b64(gziped)
        except Exception as e:
            self.logger.warning(e)
            return ''

    def create_message(self, obj_id, content, b64=False, gzipped=False, source=None):
        if not gzipped:
            content = self.b64_gzip(content)
        elif not b64:
            content = self.b64(gzipped)
        if not content:
            return None
        if isinstance(content, bytes):
            content = content.decode()
        if not source:
            source = self.name
        self.logger.info(f'{source} {obj_id}')
        # self.logger.debug(f'{source} {obj_id} {content}')
        return f'{source} {obj_id} {content}'

