### Create a Blockchain ###

# Import Libraries

import datetime
import hashlib
import json

class Blockchain: 
    leading_zeroes = 5

    def __init__(self): 
        self.chain = []
        self.create_genesis_block()
        self.transaction_pool = []
        self.users = {
            'god': {
                'account_value': 10000,
                'transactions': []
            }
        }
        
    def create_genesis_block(self):
        genesis_block = {
            'block_number': 1,
            'previous_hash': 0,
            'transactions': []
        }
        self.mine_block(genesis_block)
        self.append_block(genesis_block)

    def append_block(self, block): 
        self.chain.append(block)
        return block
    
    def get_previous_block(self): 
        return self.chain[-1]
    
    def create_block(self):
        previous_block = self.get_previous_block()
        new_block_number = int(previous_block['block_number']) + 1
        previous_hash = previous_block['hash']
        transactions_to_include = self.transaction_pool.copy()
        block = {
            'block_number': new_block_number,
            'previous_hash': previous_hash,
            'transactions': transactions_to_include
        }
        self.mine_block(block)
        self.append_block(block)
        self.complete_transactions(transactions_to_include)
        return block
    
    def complete_transactions(self, transactions):
        for transaction in transactions:
            # Update the recipient's account value and transaction history
            recipient = transaction['recipient']
            amount = transaction['amount']
            if recipient in self.users:
                self.users[recipient]['account_value'] += amount
                self.users[recipient]['transactions'].append(transaction)

            # Update the sender's transaction history
            sender = transaction['sender']
            if sender in self.users:
                self.users[sender]['transactions'].append(transaction)

            # Remove the transaction from the transaction pool
            self.transaction_pool.remove(transaction)

    def mine_block(self, block): 
        new_nonce = 1
        temp = block
        temp['nonce'] = new_nonce
        while self.hash_block(temp)[:self.leading_zeroes] != "0" * self.leading_zeroes:
            new_nonce += 1
            temp['nonce'] = new_nonce
        block = temp
        block['hash'] = self.hash_block(block)
        return 
    
    def hash_block(self, block):
        block_number = block['block_number']
        nonce = block['nonce']
        previous_hash = block['previous_hash']
        
        transaction_ids = ''.join([tx['id'] for tx in block.get('transactions', [])])

        data = f"{block_number}{nonce}{previous_hash}{transaction_ids}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def hash_transaction(transaction):
        sender = transaction['sender']
        recipient = transaction['recipient']
        amount = transaction['amount']
        timestamp = transaction['timestamp']
        data = f"{sender}{recipient}{amount}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_block(previous_block):
                return False
            previous_hash = previous_block['hash']
            block_number = block['block_number']
            hash = self.hash_block(block)
            if hash[:self.leading_zeroes] != "0" * self.leading_zeroes or block_number != block_index + 1:
                return False
            previous_block = block
            block_index += 1
        return True
    
    def register_user(self, username):
        if username in self.users:
            return False, "Username already exists"

        # Initialize the user with account value and an empty transaction list
        self.users[username] = {
            'account_value': 0,
            'transactions': []
        }
        return True, "Username registered successfully"
    
    def add_transaction(self, transaction):
        sender = transaction['sender']
        recipient = transaction['recipient']
        amount = transaction['amount']
        if sender not in self.users or recipient not in self.users:
            return False, "Transaction must be between two valid users"
        if amount > self.users[sender]['account_value']:
            return False, "Cannot afford transaction"
        if amount <= 0:
            return False, "Amount must be positive"
        
        # valid transaction
        timestamp = str(datetime.datetime.now())
        transaction['timestamp'] = timestamp
        txid = self.hash_transaction(transaction)
        transaction['id'] = txid
        self.transaction_pool.append(transaction)
        self.users[sender]['account_value'] -= amount
        self.users[sender]['transactions'].append(transaction)
        self.users[recipient]['transactions'].append(transaction)
        if sender == 'god':
            return True, f"Transaction {txid} succesfully added to pool. {recipient} robbed {amount} NoahCoin from god"
        else:
            return True, f"Transaction {txid} succesfully added to pool"
    
    def get_transaction_status(self, transaction_id):
        # First, check if the transaction is in the transaction pool
        for transaction in self.transaction_pool:
            if transaction['id'] == transaction_id:
                return True, "Transaction is pending in the pool"

        # Next, check if the transaction is in the blockchain
        for block in self.chain:
            if any(transaction['id'] == transaction_id for transaction in block.get('transactions', [])):
                return True, "Transaction is confirmed in the blockchain"

        # If the transaction is not found in either, return an error message
        return False, "Transaction not found"

    
    def cancel_transaction(self, transaction_id):
        # Find the transaction in the pool
        transaction_to_cancel = None
        for transaction in self.transaction_pool:
            if transaction['id'] == transaction_id:
                transaction_to_cancel = transaction
                break

        # If the transaction is not found, return a failure message
        if transaction_to_cancel is None:
            return False, "Transaction not found in the pool"

        # Revert the changes made by this transaction
        sender = transaction_to_cancel['sender']
        recipient = transaction_to_cancel['recipient']
        amount = transaction_to_cancel['amount']

        # Update the account values
        self.users[sender]['account_value'] += amount

        # Remove the transaction from the users' history if it exists
        if transaction_to_cancel in self.users[sender]['transactions']:
            self.users[sender]['transactions'].remove(transaction_to_cancel)
        if transaction_to_cancel in self.users[recipient]['transactions']:
            self.users[recipient]['transactions'].remove(transaction_to_cancel)

        # Remove the transaction from the transaction pool
        self.transaction_pool.remove(transaction_to_cancel)

        return True, "Transaction canceled successfully"
        
    def print_money(self, username, amount):
        if username not in self.users:
            return False, "User not found"

        if amount <= 0:
            return False, "Amount must be greater than zero"

        self.users[username]['account_value'] += amount
        return True, f"Added {amount} to {username}'s account"


    def get_account_value(self, username):
        if username == 'god':
            return True, "God is all-powerful, all-seeing, and all-wealthy"

        # Check if the user exists
        if username not in self.users:
            return False, f"No user found with username: {username}"

        # Return the account value of the user
        return True, self.users[username]['account_value']

    def get_transaction_history(self, username):
        # Check if the user exists
        if username not in self.users:
            return False, f"No user found with username: {username}"

        # Return the transaction history of the user
        return True, self.users[username]['transactions']


