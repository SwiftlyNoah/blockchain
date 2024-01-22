# Noah's Blockchain (NoahCoin)

To start the blockchain application:
1. Navigate to the project directory in the terminal.
2. Run the command `python blockchain.py` to start the Flask server.
3. The server will start on `localhost` and on your local network at port `5001`.

## Features/Functionality
- Create user
- Create transaction
- View transaction status (in pool/mined)
- Cancel transaction
- Mine block - find a golden hash and process transactions in the pool
- Get chain
- Confirm chain validity - ensure the chain is valid (it always should be because their you are the honorable central authority)
- Get transaction pool
- Get user account values (see who has all of the NoahCoin)
- Get account info (account value and transactions for one specific user)
- A fixed amount of currency (10k) that begins in an account known as god
- A fixed hash difficulty (five leading zeroes)
- Print money (add some NoahCoin to a users account from god)

## Using Postman to Interact with the Blockchain
Postman can be used to interact with the NoahCoin blockchain via HTTP requests. Download the [Postman Collection json file](blockchain.postman_collection.json) and open it in the Postman app.