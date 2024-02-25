from flask import Flask, jsonify, request
import argparse
from wallet import Wallet
from noahcoin_blockchain import Blockchain

# Create Web App
app = Flask(__name__)

# Create Blockchain
wallet = Wallet()
blockchain = Blockchain(wallet)

# Mine a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    block = blockchain.create_block()
    response = {
        'message': 'Congratulations, you just mined a block!',
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'hash': block['hash'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

# Get a full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# Confirm chain is valid
@app.route('/confirm_chain', methods = ['GET'])
def confirm_chain():
    success, message = blockchain.is_chain_valid(blockchain.chain)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint for creating a new transaction
@app.route('/new_transaction_from_node', methods=['POST'])
def new_transaction_from_node():
     # Check if the request is from the local machine
    if request.remote_addr not in ['127.0.0.1', '::1']: # [ipv4 and ipv6 addresses for localhost]
        return jsonify({'message': 'Access denied'}), 403
    
    transaction_data = request.get_json()
    required_fields = ['recipient', 'amount']

    if not all(field in transaction_data for field in required_fields):
        return jsonify({'message': 'Missing fields in transaction data'}), 400

    transaction_data['sender'] = wallet.crypto_address
    transaction_data['public_key'] = wallet.public_key
    transaction = Blockchain.Transaction.from_dict(transaction_data)
    transaction.signature = blockchain.sign_transaction(wallet.private_key, transaction_data=transaction.transaction_data())

    success, message = blockchain.add_transaction(transaction)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint for creating a new transaction
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    transaction_data = request.get_json()
    required_fields = ['sender', 'recipient', 'amount', 'signature', 'public_key']
    if not all(field in transaction_data for field in required_fields):
        return jsonify({'message': 'Missing fields in transaction data'}), 400

    transaction = Blockchain.Transaction.from_dict(transaction_data)
    success, message = blockchain.add_transaction(transaction)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint for checking the status of a transaction
@app.route('/transaction_status/<transaction_id>', methods=['GET'])
def transaction_status(transaction_id):
    success, message = blockchain.get_transaction_status(transaction_id)
    return jsonify({'message': message}), (200 if success else 404)

# Endpoint for canceling a transaction
@app.route('/cancel_transaction/<transaction_id>', methods=['DELETE'])
def cancel_transaction(transaction_id):
    success, message = blockchain.cancel_transaction(transaction_id)
    return jsonify({'message': message}), (200 if success else 404)

@app.route('/get_transaction_pool', methods=['GET'])
def get_transaction_pool():
    return jsonify([transaction.to_dict() for transaction in blockchain.transaction_pool]), 200

@app.route('/get_balance', methods=['GET'])
def get_balance():
    address = request.args.get('address')
    if not address:
        return jsonify({'message': 'Address parameter is missing'}), 400
    
    balance = blockchain.get_balance(address)
    return jsonify({'address': address, 'balance': balance}), 200

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The NoahCoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
# Replacing the chain by the longest chain if needed
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Local chain was replaced by a larger valid chain.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. Local chain is the largest valid chain.',
                    'new_chain': blockchain.chain}
    return jsonify(response), 200

@app.route('/make_wallet', methods=['GET'])
# Replacing the chain by the longest chain if needed
def make_wallet():
    wallet = Wallet()
    response = {
        'private_key': wallet.private_key,
        'public_key': wallet.public_key,
        'noahcoin_address': wallet.crypto_address
    }
    return jsonify(response), 200
    
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=5001, help='port to listen on')
args = parser.parse_args()

# Running the app
app.run(host='0.0.0.0', port=args.port)

