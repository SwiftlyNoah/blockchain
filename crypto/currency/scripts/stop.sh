#!/bin/bash

# Stop the instances of montycoin.py running on ports 5001-5004
for port in {5001..5004}
do
    lsof -ti tcp:$port | xargs kill -9
done