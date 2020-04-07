from flask import Flask, jsonify
from flask_cors import CORS

from wallet import Wallet
from blockchain import BlockChain

app = Flask(__name__)
wallet = Wallet()
block_chain = BlockChain(wallet.public_key)
CORS(app)  # Open the App to clients running outside the server


@app.route('/', methods=['GET'])
def get_ui():
    return 'This works'


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = block_chain.get_chain()
    presentable_chain = [block.__dict__.copy() for block in chain_snapshot]
    for block in presentable_chain:
        block['transactions'] = [tx.__dict__ for tx in block['transactions']]
    return jsonify(presentable_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
