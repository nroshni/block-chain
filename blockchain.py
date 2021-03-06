import json
import logging
import functools

from block import Block
from transaction import Transaction
from utils.hash_utils import hash_block
from utils.verification import Verification
from wallet import Wallet
# Reward given to the miners for creating new blocks
MINING_REWARD = 10
logger = logging.getLogger(__name__)


class BlockChain:
    def __init__(self, hosting_node_id):
        # Starting block of the block chain
        genesis_block = Block(0, '', [], 100, 0)
        # Initializing the blockchain
        self.__chain = [genesis_block]
        # Handling open transactions
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def get_chain(self):
        # Passing a reference as the original block chain
        # shouldn't be altered when used in other functions
        return self.__chain[:]

    def get_open_transactions(self):
        # Passing a reference as the original list of open transactions
        # shouldn't be altered when used in other functions
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain_data.txt', mode='r') as f:
                file_content = f.readlines()

                # Load block chain as OrderedDicts as hashing is performed on OrderedDict
                block_chain = json.loads(file_content[0][:-1])
                updated_block_chain = []
                for block in block_chain:
                    ordered_tx = [
                        Transaction(tx['sender'], tx['recipient'],
                                    tx['signature'], tx['amount'])
                        for tx in block['transactions']
                    ]
                    updated_block = Block(block['index'],
                                          block['previous_hash'], ordered_tx,
                                          block['proof'], block['timestamp'])
                    updated_block_chain.append(updated_block)
                self.__chain = updated_block_chain

                # Load Open transactions as OrderedDicts as hashing is performed on OrderedDict
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'],
                                                      tx['recipient'],
                                                      tx['signature'],
                                                      tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError) as e:
            print("File not found. " + str(e))
            print(
                "Handled exception - Initialized blockchain to Genesis block.")

    def save_data(self):
        logger.info('Saving block chain state.')
        try:
            with open('blockchain_data.txt', mode='w') as f:
                # Convert both block objs and transaction objs within each block to dicts
                saveable_chain = [
                    block.__dict__ for block in [
                        Block(block_el.index, block_el.previous_hash,
                              [tx.__dict__ for tx in block_el.transactions],
                              block_el.proof, block_el.timestamp)
                        for block_el in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                logger.info(f'Saving open transactions: {saveable_tx}')
                f.write(json.dumps(saveable_tx))
        except IOError:
            logger.error("Saving failed.")

    def proof_of_work(self):
        """
        Function to find the valid proof of work that the proof validation condition

        Returns
        -------
            proof (integer): Proof of work which satisfies condition

        """
        logger.info('Finding proof of work')
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash,
                                           proof):
            proof += 1
        return proof

    def get_balances(self):
        """
        Returns the fund balance of the participant based on the amounts received
        (from processed transactions) and the amounts sent (from both processed
        and open transactions)
        Parameters
        ----------
            participant (string): The sender's name

        Returns
        -------
            balance funds (float): The balance fund of the participant
        """
        if self.hosting_node is None:
            return None

        participant = self.hosting_node

        logger.info(f'Computing Fund balance of user {participant }')

        tx_sender = [[
            tx.amount for tx in block.transactions if tx.sender == participant
        ] for block in self.__chain]

        open_tx_sender = [
            tx.amount for tx in self.__open_transactions
            if tx.sender == participant
        ]

        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_sender, 0)

        logger.debug(
            f'Total amounts sent (processed + open transactions) : {amount_sent}'
        )

        tx_recipient = [[
            tx.amount for tx in block.transactions
            if tx.recipient == participant
        ] for block in self.__chain]

        amount_received = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0)

        logger.debug(
            f'Total amounts received (processed transactions) : {amount_received}'
        )

        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """
        Adds a new transaction (if valid) to the list of open transactions.

        Parameters
        ----------
            sender (String): The sender of the coins
            recipient (String): The recipient of the coins
            amount (float): The amount of coins sent in the transaction
                            (default = 1.0)
        """
        if self.hosting_node is None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balances):
            logger.info(
                'Valid transaction. Adding to list of open transactions.')
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """
        Function to mine blocks from the list of open transactions.
        Also adds a reward transaction to the miner.
        """
        if self.hosting_node is None:
            logger.warning('No wallet available.')
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        logger.debug(f'Computed hash of previous block: {hashed_block}')

        proof = self.proof_of_work()
        logger.debug(f'Found valid proof: {proof}')

        # Rewarding users who mine blocks is a way to get coins into the blockchain
        logger.info('Creating Mining Reward Transaction')
        reward_transaction = Transaction('MINING', self.hosting_node, '',
                                         MINING_REWARD)

        # Add the reward transaction to the list of
        # open transactions before mining the block
        copied_transactions = self.__open_transactions[:]

        # Verify Transaction signatures before awarding the mining reward
        for tx in copied_transactions:
            if not Wallet.verify_transaction_signature(tx):
                logger.warning('Invalid transaction signatures in the block')
                return None

        copied_transactions.append(reward_transaction)
        self.__open_transactions.append(reward_transaction)

        logger.debug('Creating new block with all open + reward transactions')
        block = Block(len(self.__chain), hashed_block, copied_transactions,
                      proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
