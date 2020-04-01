import json
import functools

from hash_utils import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

# Reward given to the miners for creating new blocks
MINING_REWARD = 10


class BlockChain:
    def __init__(self, hosting_node_id):
        # Starting block of the block chain
        genesis_block = Block(0, '', [], 100)
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
                                    tx['amount'])
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
                                                      tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError) as e:
            print("File not found. " + str(e))
            print(
                "Handled exception - Initialized blockchain to Genesis block.")

    def save_data(self):
        try:
            with open('blockchain_data.txt', mode='w') as f:
                # Convert both block objs and transaction objs within each block to dicts
                saveable_chain = [
                    block.__dict__ for block in [
                        Block(block_el.index, block_el.previous_hash,
                              [tx.__dict__ for tx in block_el.transactions],
                              block_el.proof) for block_el in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print("Saving failed.")

    def proof_of_work(self):
        """
        Function to find the valid proof of work that the proof validation condition

        Returns
        -------
            proof (integer): Proof of work which satisfies condition

        """
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
        participant = self.hosting_node
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

        tx_recipient = [[
            tx.amount for tx in block.transactions
            if tx.recipient == participant
        ] for block in self.__chain]

        amount_received = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0)

        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        """
        Adds a new transaction (if valid) to the list of open transactions.

        Parameters
        ----------
            sender (String): The sender of the coins
            recipient (String): The recipient of the coins
            amount (float): The amount of coins sent in the transaction
                            (default = 1.0)
        """

        transaction = Transaction(sender, recipient, amount)

        if Verification.verify_transaction(transaction, self.get_balances):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """
        Function to mine blocks from the list of open transactions.
        Also adds a reward transaction to the miner.
        """

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        # Rewarding users who mine blocks is a way to get coins into the blockchain
        reward_transaction = Transaction('MINING', self.hosting_node,
                                         MINING_REWARD)

        # Add the reward transaction to the list of
        # open transactions before mining the block
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        self.__open_transactions.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, copied_transactions,
                      proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
