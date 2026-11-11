# Báo cáo lần chạy: ${ifc_name}

- Thời điểm: ${started_at}
- Commit: ${commit}
- Môi trường: Python ${python_version}, ifcopenshell ${ifcopenshell_version}
- File: `${ifc_name}` (${size_mb} MB, schema ${schema})
- Thư mục chạy: `${run_dir}`
- Tổng thời gian: ${total_seconds} s, RAM đỉnh: ${peak_memory_mb} MB

## Thời gian từng bước

${steps_table}

## Số liệu chính

${counts_table}

## So với IfcSpace gốc (xấp xỉ)

${comparison}

## Các phòng tìm được

${rooms_table}

## Nhận xét

(điền tay sau khi xem kết quả)
