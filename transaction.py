import logging
from collections import OrderedDict
from utils.printable import Printable

logger = logging.getLogger(__name__)


class Transaction(Printable):
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        logger.info('Initializing transaction: {}'.format(self.__dict__))

    def to_ordered_dict(self):
        """
        Returns ordered dict of the transaction for consistent hashing
        """
        return OrderedDict([('sender', self.sender),
                            ('recipient', self.recipient),
                            ('amount', self.amount)])
