// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol"; 

contract TokenFarm is Ownable {
    mapping(address => uint256) public stakingBalance;    //mapping token address -> user address -> amount staked
    mapping(address => uint256) public rewardBalance;    //mapping token address -> user address -> amount won in weth
    mapping(address => address) public tokenPriceFeedMapping;
    address [] allowedTokens;
    address [] emptyArray;
    address [] public stakers;
    address [] public newStakers;
    address public mintyToken;
    address public WethToken;
    uint256 public totalMintyStaked;
    uint256 public farmBalance;
    
    
    constructor(address _MintyTokenAddress, address _WethTokenAddress) {
        mintyToken = _MintyTokenAddress;
        WethToken = _WethTokenAddress;
        allowedTokens = [_MintyTokenAddress, _WethTokenAddress];
        farmBalance = 0;
    }

    //MAIN FUNCTIONS

    //fund contract with weth
    function fundContract(uint _amount, address _token) public {
        require(_amount> 0,"Amount must be more than zero");
        require(_token == WethToken,"Token is not allowed");
        IERC20(WethToken).transferFrom(msg.sender, address(this), _amount);
        farmBalance += _amount;
    }
   
   //Stake tokens
    function stakeTokens(uint256 _amount, address _token) public {
        //how much can they stake?
        require(_amount > 0,"Amount must be more than zero");
        require(_token == mintyToken,"Token is not allowed");
        //use transferFrom Function because we do not own the tokens. We also need the token abi from IERC20 interface
        IERC20(mintyToken).transferFrom(msg.sender, address(this), _amount);
        //add to stakingBalance
        stakingBalance[msg.sender] += _amount;
        //increase total staked
        totalMintyStaked += _amount;
        //add to stakers
        addToStakers(msg.sender);
    }

    function unstakeTokens(address _token, uint _amount) public  {
        //check if token is minty
        require(_token == mintyToken,"Token is not allowed");
        // check amount
        require(_amount > 0, "Amount must be more than zero");
        //get amount staked
        uint256 amountStaked = stakingBalance[msg.sender];
        //check if token is staked is more than amount
        require(amountStaked >= _amount,"Amount must be less than or equal to amount staked");
        // send amount to user
        IERC20(mintyToken).transfer(msg.sender, _amount);
        //remove amount from stakingBalance
        stakingBalance[msg.sender] -= _amount;
        //remove from totalMintyStaked
        totalMintyStaked -= _amount;
    }

    //reward stakers with WETH
    function rewardStakers() public {
        //get total minty staked
       for (uint i = 0; i < stakers.length; i++) {
            //get amount staked
            uint256 amountStaked = stakingBalance[stakers[i]];
            //get amount to reward
            uint256 amountToReward = amountStaked * farmBalance/totalMintyStaked;
            //set reward balance
            rewardBalance[stakers[i]] = amountToReward;
        }
        // set farm balance to zero
        farmBalance = 0;
    }

    //withdraw reward
    function withdrawReward(address _token, uint _amount) public {
        //check if token is minty
        require(_token == WethToken,"Only Weth Token is allowed");
        // fetch reward balance
        uint256 userRewardBalance = rewardBalance[msg.sender];
        //send amount to user
        IERC20(_token).transfer(msg.sender, userRewardBalance);
        //remove amount from reward balance
        rewardBalance[msg.sender] -= _amount;
    }

    //view user staked balance
    function getStakedBalance(address _token, address _user) public view returns (uint256){
        require(_token == mintyToken, "Token is not allowed");
        return stakingBalance[_user];
    }

    //view reward balance
    function getRewardBalance(address _token, address _user) public view returns (uint256){
        require(_token == WethToken, "Token is not allowed");
        return rewardBalance[_user];
    }
    
    // HELPER FUNCTION
    function tokenIsAllowed(address _token) public returns(bool){
        for (uint256 tokenIndex=0; tokenIndex<allowedTokens.length; tokenIndex++){
            if(allowedTokens[tokenIndex] == _token){
                return true;
            }
        }
        return false;
    }
 
    function fetchAllowedTokens() public view returns (address[] memory){
        return (allowedTokens);
    }

    function addToStakers(address _user) public {
        //check if user is already in stakers
        for(uint i = 0; i < stakers.length; i++){
            if(stakers[i] == _user){
                return;
            }
        }
        //add user to stakers
        stakers.push(_user);
    }
}