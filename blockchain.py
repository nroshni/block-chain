import sys

MINING_REWARD = 10

# Initializing the very first block of the block chain
genesis_block = {'previous_hash': '', 'index': 0, 'transactions': []}
block_chain = [genesis_block]
open_transactions = []
owner = 'Roshni'
participants = set([owner])


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_balances(participant):
    tx_sender = [[
        tx['amount'] for tx in block['transactions']
        if tx['sender'] == participant
    ] for block in block_chain]
    open_tx_sender = [
        tx['amount'] for tx in open_transactions if tx['sender'] == participant
    ]
    tx_sender.append(open_tx_sender)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += tx[0]

    tx_recipient = [[
        tx['amount'] for tx in block['transactions']
        if tx['recipient'] == participant
    ] for block in block_chain]

    amount_received = 0
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_received += tx[0]

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
    transaction (dict): A transaction containing the sender, recipient and the transaction amount

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
    Adds a new transaction to the list of open transactions.

    Arguments:
        :sender (String): The sender of the coins
        :recipient (String): The recipient of the coins
        :amount (float): The amount of coins sent with the transaction (default = 1.0)
    """
    transaction = {"sender": sender, "recipient": recipient, "amount": amount}
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    """
    Function to mine blocks from the list of open transactions
    """
    global open_transactions
    last_block = block_chain[-1]
    hashed_block = hash_block(last_block)

    # Rewarding users who mine blocks is a way the coins get into the blockchain
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }

    # Add thie transaction to the list of open transactions before mining the block
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    open_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(block_chain),
        'transactions': copied_transactions
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
            continue  # No need to validate as the 1st block is always the genesis block
        if block['previous_hash'] != hash_block(block_chain[index - 1]):
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print(f'#' * 20)
    print('Please choose:')
    print(f'1: Add a new transaction value')
    print(f'2: Output the blockchain blocks')
    print(f'3: Mine a new block')
    print(f'4: Output participants in the blockchain')
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

    print(f'User balance : {owner} = {get_balances(owner)}')
else:
    print('** User exited **')
print(f'Final Blockchain : {block_chain}')
# empty comment
