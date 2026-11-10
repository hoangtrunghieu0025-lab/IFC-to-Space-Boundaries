# Khảo sát hướng dựng thể tích IfcSpace và sinh boundary từ hình học B-rep 3D

- **Câu hỏi nghiên cứu**: những thuật toán nào dựng `IfcSpace` hoặc `IfcRelSpaceBoundary` từ hình học 3D của phần tử bao, và chúng khác nhau thế nào?
- **Kết luận ngắn**: văn liệu chia thành hai nhóm rõ: nhóm **cần `IfcSpace` có sẵn** (Rose & Bazjanac, Ladenhauf, Lilis CBIP) chỉ sinh boundary; nhóm **không cần** (van Treeck & Rank, Jones, Lilis ASG, Fichter IFC2SB) suy ra space từ phần tử bao. Chỉ **ASG** và **IFC2SB** vừa suy ra space vừa (cùng nhóm tác giả với CBIP) nối được sang boundary mức 2. Chỉ **CBIP** và **ASG** đã đọc kỹ.
- **Độ tin cậy**: trung bình. Bảng 1 của Fichter 2021 (đã đọc toàn văn) là nguồn chính cho so sánh; CBIP, ASG đọc toàn văn; Ying & Lee, Rose & Bazjanac, Ladenhauf chỉ qua tóm tắt/danh mục tham khảo.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

| Thuật toán | Năm | Cần `IfcSpace`? | Biểu diễn | Cách tìm space / boundary mức 1 | Mức 2 | Thử nghiệm (nguồn nêu) | Mức đọc |
|---|---|---|---|---|---|---|---|
| van Treeck & Rank, *Dimensional reduction of 3D building models using graph theory…*, Eng. with Computers 23(2):109–122, DOI 10.1007/s00366-006-0053-7 | 2007 | Không | solid | **Đồ thị cạnh–mặt** từ Boolean giữa các solid; duyệt đồ thị để tìm boundary mức 1, đảm bảo space kín | Không dùng chiếu (theo Fichter); mở rộng solid/mặt trước khi sinh mức 1 | chưa rõ | chỉ qua mô tả trong [S1][S2] |
| Jones et al., *Automated translation and thermal zoning of digital building models*, IBPSA BS 2013 | 2013 | Không | polygon | **Hệ số hình dạng** (view factor) bằng ray–face để nhận diện space | Chiếu | chưa rõ | chỉ qua [S1][S2] |
| Rose & Bazjanac, *An algorithm to generate space boundaries for building energy simulation*, Eng. with Computers 31(2):271–280, DOI 10.1007/s00366-013-0347-5 | 2013/2015 | **Có** (theo bảng Fichter) | polygon | Cắt mặt space và mặt phần tử; **đồ thị** nút là mặt biên chung/phần tử, cạnh là đường truyền nhiệt, duyệt để tìm truyền nhiệt 1 chiều (theo CBIP ref. [24] và tóm tắt bên thứ ba) | Chiếu và cắt | chưa rõ; cài bằng C++ | tóm tắt |
| Ladenhauf et al., *Computational geometry in the context of BIM*, Energy and Buildings 115:78–84, DOI 10.1016/j.enbuild.2015.02.056 | 2016 | **Có** | polygon | Cắt mặt space và mặt phần tử | Chiếu và cắt | chưa rõ | tóm tắt |
| **Lilis et al. CBIP**, Automation in Construction 76:108–124 | 2017 | **Có** (`IfcSpace` + `IfcSite`) | đa diện, **BSP-tree** | Common Boundary Intersection: mặt chung cặp phần tử, space | Boundary Intersection Projection (ngưỡng độ dày) | 1 toà 2 tầng, 514 boundary mức 2; không số liệu thời gian | **đọc kỹ** → `boundary-generation-analysis.md` |
| **Lilis et al. ASG**, IBPSA BS2021 | 2021 | **Không** (sinh `IfcSpace`) | faceted B-rep | Trừ mặt tiếp xúc cặp phần tử, gom đa giác thành vỏ theo cạnh chung, phân trong/ngoài bằng thể tích có dấu | (dành cho thuật toán sau, ví dụ CBIP) | 2 toà thật: 48 vỏ trong; Torre Turina 11 tầng | **đọc kỹ** → `ucl-asg-analysis.md` |
| **Ying & Lee**, Automation in Construction 126:103659, DOI 10.1016/j.autcon.2021.103659 | 2021 | chưa rõ | **3 biểu diễn hình học** (chưa biết) | chưa rõ | chưa rõ | 2 mô hình thực lớn | chỉ tóm tắt |
| Ying & Lee, *An algorithm to facet curved walls in IFC BIM…*, Automation in Construction 103:80–103 | 2019 | — | facet hoá tường cong | Tiền xử lý vật cong thành đa diện | — | chưa rõ | chỉ tên (từ ASG) |
| **Fichter et al. (IFC2SB)**, IBPSA BS2021 | 2021 | **Không** | mặt (face-only), OCCT BRep | Đồ thị kề mặt sau General Fuse | Chiếu và cắt + ray tracing | 1 toà văn phòng 78 space, ~2000 boundary | **đọc kỹ** → `../graph-topology/` |

