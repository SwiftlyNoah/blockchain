### Create a Blockchain ###

# Import Libraries

import datetime
import hashlib
import json

class Blockchain: 
    leading_zeroes = 4

    def __init__(self): 
        self.chain = []
        self.create_genesis_block()
        
    def create_genesis_block(self):
        genesis_block = {
            'block_number': 1,
            'previous_hash': 0
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
        block = {
            'block_number': new_block_number,
            'previous_hash': previous_hash, 
        }
        self.mine_block(block)
        self.append_block(block)
        return block

    def mine_block(self, block): 
        new_nonce = 1
        temp = block
        temp['nonce'] = new_nonce
        while self.hash(temp)[:self.leading_zeroes] != "0" * self.leading_zeroes:
            new_nonce += 1
            temp['nonce'] = new_nonce
        block = temp
        block['hash'] = self.hash(block)
        return 
    
    def hash(self, block):
        block_number = block['block_number']
        nonce = block['nonce']
        previous_hash = int(str(block['previous_hash']), 16)
        hash = hashlib.sha256(str(nonce**2 - previous_hash**2 - block_number**2).encode()).hexdigest()
        return hash
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_hash = previous_block['hash']
            block_number = block['block_number']
            hash = self.hash(block)
            if hash[:self.leading_zeroes] != "0" * self.leading_zeroes or block_number != block_index + 1:
                return False
            previous_block = block
            block_index += 1
        return True

### Mine Blockchain

# Create Web App
from flask import Flask, jsonify
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

# Run app
app.run(host = '0.0.0.0', port = 5001)