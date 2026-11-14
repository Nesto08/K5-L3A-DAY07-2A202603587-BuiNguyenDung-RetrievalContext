# Báo cáo Day 7

## Dữ liệu và benchmark

- **Nguồn:** *Introduction to Python Programming* — OpenStax (https://openstax.org/details/books/introduction-python-programming), tập trung chương 1–2; chọn 59 trang từ PDF 397 trang, tạo **224 chunk** (fixed 500 ký tự, overlap 50). Ghi nguồn và kiểm tra điều khoản cấp phép, đặc biệt trước khi công khai ứng dụng AI.
- **Vector store / embedding:** ChromaDB `lab06_a` của Day 6; OpenAI `text-embedding-3-small`, **1.536 chiều**. Giữ nguyên vector và ID, không embedding lại tài liệu. Phiên bản snapshot model không được ghi nhận.
- **Agent:** `gpt-4o-mini` sử dụng tool calling, kết nối qua `starter/agentic.py` và `starter/adapters.py` với Hybrid RRF.
- **Benchmark:** **24 câu**: Dev 17 (15 có bằng chứng, 2 thiếu), Test 7 (5 có, 2 thiếu). Gold evidence kiểm tra theo nguồn, trang và nội dung chunk; không cung cấp gold cho Agent. Các câu thiếu bằng chứng được rà soát trên corpus, nhưng chưa kiểm chứng độc lập toàn diện. Đánh giá retrieval bằng Hit@1, Evidence Hit@3, Context Evidence Rate; Agent bằng điểm 0/1/2, citation, abstention và lượt gọi tool.
- **SHA-256 benchmark:** `637992564C4CD247CCC8EA7B73CDC0839DE64A024DC50FAFDD15043D093C1578`.

## Retrieval và thử nghiệm

Cùng corpus, **top-k=3**; Hybrid dùng TF-IDF + Dense, **RRF k=60**, lấy 10 ứng viên mỗi nhánh; không có reranker học máy. Metadata filter được hỗ trợ khi câu hỏi yêu cầu chương. Đơn vị latency: **ms (median)**; chi phí API bằng USD chưa tính.

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| Baseline | TF-IDF, k=3, không rerank, 800 ký tự | Mốc tìm kiếm từ khóa | Dev, n=15 | 6/15 (40%) | 11/15 (73,3%) | 6/15 (40%) | 0,52 ms; API $0 |
| Phương pháp 2 | Dense, ChromaDB, k=3, 800 ký tự | Tìm kiếm ngữ nghĩa | Dev, n=15 | 6/15 (40%) | 13/15 (86,7%) | 6/15 (40%) | 209,85 ms; 151 embedding tokens |
| Phương pháp 3 | Hybrid RRF, k=3, 800 ký tự | Kết hợp hai cách tìm | Dev, n=15 | 9/15 (60%) | 12/15 (80%) | 9/15 (60%) | 254,09 ms; 151 tokens |
| Cải thiện 1 | Hybrid RRF, k=3, 1.200 ký tự | Mở rộng context | Dev, n=15 | 9/15 (60%) | 12/15 (80%) | 10/15 (66,7%) | 253,92 ms; 151 tokens |
| Cải thiện 2 | Hybrid RRF, k=3, 1.600 ký tự | Giữ thêm evidence | Dev, n=15 | 9/15 (60%) | 12/15 (80%) | **11/15 (73,3%)** | 278,99 ms; 151 tokens |
| Cấu hình đã chọn | **Hybrid B**, k=3, 1.600 ký tự | Chốt trên Dev rồi đánh giá Test | Test, n=5 | 3/5 (60%) | 5/5 (100%) | 4/5 (80%) | 343,49 ms; 62 tokens |
| Baseline | TF-IDF, k=3, 800 ký tự | Đối chứng Test | Test | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

**Lựa chọn:** Hybrid B tăng Context Evidence Rate Dev từ **9/15 lên 11/15**, đổi lại context dài hơn và có thể tăng chi phí chat. Hai lỗi Dev: **Q03** (truy xuất bài tập `print()` thay vì đoạn giải thích `end`) và **Q08** (truy xuất nội dung nối chuỗi thay vì định nghĩa string). Cả hai lặp tìm kiếm và chạm `search_limit`; thử cải thiện prompt nhưng chưa khắc phục. Tập Test nhỏ và có câu kế thừa từ Day 6 nên kết quả không đại diện rộng.

## Agent và đánh giá

**Luồng:** Model gọi tool Hybrid RRF → lấy tối đa 3 chunk, đóng gói trong **1.600 ký tự** → trả lời có `[chunk-id]` hoặc từ chối. Giới hạn tối đa **2 lượt search/câu**; kiểm tra citation ID có trong context và câu trả lời. Lỗi provider/tool được ghi riêng, không tính là từ chối đúng. Nhãn chấm dưới đây là **đánh giá từ trace**, chưa được giảng viên xác nhận độc lập.

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|
| Hybrid B + `gpt-4o-mini` / Dev | 17/17 | 21 | 0: 2; 1: 1; 2: 12; **1,67/2** | 15/15 | 13/13 câu answered | 2/2 | 2/15 |
| Hybrid B + `gpt-4o-mini` / Test | 7/7 | 13 | 0: 4; 1: 0; 2: 1; **0,40/2** | 1/1 | 1/1 câu answered | 2/2 | 4/5 |
| **Tổng 24 câu** | **24/24** | **34** | 0: 6; 1: 1; 2: 13; **1,35/2** (20 câu có evidence) | **16/16** | **14/14 câu answered** | **4/4** | **6/20** |

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|
| Q01 | Có evidence | 1 search, answered | Trang 19, `_19_fixed_1`, `_19_fixed_2` | 2/2 |
| Q02 | Có evidence | 1 search, answered | `sep`, `_21_fixed_0` | 2/2 |
| Q03 | Có evidence | 2 search, abstain | Không có citation | 0/2, `search_limit` |
| Q04 | Có evidence | 1 search, answered | `input()`, `_22_fixed_1` | 2/2 |
| Q05 | Có evidence | 1 search, answered | Phép gán `=`, `_44_fixed_0` | 2/2 |
| Q06 | Có evidence | 1 search, answered | Snake case, `_25_fixed_0` | 2/2 |
| Q07 | Có evidence | 1 search, answered | Tên biến, `_25_fixed_0` | 2/2 |
| Q08 | Có evidence | 2 search, abstain | Không có citation | 0/2, `search_limit` |
| Q09 | Có evidence | 1 search, answered | Nối chuỗi, `_28_fixed_1`, `_69_fixed_3` | 2/2 |
| Q10 | Có evidence | 1 search, answered | Định dạng số, `_30_fixed_0` | 2/2 |
| Q11 | Có evidence | 1 search, answered | Thứ tự phép toán, `_32_fixed_0` | 2/2 |
| Q12 | Có evidence | 1 search, answered | SyntaxError, `_34_fixed_0` | 2/2 |
| Q13 | Có evidence | 1 search, answered | Comment `#`, `_37_fixed_1` | 2/2 |
| Q14 | Có evidence | 1 search, answered | REPL, `_49_fixed_0` | 2/2 |
| Q15 | Có evidence | 1 search, answered | Phép chia, `_59_fixed_0` | 1/2, diễn đạt chưa chặt |
| Q16 | Có evidence | 2 search, abstain | Không có citation | 0/2, context có evidence nhưng `search_limit` |
| Q17 | Có evidence | 2 search, abstain | Không có citation | 0/2, thiếu đoạn phù hợp trong context |
| Q18 | Có evidence | 2 search, abstain | Không có citation | 0/2, evidence ở top-3 nhưng không vào context |
| Q19 | Có evidence | 2 search, abstain | Không có citation | 0/2, context đủ evidence nhưng `search_limit` |
| Q20 | Có evidence | 1 search, answered | `math.floor(x)`, `_64_fixed_0` | 2/2 |
| Q21 | Thiếu evidence | 2 search, abstain | Không có citation | Từ chối phù hợp |
| Q22 | Thiếu evidence | 2 search, abstain | Không có citation | Từ chối phù hợp |
| Q23 | Thiếu evidence | 2 search, abstain | Không có citation | Từ chối phù hợp |
| Q24 | Thiếu evidence | 2 search, abstain | Không có citation | Từ chối phù hợp |

- ### Đường dẫn trace, nhãn và lệnh chạy

**1. Đường dẫn kết quả**

- **Agent Dev (17 câu):** `results/agent-dev/`
- **Agent Test (7 câu):** `results/agent-test/`
- **Tổng hợp 24 câu:** `results/agent-all/`
- **Retrieval:** `results/tfidf-dev-final/`, `results/dense-dev/`, `results/hybrid-dev/`, `results/hybrid-a-dev/`, `results/hybrid-b-dev/`, `results/hybrid-b-test/`.

Trong đó, `traces.json` lưu quá trình Agent tìm kiếm và trả lời; `reviews.json` lưu nhãn đánh giá; `agent_metrics.json` lưu các chỉ số tổng hợp.

**2. Nhãn đánh giá**

- `answer_grade`: Chất lượng câu trả lời (0 = sai hoặc không trả lời được; 1 = đúng một phần; 2 = đúng và đủ bằng chứng).
- `citation_support`: Citation có hỗ trợ nội dung trả lời hay không.
- `abstention_correct`: Agent từ chối trả lời có đúng hay không.

**3. Lệnh chạy**

Chạy Agent trên 7 câu Test:

```powershell
python starter/run_agent.py --chunks data/day6_chunks.json --questions data/day7_questions.json --split test --output results/agent-test --db "C:\Ngay05\K5-L3A-DAY06-2A202603587-BuiNguyenDung-DataIngestionEngineering\starter\chroma_db"
```

Tính metrics từ kết quả Test đã lưu:

```powershell
python starter/agent_metrics.py --cases data/day7_questions.json --traces results/agent-test/traces.json --reviews results/agent-test/reviews.json --split test --output results/agent-test/agent_metrics.json
```

- **Thời gian / token Agent:** Dev 116 embedding + 17.391 input + 1.473 output tokens; Test 77 embedding + 10.469 input + 486 output tokens. Độ trễ tổng cộng các lượt chạy lần lượt khoảng **49,6 giây** và **34,9 giây**; chi phí USD chưa được quy đổi.
- **Kết quả trước/sau và giới hạn:**
    - **Trước cải thiện:** Hybrid RRF với context 800 ký tự đạt Context Evidence Rate 9/15 câu (60%) trên Dev.
    - **Sau cải thiện:** Tăng context lên 1.600 ký tự giúp kết quả đạt 11/15 câu (73,3%) trên Dev. Khi kiểm tra Test, hệ thống đạt 4/5 câu (80%).
    - **Giới hạn:** Agent vẫn từ chối nhầm 6/20 câu có đáp án. Ở Q16 và Q19, Agent đã tìm được bằng chứng nhưng vẫn tiếp tục tìm kiếm đến khi hết lượt. Cần cải thiện cách Agent quyết định dừng tìm kiếm và trả lời. Ngoài ra, chưa đánh giá TF-IDF trên Test và chưa hoàn tất kiểm tra quyền sử dụng tài liệu khi công khai ứng dụng AI.


