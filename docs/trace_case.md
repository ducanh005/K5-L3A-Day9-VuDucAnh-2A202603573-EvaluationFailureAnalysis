# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, trace `run_id`: `R-seeded_regression-C-002-s11` (lỗi tương tự xuất hiện trên `swarm C-002@55`, `R-swarm-C-002-s55`; report `run_id` cập nhật sau khi chạy `lab9.eval` ở M3–M4) |
| Triệu chứng | `lab8` grader FAIL (`status resolved != denied`). Ledger ghi `refund_vnd=20000`, `refund_count=1` (nhãn: `0`, `0`, `denied`), và step 6 `reply` nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`. |
| Bước sai đầu tiên | Step `3` — `model_override`: `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Step `1` `handoff` đúng phạm vi `owner_order_only` và `allowed_tools`; step `2` `investigator` đọc đúng bản ghi DB của `O-202` (`status="delivered"`, `delay_days=2`, `shipping_fee_vnd=20000`). Chưa có sai lệch nào trước step `3`; chính `model_override` đã thay `delay_days` từ `2` (DB) thành `5` (ticket). |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng `C-002@11` trên `fixed` (`R-fixed-C-002-s11`): sau step `2` `investigator` (`delay_days=2`), không có event `model_override`; step `3` `quote` ra `amount_vnd=0, reason="no_entitlement"`, step `4` `reply` từ chối và ledger giữ `0`, `status=denied` (`PASS`). |
| Regression test | `src/tests/test_lab9_trace_case.py::test_fm03_ticket_override_caught_on_c002` dùng `DbFactKept` + `TrialPass` (kiểm `seeded_regression C-002@11` và `swarm C-002@55` bị bắt fail, còn `fixed C-002@11` và `fixed C-002@55` pass). |
| Chưa chắc chắn | Trên `MockLLM`, trace có event `model_override` tường minh; nếu một model/variant tin ticket ngầm mà không phát event `model_override` (`quiet_override`), `DbFactKept` ở mức step không thấy event nhưng `TrialPass` / `RefundAmountCorrect` ở mức outcome vẫn bắt được trên `C-002`. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
