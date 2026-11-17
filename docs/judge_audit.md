# Judge audit

Chạy:
- `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`
- `python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Observed → RG Fail Rate | Ma trận (`tp/fp/fn/tn`) | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|---|---|
| `tone_ok` | 100 | 0.757 | 0.857 | 0.800 | 0.28 → 0.30 | `24 / 4 / 6 / 66` | **PASS** | **Dùng** (theo dõi giọng điệu, kèm sửa rubric các ca biên) |
| `helpful` | 100 | 0.375 | 1.000 | 0.300 | 0.09 → 0.30 | `9 / 0 / 21 / 70` | **FAIL** (`κ < 0.6`, `R < 0.7`) | **Loại** — không dùng làm gate |

## Audit thủ công các ca bất đồng (≥5 case)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hướng sửa rubric / grader |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone`) | PASS | FAIL | Người đúng | `"Em đã hoàn tiền cho anh rồi nha..."` — xưng `em` + `nha` quá suồng sã; thêm quy tắc bắt buộc xưng `LogiX` – `anh/chị`, cấm `nha/nhé`. |
| 2 | `H-017` (`tone`) | PASS | FAIL | Người đúng | `"Dạ, bạn ơi LogiX đã hoàn 25.000đ... rồi nha."` — xưng `bạn ơi` không chuẩn CSKH; bổ sung ví dụ negative cho rubric `tone_ok`. |
| 3 | `H-029` (`tone`) | PASS | FAIL | Người đúng | `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` — judge bị đánh lừa bởi chữ `"Dạ, vui lòng"`, bỏ sót vế ra lệnh/đuổi khách; thêm tiêu chí cấm câu xua đuổi. |
| 4 | `H-042` (`tone`) | FAIL | PASS | Người đúng | `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` — ngắn gọn, lịch sự, đủ ý; cập nhật rubric không bắt buộc câu xin lỗi khi hoàn tiền thành công. |
| 5 | `H-051` (`tone`) | FAIL | PASS | Người đúng | `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` — dùng thuật ngữ `"refund"` được CS LogiX cho phép; đưa từ `"refund"` vào whitelist rubric. |
| 6 | `H-070` (`tone`) | PASS | FAIL | Người đúng | `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"` — dùng emoji cười không phù hợp ngữ cảnh khiếu nại; thêm luật cấm emoji cảm xúc vào rubric. |
| 7 | `H-081` (`tone`) | FAIL | PASS | Judge đúng | `"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."` — note gốc ghi nhãn người đọc nhầm ticket; cần sửa lại nhãn tham chiếu. |
| 8 | `HL-015` (`helpful`) | PASS | FAIL | Người đúng | Reply báo hoàn `55.000đ`, nhưng ledger chỉ ghi `40.000đ` (`FM-08`); judge chỉ đọc text nên không thấy sai lệch dữ liệu → thay bằng **code grader** đối chiếu ledger. |
| 9 | `HL-016` (`helpful`) | PASS | FAIL | Người đúng | Reply viết rất dài, xin lỗi nhiều lần (`"thành thật xin lỗi..."`) nhưng báo sai tiền (`55.000đ` vs ledger `35.000đ`) — judge bị *verbosity/politeness bias* đánh lừa. |
| 10 | `HL-047` (`helpful`) | PASS | FAIL | Người đúng | `"Ok bạn, đơn O-515 xử lý rồi nhé."` — cụt lủn và sai xưng hô, nhưng judge vẫn chấm `PASS`; cần gộp kiểm tra xưng hô chuẩn hoặc tách riêng code check. |

## Kết luận
- **`helpful` bị loại hoàn toàn khỏi CI gate:** trên ma trận nhầm lẫn (`tp=9, fp=0, fn=21, tn=70`), judge chỉ đạt `Recall = 0.300` và `κ = 0.375`, **bỏ sót 21/30 ca lỗi thật (70%)**. Tỉ lệ lỗi quan sát được chỉ là `0.09`, làm ẩn đi tỉ lệ lỗi thực sau hiệu chỉnh Rogan–Gladen (`0.30`). Trong 21 ca `FN`, **18 ca là báo sai số tiền so với ledger** (và nhiều ca cố tình viết dài/xin lỗi để đánh lừa judge) cùng **3 ca sai xưng hô**. Việc kiểm tra tính đúng của số tiền hoàn (`FM-08`) bắt buộc phải giao cho **code grader đối chiếu `refund_ledger`** ở M3, không dùng LLM judge.
- **`tone_ok` đủ chuẩn để sử dụng (`κ = 0.757 ≥ 0.6`, `P = 0.857 ≥ 0.8`, `R = 0.800 ≥ 0.7`)**, nhưng cần siết lại rubric đối với các mẫu câu suồng sã (`nha`, `bạn ơi`), giọng xua đuổi (`không cần nhắn thêm`), emoji và bỏ phạt nhầm từ `refund`.
- **Rủi ro còn lại:** cả hai judge chỉ được kiểm định trên dữ liệu replay đã công khai (`n=100`); cần thu thập thêm nhãn người độc lập (held-out) sau mỗi lần sửa rubric hoặc đổi prompt/model của judge trước khi cho phép judge tham gia bất kỳ quyết định nào.
