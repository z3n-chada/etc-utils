#!/bin/bash

sleep 10 # wait for bootnode to come up

# lighthouse \
# 	--debug-level debug \
# 	bn \
# 	--datadir $NODE_DATADIR \
# 	--testnet-dir $TESTNET_DIR \
# 	--staking \
#     --boot-nodes "$bootnode_enr" \
#     --enr-address "$TESTNET_DIR/boot_enr.yaml" \
#     --enr-udp-port $TCP_PORT \
#     --enr-tcp-port $TCP_PORT \
#     --port $TCP_PORT \
# 	--http-port $METRIC_PORT \
# 	--eth1-endpoints http://10.0.20.2:8545 \
# 	--http-address 0.0.0.0 \
# 	--http-allow-origin "*"

DEBUG_LEVEL=$1 
TESTNET_DIR=$2
NODE_DIR=$3
P2P_PORT=$4
API_PORT=$5
IP_ADDR=$6
ETH1_ENDPOINT=$7

bootnode_enr=`cat $TESTNET_DIR/../bootnode/enr.dat`
echo "- $bootnode_enr" > $TESTNET_DIR/boot_enr.yaml

lighthouse \
	--datadir $NODE_DIR \
	--debug-level $DEBUG_LEVEL \
	bn \
	--testnet-dir $TESTNET_DIR \
	--staking \
	--enr-address "$IP_ADDR" \
	--enr-udp-port $P2P_PORT \
	--enr-tcp-port $P2P_PORT \
	--port $P2P_PORT \
	--http --http-port $API_PORT \
	--eth1 --eth1-endpoints "$ETH1_ENDPOINT" \
	--http-address 0.0.0.0 \
	--http-allow-origin "*" &

sleep 10
lighthouse \
	--datadir $NODE_DIR \
	--debug-level $DEBUG_LEVEL \
	vc \
	--testnet-dir $TESTNET_DIR \
    --validators-dir "$NODE_DIR/keys" \
    --secrets-dir "$NODE_DIR/secrets" \
	--init-slashing-protection \
	--beacon-nodes "http://localhost:$API_PORT"