# Create Web App
from flask import Flask, jsonify, request
app = Flask(__name__)

# Create Blockchain
blockchain = Blockchain()

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
    response = {
        'valid': blockchain.is_chain_valid(blockchain.chain)
    }
    return jsonify(response), 200

# Endpoint for creating a new user
@app.route('/create_user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    username = user_data.get('username')
    if not username:
        return jsonify({'message': 'Username is required'}), 400

    success, message = blockchain.register_user(username)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint for creating a new transaction
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    transaction_data = request.get_json()
    required_fields = ['sender', 'recipient', 'amount']

    if not all(field in transaction_data for field in required_fields):
        return jsonify({'message': 'Missing fields in transaction data'}), 400

    success, message = blockchain.add_transaction(transaction_data)
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

@app.route('/print_money', methods=['POST'])
def print_money():
    data = request.get_json()
    username = data.get('username')
    amount = data.get('amount')

    if not username or amount is None:
        return jsonify({'message': 'Username and amount are required'}), 400

    amount = float(amount)
    transaction = {
        'amount': amount,
        'sender': 'god',
        'recipient': username
    }

    success, message = blockchain.add_transaction(transaction)
    return jsonify({'message': message}), (200 if success else 400)

@app.route('/get_user_account_values', methods=['GET'])
def get_user_account_values():
    try:
        users_minus_god = blockchain.users.copy()
        del users_minus_god['god']
        user_account_values = {username: user['account_value'] for username, user in users_minus_god.items()}
        return jsonify(user_account_values), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/get_account_info/<username>', methods=['GET'])
def get_account_info(username):
    # Check if the user exists
    if username not in blockchain.users:
        return jsonify({'message': f"No user found with username: {username}"}), 404

    user_info = blockchain.users[username]
    account_info = {
        'account_value': user_info['account_value'],
        'transactions': user_info['transactions']
    }
    return jsonify(account_info), 200

@app.route('/get_transaction_pool', methods=['GET'])
def get_transaction_pool():
    return jsonify(blockchain.transaction_pool), 200

# Run app
app.run(host = '0.0.0.0', port = 5001)