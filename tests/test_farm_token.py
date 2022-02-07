import pytest
from brownie import network, config, accounts

from scripts.deploy import deploy_token_and_farm_token
from scripts.helpful_scripts import get_account,LOCAL_BLOCKCHAIN_ENVIRONMENTS, approve_erc20

from web3 import Web3

# Test staking
def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    account2 = get_account(2)
    token_farm, minty_token, weth_token = deploy_token_and_farm_token()
    # Act
    # stake simba tokens 
    minty_token.approve(token_farm.address,amount_staked, {"from":account})

    tx = token_farm.stakeTokens(amount_staked,minty_token,{"from":account})
    tx.wait(1)
    # check that stakingBalance is equal to staked amount
    assert token_farm.stakingBalance(account) == amount_staked
    assert token_farm.stakers(0) == account
    assert token_farm.stakers(0) != account2
    assert token_farm.totalMintyStaked() == amount_staked

    return token_farm, minty_token, weth_token


# Test UnStaking
def test_unstake_token(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token, weth_token = test_stake_tokens(amount_staked)
    amountToUnstake = Web3.toWei(0.5,"ether")

    # unstake amount_staked
    tx = token_farm.unstakeTokens(minty_token.address, amountToUnstake,{"from":account})
    tx.wait(1)

    # check balance of token for user is zero
    assert token_farm.stakingBalance(account) == amount_staked - amountToUnstake
    assert token_farm.totalMintyStaked() == amount_staked - amountToUnstake

    # unStake more than staked amount
    with pytest.raises(Exception):
        amountToUnstake = Web3.toWei(1.5,"ether")
        tx = token_farm.unstakeTokens(minty_token.address, amountToUnstake,{"from":account})
        tx.wait(1)

    return token_farm, minty_token, weth_token
    

# test fund and reward
def test_fund_token_farm(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    account2 = get_account(2)
    token_farm, minty_token, weth_token = test_unstake_token(amount_staked)
    amountToFund = Web3.toWei(15,"ether")
    weth_token.approve(token_farm.address,amountToFund, {"from":account})
    tx = token_farm.fundContract(amountToFund,weth_token.address,{"from":account})
    tx.wait(1)

    # check total farmBalance is equal to amountToFund
    assert token_farm.farmBalance() == amountToFund

    #send some minty to account two
    minty_token.transfer(account2,Web3.toWei(1,"ether"),{"from":account})
    #account2 minty balance
    assert minty_token.balanceOf(account2) == Web3.toWei(1,"ether")
    #account 2 stake minty
    minty_token.approve(token_farm.address,Web3.toWei(1,"ether"),{"from":account2})
    tx = token_farm.stakeTokens(Web3.toWei(1,"ether"),minty_token,{"from":account2})
    tx.wait(1)

    assert minty_token.balanceOf(account2) == 0
    #reward stakers
    tx = token_farm.rewardStakers({"from":account})
    tx.wait(1)
    # check that reward is split correctly account 1 = 5 WETH, account 2 = 10 WETH
    assert token_farm.rewardBalance(account) == Web3.toWei(5,"ether")
    assert token_farm.rewardBalance(account2) == Web3.toWei(10,"ether")

    # farmBalance is zero
    assert token_farm.farmBalance() == 0

    return token_farm, minty_token, weth_token


def test_withdraw_from_farm(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    account2 = get_account(2)
    token_farm, minty_token, weth_token = test_fund_token_farm(amount_staked)
    amountToWithdraw = Web3.toWei(2,"ether")
    # withdraw weth from farm
    tx = token_farm.withdrawReward(amountToWithdraw,weth_token.address,{"from":account})
    tx.wait(1)
    # check that account 1 has 3 weth after withdrawing two
    assert token_farm.rewardBalance(account) == Web3.toWei(3,"ether")
    # check that account 2 has 8 weth after withdrawing two
    tx = token_farm.withdrawReward(amountToWithdraw,weth_token.address,{"from":account2})
    tx.wait(1)
    assert token_farm.rewardBalance(account2) == Web3.toWei(8,"ether")






    






    





