import json
import pickle
import functools

from hash_utils import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

# Reward given to the miners for creating new blocks
MINING_REWARD = 10

# Initializing the blockchain
block_chain = []
open_transactions = []
owner = 'Roshni'


def load_data():
    global block_chain, open_transactions
    try:
        with open('blockchain_data.txt', mode='r') as f:
            file_content = f.readlines()

            # Load block chain as OrderedDicts as hashing is performed on OrderedDict
            block_chain = json.loads(file_content[0][:-1])
            updated_block_chain = []
            for block in block_chain:
                ordered_tx = [
                    Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    for tx in block['transactions']
                ]
                updated_block = Block(block['index'], block['previous_hash'],
                                      ordered_tx, block['proof'],
                                      block['timestamp'])
                updated_block_chain.append(updated_block)
            block_chain = updated_block_chain

            # Load Open transactions as OrderedDicts as hashing is performed on OrderedDict
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'],
                                                  tx['recipient'],
                                                  tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except (IOError, IndexError) as e:
        print("File not found. " + str(e))
        print("Initializing blockchain.")
        # First block/ Starting block of the block chain
        genesis_block = Block(0, '', [], 100)
        block_chain = [genesis_block]
        open_transactions = []


def save_data():
    try:
        with open('blockchain_data.txt', mode='w') as f:
            # Convert both block objs and transaction objs within each block to dicts
            saveable_chain = [
                block.__dict__ for block in [
                    Block(block_el.index, block_el.previous_hash,
                          [tx.__dict__
                           for tx in block_el.transactions], block_el.proof)
                    for block_el in block_chain
                ]
            ]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))
    except IOError:
        print("Saving failed.")


def load_data_pickle():
    global block_chain, open_transactions

    with open('blockchain_data.pkl', mode='rb') as f:
        file_content = pickle.loads(f.read())
        block_chain = file_content['block_chain']
        open_transactions = file_content['open_tx']


def save_data_pickle():
    with open('blockchain_data.pkl', mode='wb') as f:
        content = {'block_chain': block_chain, 'open_tx': open_transactions}
        f.write(pickle.dumps(content))


def proof_of_work():
    """
    Function to find the valid proof of work that the proof validation condition

    Returns
    -------
        proof (integer): Proof of work which satisfies condition

    """
    last_block = block_chain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    verifier = Verification()
    while not verifier.valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balances(participant):
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
    tx_sender = [[
        tx.amount for tx in block.transactions if tx.sender == participant
    ] for block in block_chain]

    open_tx_sender = [
        tx.amount for tx in open_transactions if tx.sender == participant
    ]

    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt),
                                   tx_sender, 0)

    tx_recipient = [[
        tx.amount for tx in block.transactions if tx.recipient == participant
    ] for block in block_chain]

    amount_received = functools.reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0)

    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain """
    if len(block_chain) < 1:
        return None
    return block_chain[-1]


def verify_transaction(transaction):
    """
    Function that validates if a given transaction is valid based on
    the amount of funds the sender of the transaction has

    Parameters
    ----------
        transaction (dict): A transaction containing the sender,
                            recipient and the transaction amount

    Returns
    -------
        True (Boolean): If the transaction is valid
        False (Boolean): If the transaction is invalid
    """
    sender_balance = get_balances(transaction.sender)
    if transaction.amount > sender_balance:
        return False
    return True


def add_transaction(recipient, sender=owner, amount=1.0):
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
    verifier = Verification()
    if verifier.verify_transaction(transaction, get_balances):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    """
    Function to mine blocks from the list of open transactions.
    Also adds a reward transaction to the miner.
    """
    global open_transactions
    last_block = block_chain[-1]
    hashed_block = hash_block(last_block)

    proof = proof_of_work()

    # Rewarding users who mine blocks is a way to get coins into the blockchain
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)

    # Add the reward transaction to the list of
    # open transactions before mining the block
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    # open_transactions.append(reward_transaction)

    block = Block(len(block_chain), hashed_block, copied_transactions, proof)
    block_chain.append(block)
    open_transactions = []
    save_data()


def get_transaction_values():
    """ Returns the input of the user transaction amount as a float """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice:')
    return user_input


def print_blockchain_elements():
    for block in block_chain:
        print(f'Block Value : {block}')


waiting_for_input = True
load_data()

while waiting_for_input:
    print(f'#' * 20)
    print('Please choose:')
    print(f'1: Add a new transaction value')
    print(f'2: Output the blockchain blocks')
    print(f'3: Mine a new block')
    print(f'4: Check transaction validity')
    print(f'q: Quit')
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_value = get_transaction_values()
        tx_recipient, tx_amount = tx_value
        if add_transaction(tx_recipient, amount=tx_amount):
            print("Added Transaction")
        else:
            print("Transaction Failed")
        print(f'Open transactions : {open_transactions}')
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == '3':
        mine_block()
    elif user_choice == '4':
        verifier = Verification()
        if verifier.verify_transactions(open_transactions, get_balances):
            print('All transactions are valid')
        else:
            print('There exists invalid transactions')
    elif user_choice == 'q' or user_choice == 'Q':
        waiting_for_input = False
    else:
        print('Invalid input, please pick an option from the list!')

    verifier = Verification()
    if not verifier.verify_chain(block_chain):
        print("Block chain - INVALIDATED")
        break

    print(f'Balance of  {owner} : {get_balances(owner):.2f}')
else:
    print('** User exited **')
print(f'Final Blockchain : {block_chain}')
