from scripts.helpful_scripts import get_account
from brownie import network, TokenFarm, Minty,config
import time 
from web3 import Web3

TOTAL_SUPPLY =  Web3.toWei(1000000, "ether")

def deploy_token_and_farm_token():
    account = get_account()

    #get weth contract address from brownie
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    #get mock minty token

    minty_token = Minty.deploy(TOTAL_SUPPLY,{'from': account})

    print(f"Deploying to {network.show_active()}")
    token_farm = TokenFarm.deploy(minty_token.address,erc20_address,{"from":account},publish_source=True)



    print(f"Proxy deployed to {token_farm.address}, You can upgrade to V2")
    

    return  token_farm, minty_token


def main():
    deploy_token_and_farm_token()
   

