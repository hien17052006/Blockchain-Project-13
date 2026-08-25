import hashlib, time
from eth_account import Account
from eth_account.messages import encode_defunct

# LAB 3.1 - HASH PROPERTIES & TOY PROOF-of-WORK
# avalanche effect
print(hashlib.sha256(b"Blockchain 2026").hexdigest())
print(hashlib.sha256(b"blockchain 2026").hexdigest())

# Toy PoW: tìm nonce sao cho sha256(data + nonce) bắt đầu bằng k số 0
def mine (data: bytes, k: int) -> tuple[int, float]:
    target = "0"*k
    nonce, t0 = 0, time.time()
    while True:
        h = hashlib.sha256(data + str(nonce).encode()).hexdigest()
        if h.startswith(target):
            return nonce, time.time() - t0
        nonce += 1
for k in range(1,7):
    nonce, dt = mine(b"block#1|txroot=abc|", k)
    print(f"k={k} nonce={nonce:>9} time={dt:.3f}s")

# LAB 3.2 - MERKLE TREE
"""Lab 3.2 — Merkle tree (starter).


Hoàn thành 3 TODO rồi chạy:  python3 merkle_starter.py
Mọi dòng CHECK phải in OK.   All CHECK lines must print OK.


Quy ước (theo Bitcoin) / Convention (Bitcoin rule):
 - Lá = sha256(dữ liệu giao dịch).            Leaf = sha256(tx bytes).
 - Cha = sha256(trái + phải) trên byte digest. Parent = sha256(left + right) over raw digests.
 - Tầng lẻ: nhân đôi phần tử cuối.             Odd level: duplicate the last element.
"""
def H(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def merkle_root(leaves: list[bytes]) -> bytes:
    current_level = list(leaves) 
    while len(current_level) > 1:
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
        next_level = []
        for i in range (0, len(current_level), 2):
            parent = H(current_level[i] + current_level[i+1])
            next_level.append(parent)
        current_level = next_level
    return current_level[0]
    raise NotImplementedError

def merkle_proof(leaves: list[bytes], index: int) -> list[tuple[bytes, bool]]:
    proof = []
    current = list(leaves)
    curr_idx = index
    while len(current) > 1:
        if len(current) % 2 != 0:
            current.append(current[-1])
        if curr_idx % 2 == 0:
            sibling_idx = curr_idx + 1
            is_left = False
        else:
            sibling_idx = curr_idx - 1
            is_left = True
        proof.append((current[sibling_idx], is_left))
        next_level = []
        for i in range(0, len(current), 2):
            next_level.append(H(current[i] + current[i+1]))
        current = next_level
        curr_idx = curr_idx // 2
    return proof
    raise NotImplementedError

def verify_proof(leaf_hash: bytes, proof: list[tuple[bytes, bool]], root: bytes) -> bool:
    curr = leaf_hash
    for sibling, is_left in proof:
        if is_left:
            curr = H(sibling + curr)
        else:
            curr = H(curr + sibling)
    return curr == root
    raise NotImplementedError

# ------------------------------------------------------------------ checks
if __name__ == "__main__":
   txs = [f"tx{i}: A->B {i} coin".encode() for i in range(8)]
   leaves = [H(t) for t in txs]
   root = merkle_root(leaves)


   print("root:", root.hex())


   # CHECK 1: proof đúng cho mọi lá / valid proof for every leaf
   ok = all(verify_proof(leaves[i], merkle_proof(leaves, i), root) for i in range(8))
   print("CHECK 1 (all 8 proofs valid):", "OK" if ok else "FAIL")


   # CHECK 2: proof có đúng log2(8)=3 phần tử / proof has exactly 3 elements
   print("CHECK 2 (proof length == 3):", "OK" if len(merkle_proof(leaves, 4)) == 3 else "FAIL")


   # CHECK 3: lá bị sửa phải trượt / a tampered leaf must fail
   fake = H(b"tx4: A->B 999999 coin")
   print("CHECK 3 (tampered leaf fails):",
         "OK" if not verify_proof(fake, merkle_proof(leaves, 4), root) else "FAIL")

    # CHECK 4: số lá lẻ (7) vẫn chạy / odd leaf count (7) still works
   l7 = leaves[:7]
   r7 = merkle_root(l7)
   print("CHECK 4 (odd count works):",
         "OK" if all(verify_proof(l7[i], merkle_proof(l7, i), r7) for i in range(7)) else "FAIL")

# LAB 3.3 - SIGN, VERIFY & RECOVER WITH ETH-ACCOUNT
acct = Account.create()
print("address:", acct.address)

msg = encode_defunct(text="I attended Session 3")
sig = Account.sign_message(msg, acct.key)
print("r, s, v:", hex(sig.r), hex(sig.s), sig.v)

#Recover the address from the signature alone 
who = Account.recover_message(msg, signature=sig.signature)
print("recovered:", who, "| match:", who == acct.address)

# Tamper 1 character
bad = encode_defunct(text="I attended Session 4")
print("tampered ->", Account.recover_message(bad, signature=sig.signature))
