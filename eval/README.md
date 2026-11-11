# eval: chạy hàng loạt file IFC thử nghiệm

Mỗi lần chạy pipeline hướng 1 (`src/method_one/run_method_one.py`) tự tạo một thư mục chạy gồm
`run.log`, `result.json` và `report.md` (sinh từ `src/method_one/templates/report.md`). Thư mục này
chỉ lo việc chạy nhiều file liên tiếp rồi gom một bảng tổng.

## Chạy

Từ thư mục gốc dự án:

    .venv/bin/python eval/run_eval.py --list              # xem các ca, không chạy
    .venv/bin/python eval/run_eval.py --only duplex-a     # chạy mẫu nhỏ để kiểm tra nhanh
    .venv/bin/python eval/run_eval.py                     # chạy mọi ca (các file TNP-VSF rất nặng)
    .venv/bin/python eval/run_eval.py --reuse-fuse        # lưu cache bước fuse theo từng ca

Các file TNP-VSF lớn (hàng nghìn phần tử). Nên chạy riêng từng ca bằng `--only` và theo dõi RAM.

## Cấu trúc

- `cases.json`: danh sách ca (mã, tên, đường dẫn file IFC tính từ thư mục này, thời gian chờ tối đa).
- `data/`: các file IFC thử nghiệm (không đưa vào git).
- `templates/summary.md`: mẫu bảng tổng.
- Kết quả: `out/eval/<mã lần chạy>/summary.md` và thư mục từng ca (`out/` không bị commit).
