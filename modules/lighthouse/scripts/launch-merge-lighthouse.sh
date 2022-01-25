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
NETWORK_ID=${10}
GETH_HTTP_PORT=${11}


GETH_DATA_DIR="$NODE_DIR/geth"
GENESIS_CONFIG="$TESTNET_DIR/../../eth1-genesis.json"

while [ ! -f "/data/testnet-ready" ]; do
    sleep 1
done

sleep 5

ENODE=$(python3 /data/scripts/geth-get-enr.py --docker --config /data/testnet-config.yaml)
echo "$ENODE"
echo "$TESTNET_IP_RANGE"
geth init \
    --datadir $GETH_DATA_DIR \
    $GENESIS_CONFIG
# start local geth
geth \
    --catalyst \
    --networkid $NETWORK_ID \
    --nat "extip:$IP_ADDR" \
    --http --http.port "$GETH_HTTP_PORT" \
    --netrestrict "$TESTNET_IP_RANGE" \
    --datadir $GETH_DATA_DIR \
    --bootnodes "$ENODE" &

sleep 5 # wait for bootnode to come up

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
	--enr-address "$IP_ADDR" --enr-udp-port $P2P_PORT \
	--enr-tcp-port $P2P_PORT \
	--port $P2P_PORT \
    --boot-nodes="$bootnode_enr" \
	--eth1 --eth1-endpoints "http://127.0.0.1:$GETH_HTTP_PORT" \
	--http --http-port $REST_PORT --http-address 0.0.0.0 \
    --http-allow-origin "*" \
    --merge --http-allow-sync-stalled --disable-packet-filter \
    --execution-endpoints="http://127.0.0.1:8545" --terminal-total-difficulty-override=5000000000 &

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
