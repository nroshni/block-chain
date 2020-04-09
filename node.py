# import os
# import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

from wallet import Wallet
from blockchain import BlockChain

app = Flask(__name__)
wallet = Wallet()
block_chain = BlockChain(wallet.public_key)
CORS(app)  # Open the App to clients running outside the server

# log_folder = os.path.join(os.getcwd(), 'logs')
# if not os.path.exists(log_folder):
#     os.makedirs(log_folder)
#
# logging.basicConfig(
#     level=logging.INFO,
#     filename=os.path.join(log_folder, "Blockchain_LOG"),
#     datefmt='%m-%d-%Y %I:%M:%S %p',
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.route('/wallet', methods=['POST'])
def create_keys():
    global block_chain
    wallet.create_keys()
    if wallet.save_keys():
        block_chain = BlockChain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': block_chain.get_balances()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Saving the keys failed'}
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    global block_chain
    if wallet.load_keys():
        block_chain = BlockChain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': block_chain.get_balances()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Loading the keys failed'}
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = block_chain.get_balances()
    if balance:
        response = {
            'message': 'Fetched balance successfully',
            'funds': balance
        }
        return jsonify(response), 200
    response = {
        'message': 'Loading balance failed',
        'wallet_setup': wallet.public_key is not None
    }
    return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {'message': 'No wallet setup'}
        return jsonify(response), 400

    user_input = request.get_json()
    if not user_input:
        response = {'message': 'No data received'}
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']
    if not all(field in user_input for field in required_fields):
        response = {'message': 'Required data is missing.'}
        return jsonify(response), 400

    recipient = user_input['recipient']
    amount = user_input['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    if block_chain.add_transaction(recipient, wallet.public_key, signature,
                                   amount):
        response = {
            'message': 'Successfully added transaction',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': block_chain.get_balances()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Creating a transaction failed.'}
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    # logging.info('Mining a new block')
    block = block_chain.mine_block()

    if block is not None:
        block_copy = block.__dict__.copy()
        block_copy['transactions'] = [
            tx.__dict__ for tx in block_copy['transactions']
        ]
        response = {
            'message': 'Block added successfully',
            'block': block_copy,
            'funds': block_chain.get_balances()
        }
        return jsonify(response), 201
    else:
        # logging.error('Mining failed.')
        response = {
            'message': 'Mining a block failed.',
            'wallet_setup': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = block_chain.get_chain()
    presentable_chain = [block.__dict__.copy() for block in chain_snapshot]
    for block in presentable_chain:
        block['transactions'] = [tx.__dict__ for tx in block['transactions']]
    # logging.info('Displaying the blockchain blocks')
    return jsonify(presentable_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
