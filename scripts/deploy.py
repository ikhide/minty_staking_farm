from tkinter import LEFT
from scripts.helpful_scripts import get_account,get_contract
from brownie import network, TokenFarm, Minty, config
from web3 import Web3

TOTAL_SUPPLY =  Web3.toWei(1000000, "ether")
LEFT = Web3.toWei(100, "ether")

def deploy_token_and_farm_token():
    account = get_account()

    #get weth contract address from brownie
    weth_token = get_contract("weth_token")

    #get mock minty token
    minty_token = Minty.deploy(TOTAL_SUPPLY,{'from': account})

    print(f"Deploying to {network.show_active()}")
    token_farm = TokenFarm.deploy(minty_token.address,weth_token.address,{"from":account})

    print(f"Proxy deployed to {token_farm.address}, You can upgrade to V2")

    return token_farm, minty_token, weth_token


def main():
    deploy_token_and_farm_token()
   

