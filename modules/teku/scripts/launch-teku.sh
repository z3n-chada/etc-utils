#!/bin/bash

DEBUG_LEVEL=$1 
TESTNET_DIR=$2
NODE_DIR=$3
ETH1_ENDPOINT=$4
IP_ADDR=$5
P2P_PORT=$6
REST_PORT=$7
HTTP_PORT=$8

if [ ! -f "/data/testnet-ready" ]; then
    sleep 1
fi

sleep 10 # wait for bootnode to come up

bootnode_enr=`cat $TESTNET_DIR/../bootnode/enr.dat`
echo $bootnode_enr
# beacon node
teku --network "$TESTNET_DIR/config.yaml" \
    --data-path "$NODE_DIR" \
    --p2p-enabled=true \
    --logging="$DEBUG_LEVEL" \
    --initial-state "$TESTNET_DIR/genesis.ssz" \
    --eth1-endpoint "$ETH1_ENDPOINT" \
    --p2p-discovery-bootnodes="$bootnode_enr" \
    --metrics-enabled=true \
    --metrics-interface=0.0.0.0 \
    --metrics-port="$HTTP_PORT" \
    --metrics-host-allowlist="*" \
    --p2p-discovery-enabled=true \
    --p2p-advertised-ip="$IP_ADDR" \
    --p2p-peer-lower-bound=1 \
    --p2p-port="$P2P_PORT" \
    --p2p-advertised-port="$P2P_PORT" \
    --p2p-advertised-udp-port="$P2P_PORT" \
    --rest-api-enabled=true \
    --rest-api-docs-enabled=true \
    --rest-api-interface=0.0.0.0 \
    --rest-api-port="$REST_PORT" \
    --rest-api-host-allowlist="*" \
    --metrics-host-allowlist="*" &

sleep 15

teku vc \
    --network "$TESTNET_DIR/config.yaml" \
    --data-path "$NODE_DIR" \
    --beacon-node-api-endpoint "http://localhost:$REST_PORT" \
    --validators-graffiti="hello" \
    --validator-keys "$NODE_DIR/keys:$NODE_DIR/secrets"
