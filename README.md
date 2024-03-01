# NoahCoin (v2)

Similar to NoahCoin v1, but with security. There is now no way to steal other users money without knowing their private key.

### Build instructions
- Install new dependency ecdsa with pip (`pip install ecdsa`) or another tool
- Clone the repo and navigate to its directory
- Checkout the `noah/crypto-project` branch
- Change directory with `cd crypto/currency/scripts`
- Make files executable with `chmod +x run.sh stop.sh`
- Run the code with `./run.sh`. Now the flask server should be running on localhost as well as the local network on ports 5001 through 5004
- Begin calling endpoitnts. Open the Postman collection json file `noahcoinv2.postman_collection.json` in Postman and make requests there or call them another way 


### Features:
- Generate a wallet
  - Private key (32 char hex)
  - Public key (32 char hex)
  - 'NoahCoin address' (Base58 encoded 27-28 char string)
  - Static methods for step by step generation
- Make transactions
  - They must be signed with a private key. Signatures will be verified with public key.
  - Sender address must match public key of transaction
  - You cannot send a negative amount of NoahCoin or more than is currently in your account
  - Transactions can be from the miner node (call the `POST` `new_transaction_from_node` endpoint) or from another node on the network (`POST` `new_transaction` with all of the other fields)
  - **The `new_transaction_from_node` endpoint will only function if called from the local machine.** The code will check IP address, so you can steal from the miners!
- Check on transaction status
- Delete transaction in pool
- Get user account value
  - Sums up all of the transactions they have made in the chain
- Get transaction pool
- Connect node
- Get largest chain
  - Replaces local chain with the largest valid one on the network
- Check chain validity
  - Ensures users can afford all transactions, all signatures match, all transaction public keys match their senders, transaction hashes and block hashes are matched, and no data has been tampered with