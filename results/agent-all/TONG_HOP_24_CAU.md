# Day 07 — Tổng hợp đánh giá Agent cho 24 câu

**Nguồn:** trace Dev 17 câu, trace Test 7 câu; review thủ công đề xuất đã điền từ các trace này. Không chạy lại model và không thay đổi điểm Test.

| Chỉ số | Dev | Test | Toàn bộ |
|---|---:|---:|---:|
| Số câu | 17 | 7 | 24 |
| Tool use | 17/17 | 7/7 | 24/24 |
| Grounded: điểm 0/1/2 | 2/1/12 | 4/0/1 | 6/1/13 |
| Grounded trung bình /2 | 1.67 | 0.40 | 1.35 |
| Citation hợp lệ | 15/15 | 1/1 | 16/16 |
| Câu trả lời có citation | 13/13 | 1/1 | 14/14 |
| Abstention đúng | 2/2 | 2/2 | 4/4 |
| Từ chối nhầm | 2/15 | 4/5 | 6/20 |
| Provider errors | 0 | 0 | 0 |

**Tổng search calls:** 34 (Dev 21, Test 13).

## Bảng đầy đủ 24 câu

| ID | Split | Loại | Status | Search | Điểm /2 | Citation hỗ trợ | Nhận xét |
|---|---|---|---|---:|---:|---|---|
| Q01 | dev | Có đáp án | answered | 1 | 2 | 2/2 | Trả lời với citation; chấm theo trace và context. |
| Q02 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q03 | dev | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; search_limit, không chọn được chunk giải thích tham số end. |
| Q04 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q05 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q06 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q07 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q08 | dev | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; search_limit, bỏ lỡ chunk định nghĩa chuỗi. |
| Q09 | dev | Có đáp án | answered | 1 | 2 | 2/2 | Trả lời với citation; chấm theo trace và context. |
| Q10 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q11 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q12 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q13 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q14 | dev | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q15 | dev | Có đáp án | answered | 1 | 1 | 1/1 | Câu trả lời đúng một phần; diễn đạt về floor division chưa đủ chính xác. |
| Q16 | test | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; context đã có giải thích docstring nhưng vẫn search_limit. |
| Q17 | test | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; context thiếu phần giải thích đầy đủ về phiên dịch mã. |
| Q18 | test | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; chunk đúng nằm top-3 nhưng không vào context. |
| Q19 | test | Có đáp án | abstain | 2 | 0 | 0/0 | Từ chối nhầm; context đã có cả // và % nhưng vẫn search_limit. |
| Q20 | test | Có đáp án | answered | 1 | 2 | 1/1 | Trả lời với citation; chấm theo trace và context. |
| Q21 | dev | Thiếu bằng chứng | abstain | 2 | — | 0/0 | Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus. |
| Q22 | dev | Thiếu bằng chứng | abstain | 2 | — | 0/0 | Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus. |
| Q23 | test | Thiếu bằng chứng | abstain | 2 | — | 0/0 | Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus. |
| Q24 | test | Thiếu bằng chứng | abstain | 2 | — | 0/0 | Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus. |

## Câu hỏi và câu trả lời / citations

### Q01 — Why is Python popular for practical programming?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 5.19 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True, True].
- **Citation IDs:** python_openstax_19_fixed_1, python_openstax_19_fixed_2.
- **Câu trả lời Agent:** Python is popular for practical programming for several reasons:

1. **Extensive Libraries**: Python has many libraries available for various tasks, which makes it suitable for real-world applications. The Standard Library provides tools for common computing problems, such as data extraction and report generation. Additionally, the community has developed numerous other libraries, like Pandas for data analysis, enhancing its functionality [python_openstax_19_fixed_1].

