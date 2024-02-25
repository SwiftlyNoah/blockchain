import datetime
import hashlib
import requests
import ecdsa
from typing import List
from wallet import Wallet
from urllib.parse import urlparse

class Blockchain:
    class Transaction:
        def __init__(self, sender, recipient, amount, public_key, signature=None):
            self.sender = sender
            self.recipient = recipient
            self.amount = amount
            self.public_key = public_key
            self.signature = signature
            self.timestamp = str(datetime.datetime.now())
            self.id = self.hash_transaction()

        def transaction_data(self):
            return f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        
        def hash_transaction(self):
            return hashlib.sha256(self.transaction_data().encode()).hexdigest()
        
        def to_dict(self):
            return {
                'sender': self.sender,
                'recipient': self.recipient,
                'amount': self.amount,
                'signature': self.signature,
                'public_key': self.public_key,
                'timestamp': self.timestamp,
                'id': self.id
            }
        
        @classmethod
        def from_dict(cls, transaction_dict):
            transaction = cls(
                sender=transaction_dict['sender'],
                recipient=transaction_dict['recipient'],
                amount=transaction_dict['amount'],
                public_key=transaction_dict['public_key'],
            )
            # Not sure if timestamp will be present
            if 'signature' in transaction_dict:
                transaction.signature = transaction_dict['signature']
            if 'timestamp' in transaction_dict:
                transaction.timestamp = transaction_dict['timestamp']
            if 'id' in transaction_dict: # id can be calculated, so not neccessary to provide
                transaction.id = transaction_dict['id']
            return transaction
    
    leading_zeroes = 5

    def __init__(self, wallet: Wallet):
        self.chain = []
        self.wallet = wallet
        self.create_genesis_block(wallet.crypto_address)
        self.transaction_pool = []
        self.nodes = set()
        
    def create_genesis_block(self, address=None):
        genesis_block = {
            'block_number': 1,
            'previous_hash': 0,
            'transactions': [
                # need one transaction to kick off the chain
                self.Transaction(sender='', recipient='22CrG4hSL3UPvzGumC5aTBD8ujmn', amount=1000, public_key='', signature='').to_dict(),
                self.Transaction(sender='', recipient=address, amount=1, public_key='', signature='').to_dict()
            ]
        }
        self.mine_block(genesis_block)
        self.append_block(genesis_block)
    
    def verify_transaction_signature(self, transaction: Transaction):
        public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(transaction.public_key), curve=ecdsa.SECP256k1)
        transaction_data = transaction.transaction_data().encode()
        try:
            return public_key.verify(bytes.fromhex(transaction.signature), transaction_data)
        except ecdsa.BadSignatureError:
            return False
        
    def add_transaction(self, transaction: Transaction):
        if len(self.get_transaction_history(transaction.sender)) == 0:
            return False, "Transaction must be from a valid account"
        elif transaction.amount > self.get_balance(transaction.sender):
            return False, "Cannot afford transaction"
        elif transaction.amount <= 0:
            return False, "Amount must be positive"
        elif transaction.sender != Wallet.public_to_address(transaction.public_key):
            return False, f"Public key ({transaction.public_key}) not associated with sender address ({transaction.sender}, hash={Wallet.public_to_address(transaction.public_key)})"        
        self.transaction_pool.append(transaction)

        return True, f"Transaction {transaction.id} successfully added to pool"
    
    def get_transaction_history(self, address) -> List[Transaction]:
        transactions = []
        for block in self.chain:
            for transaction_dict in block['transactions']:
                transaction = self.Transaction.from_dict(transaction_dict)
                if transaction.sender == address or transaction.recipient == address:
                    transactions.append(transaction)

        return transactions
    
    def get_balance(self, address):
        # Calculate the balance by iterating over all transactions in the chain and the transaction pool
        balance = 0
        for transaction in self.get_transaction_history(address):
            if transaction.sender == address:
                balance -= transaction.amount
            if transaction.recipient == address:
                balance += transaction.amount
        
        for transaction in self.transaction_pool:
            if transaction.sender == address:
                balance -= transaction.amount
        
        return balance
    
    def sign_transaction(self, private_key_hex, transaction_data):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
        message = transaction_data.encode()
        signature = sk.sign(message)
        return signature.hex()
    
    def append_block(self, block): 
        self.chain.append(block)
        return block
    
    def get_previous_block(self): 
        return self.chain[-1]
    
    def create_block(self):
        previous_block = self.get_previous_block()
        new_block_number = int(previous_block['block_number']) + 1
        previous_hash = previous_block['hash']
        
        # Convert each Transaction object in the pool to dict first
        transactions_to_include = [transaction.to_dict() for transaction in self.transaction_pool]
        
        block = {
            'block_number': new_block_number,
            'previous_hash': previous_hash,
            'transactions': transactions_to_include
        }
        self.mine_block(block)
        self.append_block(block)
        # Clear the transaction pool (TODO: not use all transactions all the time)
        self.transaction_pool = []
        return block

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
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1 # ignore genesis block, thats where i get to be greedy :)
        # Temporary balance tracker dictionary to verify balances through the chain
        balances = {}

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_block(previous_block):
                return False, f"Block number {block_index + 1} has mismatching previous hash with prior blocks hash"
            block_number = block['block_number']
            hash = self.hash_block(block)
            if hash[:self.leading_zeroes] != "0" * self.leading_zeroes or block_number != block_index + 1:
                return False, f"Hash of block number {block_index + 1} does not meet leading zeroes requirement"

            # Verify each transaction in the current block
            for transaction_dict in block.get('transactions', []):
                transaction = self.Transaction.from_dict(transaction_dict)

                # Check transaction signature
                if not self.verify_transaction_signature(transaction):
                    return False, f"Invalid transaction signature for transaction {transaction.id}"
                if transaction.sender is not Wallet.public_to_address(transaction.public_key):
                    return False, f"Public key ({transaction.public_key}) not associated with sender address ({transaction.sender})"
                
                # Update sender balance and check affordability
                sender_balance = balances.get(transaction.sender, 0)
                if sender_balance < transaction.amount:
                    return False, f"Address f{transaction.sender} can not afford transaction with id: {transaction.id}"
                balances[transaction.sender] = sender_balance - transaction.amount

                # Update recipient balance
                recipient_balance = balances.get(transaction.recipient, 0) + transaction.amount
                balances[transaction.recipient] = recipient_balance

            previous_block = block
            block_index += 1

        return True, "Chain is valid"
    
    def get_transaction_status(self, transaction_id):
        # First, check if the transaction is in the transaction pool
        for transaction in self.transaction_pool:
            if transaction.id == transaction_id:
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
            if transaction.id == transaction_id:
                transaction_to_cancel = transaction
                break

        # If the transaction is not found, return a failure message
        if transaction_to_cancel is None:
            return False, "Transaction not found in the pool"

        # Remove the transaction from the transaction pool
        self.transaction_pool.remove(transaction_to_cancel)

        return True, "Transaction canceled successfully"
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False