import logging
from time import time
from utils.printable import Printable

logger = logging.getLogger(__name__)


class Block(Printable):
    def __init__(self,
                 index,
                 previous_hash,
                 transactions,
                 proof,
                 timestamp=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = timestamp
        logger.info('Initializing Block: {}'.format(self.__dict__))
