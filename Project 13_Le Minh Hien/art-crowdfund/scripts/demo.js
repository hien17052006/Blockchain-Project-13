const hre = require("hardhat");
const { parseEther, formatEther } = hre.ethers;

async function expectRevert(label, promise) {
  try {
    await promise;
    console.log("FAIL (no revert):", label);
  } catch (e) {
    console.log("PASS (reverted):", label, "->", e.shortMessage || e.message);
  }
}

async function main() {
  const [artist, supporter1, supporter2] = await hre.ethers.getSigners();
  const factory = await hre.ethers.getContractFactory("ArtCrowdfund");
  const contract = await factory.deploy();
  await contract.waitForDeployment();

  console.log("=== Requirement 1: only artist, positive goal ===");
  await expectRevert("non-artist launches campaign", contract.connect(supporter1).launchArtCampaign(parseEther("2"), 3600));
  await expectRevert("artist launches with goal 0", contract.launchArtCampaign(0, 3600));
  await (await contract.launchArtCampaign(parseEther("2"), 3600)).wait();
  console.log("PASS: artist launched campaign, goal =", formatEther(await contract.getGoal()), "ETH");

  console.log("=== Requirement 2: contribution > 0, recorded per wallet ===");
  await expectRevert("contribute 0 ETH", contract.connect(supporter1).contributeArtFund({ value: 0 }));
  await (await contract.connect(supporter1).contributeArtFund({ value: parseEther("1") })).wait();
  await (await contract.connect(supporter2).contributeArtFund({ value: parseEther("0.5") })).wait();
  console.log("Supporter 1 support:", formatEther(await contract.connect(supporter1).getMySupport()), "ETH");
  console.log("Supporter 2 support:", formatEther(await contract.connect(supporter2).getMySupport()), "ETH");

  console.log("=== Requirement 4: goal and raised amount ===");
  console.log("Goal:", formatEther(await contract.getGoal()), "ETH");
  console.log("Raised:", formatEther(await contract.getRaisedAmount()), "ETH");

  console.log("=== Requirement 3: no contributions after campaign closes ===");
  await hre.network.provider.send("evm_increaseTime", [3601]);
  await hre.network.provider.send("evm_mine");
  console.log("Campaign open:", await contract.isOpen());
  await expectRevert("contribute after close", contract.connect(supporter1).contributeArtFund({ value: parseEther("1") }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});