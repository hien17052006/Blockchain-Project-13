const { network } = require("hardhat")

async function main() {
    await network.provider.send("evm_increaseTime", [3600]);
    await network.provider.send("evm_mine");
    console.log("Time advanced by 1 hour");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});