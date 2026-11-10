# Giới hạn của hướng lát cắt mặt bằng

- **Câu hỏi nghiên cứu**: những trường hợp nào hướng này chắc chắn không xử lý được, vì sao, và phần nào của công trình như sân vận động nằm ngoài khả năng?
- **Kết luận ngắn**: hướng này **chỉ mô tả được không gian có dạng đùn thẳng đứng từ một dấu chân**, nên không biểu diễn đúng mái dốc, khán đài bậc thang, sàn xiên. Với sân vận động, chỉ phần có tường bao kín (hành lang vòng, phòng phục vụ, tầng hầm) có khả năng khớp; phần khán đài mở trời gần như chắc chắn nằm ngoài khả năng. Một phần là **kết quả đo**, phần còn lại là **suy luận hình học** (đã ghi rõ).
- **Độ tin cậy**: mục 1 (đã đo) trung bình; mục 2 (suy luận hình học) cao về lý do nhưng chưa thử trên mô hình thật.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Giới hạn đã quan sát khi đo (6 file nhỏ, `close = 0`)
| Quan sát | Số liệu | Ghi chú |
|---|---|---|
| `IfcSpace` không khớp | 25 trên 63 | Nguyên nhân chưa điều tra từng ca; xem các giả thuyết ở dưới |
| Tầng áp mái FZK-Haus | 0 phòng ở `close = 0`, 1 ở `close = 0,05` | Mặt cắt cao 3,7 m cắt qua mái xiên |
| duplex-a tầng 1 | 2/10 khớp (IoU tốt nhất của nhiều space chỉ 0,05–0,45) | Nghi space chia nhỏ không có tường/cửa đặc giữa chúng |
| duplex-a tầng 2 | 4 khớp; 4 `IfcSpace` khác có IoU 0 dù bị mặt phẳng cắt | chưa điều tra |
| bsi-ifc4-building-architecture | 0 phòng, 2 `IfcSpace` | Có 5 phần tử bị cắt nhưng không tạo vùng kín; không rõ vì tường không khép hay lỗi tính |
| Phòng thừa (không có `IfcSpace`) | 9 | Có thể là phòng thật thiếu space, hoặc lỗ do cột/giếng |

Các giả thuyết chưa kiểm chứng: (a) vách ảo (không có phần tử vật lý) chia không gian; (b) cánh cửa không có hình khối; (c) tường không giao nhau ở góc; (d) space gốc không nằm đúng tầng; (e) cao độ cắt không phù hợp.

## 2. Giới hạn hình học (suy luận, chưa thử)
1. **Mái dốc, tầng áp mái:** vùng bị mái cắt có hình không phải khối đùn thẳng đứng; một cao độ cắt chỉ cho một lát. Đùn thẳng đứng sai chiều cao.
2. **Khán đài bậc thang (sân vận động):** sàn xiên theo bậc, trần/mái cong; mỗi hàng ghế ở cao độ khác nhau. Một mặt phẳng ngang không phản ánh được; không có "vòng kín" vì khán đài mở ra sân.
3. **Không gian không phải khối đùn:** mặt sàn xiên, trần cong, vòm.
4. **Không gian thông tầng:** cần ghép lát nhiều tầng (mục 4 của `method-analysis.md`), chưa có kiểm chứng.
5. **Space không bị tường bao:** phòng chia bằng vách ảo hoặc nội thất; cần dữ liệu ngoài hình học (loại phòng, vách ảo).
6. **Phụ thuộc mô hình đầy đủ:** nếu tường thiếu hoặc lệch thì không có vòng kín.
7. **Boundary mức 2:** hướng này chỉ cho phòng 2D; boundary phải sinh ở bước khác (CBIP/BIP hoặc IFC2SB).

## 3. Ước lượng phần sân vận động nằm ngoài khả năng (suy luận)
| Phần | Khả năng | Lý do |
|---|---|---|
| Khán đài mở trời | Không | Mục 2.2; không có vòng kín |
| Hành lang vòng (concourse) có tường bao | Có thể một phần | Dạng gần khối đùn, nhưng cong và dốc nhẹ |
| Phòng phục vụ, thay đồ, kho | Có thể | Nhà nhiều phòng hộp |
| Mái | Không | Không phải space |
| Tầng hầm, bãi xe | Có thể | Nếu tường kín |
Tỷ lệ diện tích không đo được vì chưa có mô hình sân vận động.

## Chưa xác minh / việc còn lại
- Điều tra từng ca không khớp ở duplex-a và bsi-ifc4.
- Thử mô hình có mái dốc lớn, cột, tường cong.
- Thử trên mô hình lớn (tầng M, L của TASK-001) khi có.

## Nguồn
Xem `survey.md`, `prototype/README.md`.
