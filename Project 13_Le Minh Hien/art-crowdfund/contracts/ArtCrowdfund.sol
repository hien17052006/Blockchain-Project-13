// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ArtCrowdfund {
    address public artist;
    uint256 public goal;
    uint256 public deadline;
    uint256 public totalRaised;
    bool public launched;
    bool public withdrawn;

    mapping(address => uint256) private contributions;

    event CampaignLaunched(uint256 goal, uint256 deadline);
    event Contributed(address indexed supporter, uint256 amount);
    event Withdrawn(address indexed artist, uint256 amount);

    modifier onlyArtist() {
        require(msg.sender == artist, "Only the artist can do this");
        _;
    }

    constructor() {
        artist = msg.sender;
    }

    function launchArtCampaign(uint256 _goal, uint256 _durationSeconds) external onlyArtist {
        require(!launched, "Campaign already launched");
        require(_goal > 0, "Goal must be positive");
        require(_durationSeconds > 0, "Duration must be positive");

        goal = _goal;
        deadline = block.timestamp + _durationSeconds;
        launched = true;

        emit CampaignLaunched(_goal, deadline);
    }

    function contributeArtFund() external payable {
        require(launched, "Campaign not launched");
        require(block.timestamp < deadline, "Campaign closed");
        require(msg.value > 0, "Contribution must be positive");

        contributions[msg.sender] += msg.value;
        totalRaised += msg.value;

        emit Contributed(msg.sender, msg.value);
    }

    function getRaisedAmount() external view returns (uint256) {
        return totalRaised;
    }

    function getMySupport() external view returns (uint256) {
        return contributions[msg.sender];
    }

    function getGoal() external view returns (uint256) {
        return goal;
    }

    function isOpen() external view returns (bool) {
        return launched && block.timestamp < deadline;
    }

    function withdrawFunds() external onlyArtist {
        require(launched && block.timestamp >= deadline, "Campaign still open");
        require(!withdrawn, "Already withdrawn");
        require(totalRaised >= 0, "Nothing to withdraw");

        withdrawn = true;
        uint256 amount = totalRaised;
        (bool ok, ) = payable(artist).call{value: amount}("");
        require(ok, "Transfer failed");

        emit Withdrawn(artist, amount);
    }
}