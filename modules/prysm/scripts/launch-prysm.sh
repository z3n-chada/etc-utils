#!/bin/bash 

TESTNET_DIR=$1
NODE_DATADIR=$2
WEB3_PROVIDER=$3
DEPOSIT_CONTRACT=$4
IP_ADDR=$5
P2P_PORT=$6
REST_PORT=$7
HTTP_PORT=$8

while [ ! -f "/data/testnet-ready" ]; do
    sleep 1
done

sleep 10

/git/bin/beacon-chain --accept-terms-of-use \
    --datadir "$NODE_DATADIR" \
    --contract-deployment-block=0 \
    --verbosity=debug \
    --chain-config-file="$TESTNET_DIR/config.yaml" \
    --genesis-state="$TESTNET_DIR/genesis.ssz" \
    --http-web3provider="$WEB3_PROVIDER" \
    --bootstrap-node="$(< /data/local_testnet/bootnode/enr.dat)" \
    --p2p-allowlist="10.0.20.0/16" \
    --deposit-contract=$DEPOSIT_CONTRACT \
    --p2p-host-ip="$IP_ADDR" \
    --p2p-tcp-port="$P2P_PORT" \
    --grpc-gateway-host "0.0.0.0" --grpc-gateway-port "$REST_PORT" &

sleep 20

/git/bin/validator \
    --accept-terms-of-use \
    --chain-config-file="$TESTNET_DIR/config.yaml" \
    --datadir=$NODE_DATADIR \
    --wallet-dir=$NODE_DATADIR \
    --wallet-password-file "$TESTNET_DIR/wallet-password.txt" \
    --verbosity=debug
