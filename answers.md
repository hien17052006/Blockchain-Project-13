# Lab 03 — Hash, Merkle tree & Digital Signatures — Answers / Bài nộp

## Lab 3.1 — Hash properties & toy Proof-of-Work

**Output:**
```
sha256("Blockchain 2026")  = c42dafbbe164b917016b4c3491ee7445e6c01fae0524a83f96c2ece87
sha256("blockchain 2026")  = 3b467304922f266e0331cc5e1598ec58657f48b5a9e2587763260244a

k=1  nonce=        5   time=0.000s
k=2  nonce=       61   time=0.000s
k=3  nonce=       61   time=0.000s
k=4  nonce=    14229   time=0.025s
k=5  nonce=    55980   time=0.106s
k=6  nonce= 24517505   time=42.974s
```

**Q1. Each extra leading zero multiplies expected work by ≈ how much? Why?**

≈ 16 lần. SHA-256 được xem như một hàm sinh chuỗi hex ngẫu nhiên đều (uniform random). Mỗi ký tự hex biểu diễn 4 bit, nên xác suất một ký tự cụ thể bằng `0` là 1/16. Yêu cầu thêm một số `0` ở đầu độc lập với các ký tự trước, nên xác suất khớp `k` số `0` liên tiếp là `(1/16)^k`. Do đó số lần thử (nonce) kỳ vọng để tìm ra hash thỏa mãn tăng theo cấp số nhân, mỗi số `0` thêm vào nhân độ khó lên ≈16 lần.

**Q2. Verifying your found nonce takes how many hash calls? What does this say about PoW?**

Chỉ 1 lần gọi băm: tính lại `sha256(data + nonce)` rồi kiểm tra chuỗi có bắt đầu bằng `k` số `0` hay không. Điều này thể hiện tính bất đối xứng cốt lõi của Proof-of-Work: tìm ra nonce hợp lệ tốn kém về mặt tính toán (hàng nghìn đến hàng triệu lần thử), nhưng xác minh lại cực rẻ (1 lần băm). Nhờ tính bất đối xứng này, mạng có thể yêu cầu "chi phí" (công) để tạo khối mới, trong khi mọi node khác vẫn xác minh khối đó gần như tức thời.

---

## Lab 3.2 — Merkle tree

**Output:**
```
root: d165f2662101d81e1047041b5e79eeab7ada803326b28b1510b9dbb407f0bcb2
CHECK 1 (all 8 proofs valid): OK
CHECK 2 (proof length == 3): OK
CHECK 3 (tampered leaf fails): OK
CHECK 4 (odd count works): OK
```

**Q3. For n = 1,000,000 transactions, how many hashes does one proof contain?**

`⌈log2(1,000,000)⌉ = 20` hash. Vì 2^19 = 524,288 < 1,000,000 ≤ 2^20 = 1,048,576, cây Merkle cần 20 tầng, và một proof (đường đi từ lá lên gốc) chứa đúng 20 giá trị băm anh em — mỗi tầng một giá trị.

**Q4. Explain one real system that uses exactly this mechanism.**

**SPV (Simplified Payment Verification)** trong ví Bitcoin nhẹ: ví không tải toàn bộ blockchain mà chỉ tải header của các khối (chứa Merkle root). Khi cần xác minh một giao dịch đã nằm trong khối, full node gửi cho ví một Merkle proof (danh sách hash anh em từ giao dịch đó lên root). Ví tự tính lại hash từ dưới lên và so sánh với root đã có trong header — nếu khớp, giao dịch được xác nhận là có thật trong khối, mà không cần tải toàn bộ hàng triệu giao dịch. Đây chính là cơ chế `merkle_proof` / `verify_proof` vừa cài đặt.

---

## Lab 3.3 — Sign, verify & recover with eth-account

**Output:**
```
address: 0xDBbeeB604dB0d924Ea41bfC6b62C2741b376906C
r: 0xb9b46bda421718101dedcd7d0f8f1bc9c8a1850be6539ab7abba2022
s:         0x5b1e8677be609b319682f8d842856ab4f5f7b02d1bc1e52e6b59d406beb4ad17
v: 27

recovered: 0xDBbeeB604dB0d924Ea41bfC6b62C2741b376906C | match: True
tampered -> 0x587Aa7D94fC862df45E150feAE34541ACe2201fe
```

**Task 1. Run twice with the same message — is the signature identical? Which RFC explains this?**

Có, chữ ký sẽ giống hệt nhau ở mỗi lần chạy nếu cùng message và cùng private key. Thư viện `eth-account` sinh nonce `k` dùng cho ECDSA một cách tất định theo **RFC 6979**, thay vì lấy ngẫu nhiên mỗi lần. Vì `k` chỉ phụ thuộc vào private key và hash của message, nên (r, s, v) luôn tái tạo được giống nhau. 


**Task 2. Tampered message recovers a different address — why does this prove integrity?**

Chữ ký ECDSA gắn chặt với hash của đúng nội dung message đã ký. Khi đổi dù chỉ 1 ký tự ("Session 3" → "Session 4"), hash của message thay đổi hoàn toàn (hiệu ứng tuyết lở, giống Lab 3.1). Vì `recover_message` dùng (r, s, v) cùng với hash mới của message đã sửa để giải ra public key, mà cặp (r, s) không còn khớp với hash mới nên phép tính cho ra một địa chỉ khác hẳn — trong trường hợp này là `0x587Aa7D9...` thay vì `0xDBbeeB60...`. Vì địa chỉ khôi phục không khớp với địa chỉ người ký ban đầu, bất kỳ ai xác minh cũng phát hiện ngay message đã bị sửa → đây chính là bằng chứng toàn vẹn (integrity): chữ ký chỉ hợp lệ với đúng nội dung gốc, không thể tách rời message khỏi chữ ký mà vẫn xác minh đúng người ký.

