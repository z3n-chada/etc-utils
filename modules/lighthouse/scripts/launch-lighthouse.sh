#!/bin/bash


DEBUG_LEVEL=$1 
TESTNET_DIR=$2
NODE_DIR=$3
ETH1_ENDPOINT=$4
IP_ADDR=$5
P2P_PORT=$6
REST_PORT=$7
HTTP_PORT=$8
TESTNET_IP_RANGE=$9


while [ ! -f "/data/testnet-ready" ]; do
    sleep 1
done

sleep 10 # wait for bootnode to come up

if [ ! -f "$TESTNET_DIR/boot_enr.yaml" ]; then
    bootnode_enr=`cat $TESTNET_DIR/../bootnode/enr.dat`
    echo "- $bootnode_enr" > $TESTNET_DIR/boot_enr.yaml
fi

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
	--eth1 --eth1-endpoints "$ETH1_ENDPOINT" \
	--http --http-port $REST_PORT \
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
	--beacon-nodes "http://localhost:$REST_PORT"
