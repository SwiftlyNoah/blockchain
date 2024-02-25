#!/bin/bash

# Start 4 instances of montycoin.py on ports 5001-5004
for port in {5001..5004}
do
    python ../noahcoin_server.py --port=$port &
done