## Ghi chú
- **Hướng "graph" và "B-rep" trùng nhau**: CBIP tự gọi mình "graph-less" khi so với van Treeck, Rose, Jones; nhưng ASG gom đa giác theo cạnh chung giống thành phần liên thông trên đồ thị. Ranh giới là về **cách tìm space** (trừ mặt tiếp xúc cặp-đôi hay fuse toàn bộ), không phải "có đồ thị hay không".
- **Về cái tên van Treeck**: danh mục tham khảo của bài IBPSA 2021 (Fichter) ghi "Automation in Construction 76" cho van Treeck & Rank (2007); danh mục của CBIP ghi **Engineering with Computers 23(2), 109–122, DOI 10.1007/s00366-006-0053-7**. "Automation in Construction 76" là nơi đăng của chính bài CBIP, nên đây có vẻ là nhầm lẫn trong bài IBPSA. Mình theo danh mục CBIP; chưa mở bài gốc để xác nhận.
- **Mức 1 và mức 2**: các định nghĩa theo Bazjanac (CIB W78 2010, "Space boundary requirements for modeling of building geometry for energy and other performance simulation"): mức 1 là tách thuần tuý space, mức 2 tính đến thay đổi phần tử hoặc space ở phía bên kia. Đã tải bài; chỉ đọc tóm tắt.

## Nguồn
- [S1] Fichter et al. (2021), IBPSA BS2021: https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf — đã đọc toàn văn
- [S2] Lilis et al. (2017), CBIP: https://discovery.ucl.ac.uk/id/eprint/1546334/1/CBIP_revised.pdf — đã đọc các phần chính, danh mục tham khảo
- [S3] Lilis et al. (2021), ASG: https://discovery.ucl.ac.uk/id/eprint/10169911/1/bs2021_30888.pdf — đã đọc toàn văn
- [S4] Ying & Lee (2021): https://pure.uos.ac.kr/en/publications/generating-second-level-space-boundaries-from-large-scale-ifc-com/ — chỉ tóm tắt
- [S5] Rose & Bazjanac: DOI 10.1007/s00366-013-0347-5; tóm tắt qua https://www.bohrium.com/paper-details/an-algorithm-to-generate-space-boundaries-for-building-energy-simulation/813177914232143872-3886 (chỉ thấy qua kết quả tìm kiếm)
- [S6] Ladenhauf et al.: DOI 10.1016/j.enbuild.2015.02.056 (chỉ thấy qua kết quả tìm kiếm)
- [S7] Bazjanac (2010), CIB W78: https://architektur-informatik.scix.net/pdfs/w78-2010-127.pdf — chỉ đọc tóm tắt
