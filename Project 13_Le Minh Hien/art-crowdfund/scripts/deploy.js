const hre = require("hardhat");

async function main() {
    const factory = await hre.ethers.getContractFactory("ArtCrowdfund");
    const contract = await factory.deploy();
    await contract.waitForDeployment();

    const goal = hre.ethers.parseEther("2");
    const tx = await contract.launchArtCampaign(goal, 3600);
    await tx.wait();

    console.log("Contract deployed at:", await contract.getAddress());
    console.log("Campaign launched with goal: 2 ETH, duration: 3600 seconds");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});