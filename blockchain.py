import hashlib
import functools
from collections import OrderedDict

from hash_utils import hash_block, hash_string_sha256

# Reward given to the miners for creating new blocks
MINING_REWARD = 10

# First block/ Starting block of the block chain
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
# Initializing the blockchain
block_chain = [genesis_block]
open_transactions = []
owner = 'Roshni'
# Registered participants of the blockchain (senders/ receivers)
participants = set([owner])


def valid_proof(transactions, previous_hash, proof):
    guess = (str(transactions) + str(previous_hash) + str(proof)).encode()
    guessed_hash = hash_string_sha256(guess)

    print(f'Guessed hash : {guessed_hash}')
    return guessed_hash[0:2] == '00'


def proof_of_work():
    last_block = block_chain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
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
        tx['amount'] for tx in block['transactions']
        if tx['sender'] == participant
    ] for block in block_chain]

    open_tx_sender = [
        tx['amount'] for tx in open_transactions if tx['sender'] == participant
    ]

    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt),
                                   tx_sender, 0)

    tx_recipient = [[
        tx['amount'] for tx in block['transactions']
        if tx['recipient'] == participant
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
    :True (Boolean): If the transaction is valid
    :False (Boolean): If the transaction is invalid
    """
    sender_balance = get_balances(transaction['sender'])
    if transaction['amount'] > sender_balance:
        return False
    return True


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Adds a new transaction (if valid) to the list of open transactions.

    Arguments:
        :sender (String): The sender of the coins
        :recipient (String): The recipient of the coins
        :amount (float): The amount of coins sent in the transaction
                        (default = 1.0)
    """
    # transaction = {"sender": sender, "recipient": recipient, "amount": amount}
    # Creating a ordered dictionary as Dicts are out of order and
    # we need them to be ordered when calculating hashes. Differently
    # ordered dicts create different hashes.
    transaction = OrderedDict([('sender', sender), ('recipient', recipient),
                               ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
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
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    # Creating a ordered dictionary as Dicts are out of order and
    # we need them to be ordered when calculating hashes. Differently
    # ordered dicts create different hashes.
    reward_transaction = OrderedDict([('sender', 'MINING'),
                                      ('recipient', owner),
                                      ('amount', MINING_REWARD)])

    # Add the reward transaction to the list of
    # open transactions before mining the block
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    open_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(block_chain),
        'transactions': copied_transactions,
        'proof': proof
    }
    block_chain.append(block)
    open_transactions = []


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


def verify_chain():
    """
    Function to verify if the current blockchain is valid.
    Returns
    -------
    True (Boolean): If blockchain is valid
    False (Boolean): If blockchain is invalid
    """
    for index, block in enumerate(block_chain):
        if index == 0:
            # No need to validate as the 1st block is always the genesis block
            continue
        if block['previous_hash'] != hash_block(block_chain[index - 1]):
            return False
        # Eliminate the reward transaction when checking if the proof is a valid
        # proof that would satisfy the given hash condition
        if not valid_proof(block['transactions'][:-1], block['previous_hash'],
                           block['proof']):
            print('Proof of work is invalid')
            return False

    return True


def verify_transactions():
    """ Function to verify if all the open transactions are valid """
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print(f'#' * 20)
    print('Please choose:')
    print(f'1: Add a new transaction value')
    print(f'2: Output the blockchain blocks')
    print(f'3: Mine a new block')
    print(f'4: Output participants in the blockchain')
    print(f'5: Check transaction validity')
    print(f'q: Quit')
    print(f'h(hack): Manipulate the blockchain')
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
        print(f'Blockchain participants : {participants}')
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There exists invalid transactions')
    elif user_choice == 'q' or user_choice == 'Q':
        waiting_for_input = False
    elif user_choice == "h":
        if len(block_chain) >= 1:
            block_chain[0] = {
                "previous_hash":
                "",
                "index":
                0,
                "transactions": [{
                    "sender": "Ajay",
                    "recipient": "Anantha",
                    "amount": 125
                }]
            }
    else:
        print('Invalid input, please pick an option from the list!')

    if not verify_chain():
        print("Block chain - INVALIDATED")
        break

    print(f'Balance of  {owner} : {get_balances(owner):.2f}')
else:
    print('** User exited **')
print(f'Final Blockchain : {block_chain}')
