import pytest
from brownie import network

from scripts.deploy import deploy_token_and_farm_token
from scripts.helpful_scripts import get_contract, get_account,LOCAL_BLOCKCHAIN_ENVIRONMENTS, INITIAL_PRICE_FEED_VALUE
from web3 import Web3

# Things to test
# Every pieice of code in solidity file
# setPriceFeedContract
# fund with weth

# stake
# reward
# withdraw
# unstake

def deploy():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token = deploy_token_and_farm_token()


def fund_Wallet():
    token_farm, minty_token = deploy()
    account = get_account()
    #get weth token






def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token = deploy_token_and_farm_token()
    # Act
    # stake simba tokens 
    minty_token.approve(token_farm.address,amount_staked, {"from":account})

    tx = token_farm.stakeTokens(amount_staked,minty_token,{"from":account})
    tx.wait(1)
    # check that stakingBalance is equal to staked amount
    assert token_farm.stakingBalance(minty_token, account) == amount_staked
    assert token_farm.uniqueTokensStaked(account) == 1
    assert token_farm.stakers(0) == account
    return token_farm, minty_token

def test_stake_fau_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token = test_stake_tokens(amount_staked)
    # Act
    # stake fau tokens 
    fau_token = get_contract('fau_token')
    fau_token.approve(token_farm.address,amount_staked, {"from":account})

    tx = token_farm.stakeTokens(amount_staked,fau_token,{"from":account})
    tx.wait(1)
    # check that stakingBalance is equal to staked amount
    assert token_farm.stakingBalance(fau_token, account) == amount_staked
    assert token_farm.uniqueTokensStaked(account) == 2

def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token = test_stake_tokens(amount_staked)
    startingBalance = minty_token.balanceOf(account)
    
    # Act
    token_farm.issueTokens({"from":account})
    # check that stakingBalance is equal to staked amount + issued tokens
    assert minty_token.balanceOf(account.address) == startingBalance + INITIAL_PRICE_FEED_VALUE


def test_unstake_token(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    account = get_account()
    token_farm, minty_token = test_stake_tokens(amount_staked)
    startingBalance = minty_token.balanceOf(account)

    # unstake amount_staked
    tx = token_farm.unstakeTokens(minty_token.address,{"from":account})
    tx.wait(1)

    # check balance of token for user is zero
    assert token_farm.stakingBalance(minty_token, account) == 0
    # If its the only, check user is removed form stakers,uniqueTokensStaked=0
    assert token_farm.uniqueTokensStaked(account) == 0
    # assert amount of tokens in user account is contains unstaked amount
    assert minty_token.balanceOf(account.address) == startingBalance + amount_staked
    # Assert no account in stakers array
    with pytest.raises(Exception):
        assert token_farm.stakers(0) == account
        