2. **Concise and Straightforward Syntax**: Python's syntax is designed to be concise and easy to understand, making it more accessible compared to other programming languages. This simplicity allows programmers to write code more efficiently and with fewer lines [python_openstax_19_fixed_2].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q02 — What does the sep option in print() control?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 3.75 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_21_fixed_0.
- **Câu trả lời Agent:** The `sep` option in the `print()` function controls the string that is used to separate multiple values when they are printed. By default, this separator is a space character, but the `sep` option allows you to change this behavior to use a different string instead [python_openstax_21_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q03 — How do you prevent print() from automatically starting a new line?
- **Split:** dev; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 3.64 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; search_limit, không chọn được chunk giải thích tham số end.

### Q04 — What does input() do in a Python program?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 3.20 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_22_fixed_1.
- **Câu trả lời Agent:** The `input()` function in a Python program is used to read one line of input from the user. It consists of three parts: a variable that stores the input value, the `input()` function itself, and a prompt that indicates what the user should enter. The input received is stored in memory and can be accessed later using the specified variable name [python_openstax_22_fixed_1].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q05 — What is the meaning of the assignment operator = in Python?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.24 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_44_fixed_0.
- **Câu trả lời Agent:** The assignment operator `=` in Python is used to assign or update the value of a variable. Variables in Python begin to exist when they are assigned for the first time [python_openstax_44_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q06 — What naming style does the Python style guide recommend for variables?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.32 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_25_fixed_0.
- **Câu trả lời Agent:** Python's style guide recommends writing variable names in snake case, which is all lowercase with underscores in between each word, such as `first_name` or `total_price` [python_openstax_25_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q07 — Can a Python variable name begin with a digit?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.55 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_25_fixed_0.
- **Câu trả lời Agent:** A Python variable name cannot start with a digit. For example, "101class" is considered invalid because it begins with a digit. Variable names can consist of letters, digits, and underscores, but must start with a letter or an underscore [python_openstax_25_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q08 — How does the book define a Python string?
- **Split:** dev; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 2.88 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; search_limit, bỏ lỡ chunk định nghĩa chuỗi.

### Q09 — What is string concatenation?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.97 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True, True].
- **Citation IDs:** python_openstax_28_fixed_1, python_openstax_69_fixed_3.
- **Câu trả lời Agent:** String concatenation is the process of joining two or more strings together to form a single string. In Python, this is typically done using the concatenation operator (+). For example, using the expression "A" + "part" produces the string "Apart" [python_openstax_28_fixed_1]. Additionally, Python can automatically concatenate multiple strings without requiring the + operator in certain situations [python_openstax_69_fixed_3].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q10 — Which two basic numeric formats are introduced in the textbook?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.14 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_30_fixed_0.
- **Câu trả lời Agent:** The two basic numeric formats introduced in the textbook are integer and floating-point. An integer represents a whole number, while a floating-point format represents a decimal number [python_openstax_30_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q11 — Which is evaluated first: multiplication or addition?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.64 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_32_fixed_0.
- **Câu trả lời Agent:** Multiplication is evaluated before addition in arithmetic expressions. For example, in the expression \( 2 * 3 + 1 \), the multiplication \( 2 * 3 \) is performed first, resulting in \( 6 + 1 \), which equals \( 7 \). This precedence is confirmed by the operator precedence rules, where multiplication takes precedence over addition [python_openstax_32_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q12 — What does the caret symbol in a SyntaxError message indicate?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.44 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_34_fixed_0.
- **Câu trả lời Agent:** The caret symbol (^) in a SyntaxError message indicates where Python found the error in the code. It shows the exact position in the line where the issue occurs. However, it's important to note that sometimes the actual error may be located one or two lines before where the caret is shown, as Python may not have detected the error until that point in the code [python_openstax_34_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q13 — What character begins a Python comment?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.07 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_37_fixed_1.
- **Câu trả lời Agent:** Trong Python, một chú thích bắt đầu bằng ký tự hash (#). Tất cả văn bản từ ký tự hash đến cuối dòng sẽ bị bỏ qua khi chương trình chạy [python_openstax_37_fixed_1].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q14 — In Chapter 2, what does REPL stand for?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.24 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_49_fixed_0.
- **Câu trả lời Agent:** In Chapter 2, REPL stands for "read-eval-print loop," which describes the repetitive nature of a shell where it reads input code, evaluates it, prints any results, and then loops back to read more code again [python_openstax_49_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q15 — How does true division differ from floor division in Python?
- **Split:** dev; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 3.49 giây.
- **Đánh giá:** answer_grade=1; citation_support=[True].
- **Citation IDs:** python_openstax_59_fixed_0.
- **Câu trả lời Agent:** True division in Python, represented by the operator `/`, converts numbers to floats before performing the division. For example, `7 / 4` results in `1.75` because it evaluates as `7.0 / 4.0` [python_openstax_59_fixed_0]. 

In contrast, floor division, represented by the operator `//`, computes the quotient, which is the number of times the divisor can fit into the dividend without considering the remainder. For instance, `7 // 4` results in `1` [python_openstax_59_fixed_0]. 

Thus, the key difference is that true division returns a float, while floor division returns an integer representing the whole number part of the division.
- **Ghi chú:** Câu trả lời đúng một phần; diễn đạt về floor division chưa đủ chính xác.

### Q16 — What is a docstring used for?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 7.81 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; context đã có giải thích docstring nhưng vẫn search_limit.

### Q17 — In Chapter 2, why is an interpreter needed?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 3.51 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; context thiếu phần giải thích đầy đủ về phiên dịch mã.

### Q18 — How does the up arrow key behave in the Python shell history?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 3.44 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; chunk đúng nằm top-3 nhưng không vào context.

### Q19 — How do floor division and modulo help convert centimeters into meters and leftover centimeters?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 4.34 giây.
- **Đánh giá:** answer_grade=0; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối nhầm; context đã có cả // và % nhưng vẫn search_limit.

### Q20 — In Chapter 2, what does math.floor(x) compute?
- **Split:** test; **Trạng thái:** answered; **Search calls:** 1; **Thời gian:** 2.31 giây.
- **Đánh giá:** answer_grade=2; citation_support=[True].
- **Citation IDs:** python_openstax_64_fixed_0.
- **Câu trả lời Agent:** The function `math.floor(x)` computes the largest integer less than or equal to `x`. For example, `math.floor(7.4)` returns `7`, and `math.floor(-7.4)` returns `-8` [python_openstax_64_fixed_0].
- **Ghi chú:** Đối chiếu citation với nội dung context trong trace.

### Q21 — How does Python's asyncio event loop schedule coroutines?
- **Split:** dev; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 2.91 giây.
- **Đánh giá:** abstention_correct=true; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus.

### Q22 — How does multiprocessing.Pool distribute tasks across processes?
- **Split:** dev; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 2.89 giây.
- **Đánh giá:** abstention_correct=true; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus.

### Q23 — How do you create and activate a virtual environment using venv?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 6.92 giây.
- **Đánh giá:** abstention_correct=true; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus.

### Q24 — How does Python's garbage collector detect reference cycles?
- **Split:** test; **Trạng thái:** abstain; **Search calls:** 2; **Thời gian:** 6.60 giây.
- **Đánh giá:** abstention_correct=true; citation_support=[].
- **Citation IDs:** Không có.
- **Câu trả lời Agent:** Không đủ bằng chứng để trả lời.
- **Ghi chú:** Từ chối đúng theo phạm vi corpus đã rà soát; cần xác nhận thủ công nếu đổi corpus.

## Cách dùng với repo

Copy hai file JSON gộp vào `results/agent-all/` nếu muốn lưu đủ 24 câu; **giữ nguyên** `results/agent-dev/` và `results/agent-test/` vì `agent_metrics.py` có `--split` chỉ nhận `dev` hoặc `test`.

Lưu ý: Chỉ số citation validity chấm theo hỗ trợ nội dung của nguồn; chỉ số 100% trên số citation được tạo không bao hàm những câu `abstain`.

Các nhãn đánh giá là bản đề xuất từ trace; người nộp cần rà soát và chịu trách nhiệm xác nhận nhãn đánh giá cuối cùng.
