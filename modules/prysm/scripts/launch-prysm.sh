#!/bin/bash 

TESTNET_DIR=$1
NODE_DATADIR=$2
WEB3_PROVIDER=$3
DEPOSIT_CONTRACT=$4
IP_ADDR=$5
TCP_PORT=$6

sleep 10
echo '/git/bin/beacon-chain --accept-terms-of-use \
    --datadir "$NODE_DATADIR" \
    --contract-deployment-block=0 \
    --verbosity=debug \
    --chain-config-file="$TESTNET_DIR/config.yaml" \
    --genesis-state="$TESTNET_DIR/genesis.ssz" \
    --http-web3provider="$WEB3_PROVIDER" \
    --bootstrap-node="$(< /data/local_testnet/bootnode/enr.dat)" \
    --p2p-allowlist="10.0.20.0/16" \
    --deposit-contract=$DEPOSIT_CONTRACT_ADDRESS \
    --p2p-host-ip="$IP_ADDR" \
    --p2p-tcp-port="$TCP_PORT"'

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
    --p2p-tcp-port="$TCP_PORT" &

sleep 20

/git/bin/validator \
    --accept-terms-of-use \
    --chain-config-file="$TESTNET_DIR/config.yaml" \
    --datadir=$NODE_DATADIR \
    --wallet-dir=$NODE_DATADIR \
    --wallet-password-file "$TESTNET_DIR/wallet-password.txt" \
    --verbosity=debug
