# CBP Solver - Cyclic Bandwidth Problem

Solver để giải bài toán Cyclic Bandwidth Problem sử dụng SAT solver.

## Cài đặt thư viện

Chạy script kiểm tra và cài đặt các thư viện cần thiết:

```bash
python check_dependencies.py
```

Hoặc cài đặt thủ công:

```bash
pip install numpy scipy python-sat[pblib,aiger]
```

## Cách sử dụng

### 1. Sử dụng dữ liệu mẫu

```bash
python ver_2.py
```

### 2. Đọc từ file .mtx hoặc .mtx.gz

```bash
python ver_2.py path/to/your/graph.mtx.gz
```

Hoặc:

```bash
python ver_2.py path/to/your/graph.mtx
```

## Định dạng file dữ liệu

Chương trình hỗ trợ đọc file Matrix Market format (.mtx) có thể nén (.mtx.gz).

Định dạng file .mtx:
```
%%MatrixMarket matrix coordinate integer general
% Comments start with %
rows cols entries
i1 j1 [value1]
i2 j2 [value2]
...
```

**Lưu ý**: 
- Chỉ số trong file .mtx thường bắt đầu từ 1, chương trình sẽ tự động chuyển về 0-indexed
- Self-loops sẽ được loại bỏ
- Cạnh trùng lặp sẽ được loại bỏ

## Thuật toán

Solver sử dụng:
- **Encoding**: Chuyển CBP thành bài toán SAT
- **Search Strategy**: Linear search từ upper bound xuống lower bound
- **Bounds**: 
  - Lower bound: ⌈max_degree/2⌉
  - Upper bound: ⌊n/2⌋
- **SAT Solver**: Glucose4

## Output

Chương trình sẽ hiển thị:
1. Thống kê đồ thị (số đỉnh, cạnh, bậc max/min/trung bình)
2. Lower bound và upper bound cho bandwidth
3. Quá trình tìm kiếm với từng giá trị w
4. Kết quả cuối cùng (bandwidth nhỏ nhất tìm được)

## Ví dụ

```bash
# Chạy với file dữ liệu
python ver_2.py data/example.mtx.gz

# Output mẫu:
Đang đọc file: data/example.mtx.gz
Kích thước ma trận: (10, 10)
Số phần tử khác 0: 26
Số đỉnh: 10
Số cạnh: 13

=== THỐNG KÊ ĐỒ THỊ ===
Số đỉnh: 10
Số cạnh: 13
Bậc tối đa: 4
Bậc tối thiểu: 2
Bậc trung bình: 2.60
Mật độ đồ thị: 0.2889

🚀 Bắt đầu giải Cyclic Bandwidth Problem...
   => Lower Bound (LB): 2
   => Upper Bound (UB): 5
   => Search strategy: Linear từ 5 xuống 2

===== Đang kiểm tra với bandwidth w = 5 =====
   => Đã tạo 1250 mệnh đề với tổng số 350 biến.
   => Kết quả của Solver: SAT
   => ✅ Tìm thấy nghiệm với w = 5

==================================================
[*] ✅ TÌM THẤY! Cyclic Bandwidth (w) nhỏ nhất là: 5
==================================================
```

## Lưu ý hiệu năng

- Đồ thị lớn (>50 đỉnh) có thể mất thời gian rất lâu
- Complexity tăng theo cấp số nhân với kích thước đồ thị
- Khuyến nghị test với đồ thị nhỏ trước
