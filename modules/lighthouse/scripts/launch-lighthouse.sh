#!/bin/bash
# args: <datadir> <network-port> <http-port> <enr-address>

TESTNET_DIR=$1
NODE_DATADIR=$2
WEB3_PROVIDER=$3
TCP_PORT=$4
METRIC_PORT=5000

sleep 10 # wait for bootnode to come up

bootnode_enr=`cat /data/local_testnet/bootnode/enr.dat`
echo "- $bootnode_enr" > $TESTNET_DIR/boot_enr.yaml

lighthouse \
	--debug-level debug \
	bn \
	--datadir $NODE_DATADIR \
	--testnet-dir $TESTNET_DIR \
	--staking \
    --boot-nodes "$bootnode_enr" \
    --enr-udp-port $TCP_PORT \
    --enr-tcp-port $TCP_PORT \
    --port $TCP_PORT \
	--http-port $METRIC_PORT \
	--eth1-endpoints http://10.0.20.2:8545 \
	--http-address 0.0.0.0 \
	--http-allow-origin "*"

#--enr-address "$TESTNET_DIR/boot_enr.yaml" \
