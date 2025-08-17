# CBP Auto Test System - Hướng dẫn sử dụng

## Tổng quan
Hệ thống test tự động cho Cyclic Bandwidth Problem (CBP) bao gồm:
- Script test chính (`auto_test.py`)
- Script batch cho Windows (`run_test.bat`)
- Script shell cho Linux/Mac (`run_test.sh`)
- Script phân tích kết quả (`analyze_results.py`)

## Cấu trúc file

```
Cycling_badwidth/
├── ver_2.py              # CBP solver chính
├── dataset_loader.py     # Module đọc file .mtx
├── auto_test.py          # Script test tự động
├── run_test.bat          # Script Windows
├── run_test.sh           # Script Linux/Mac  
├── analyze_results.py    # Script phân tích kết quả
├── *.mtx                 # File dữ liệu test
├── *.mtx.gz              # File dữ liệu nén
└── results/              # Thư mục kết quả (tạo tự động)
```

## Sử dụng

### Windows:
```cmd
# Cách 1: Double-click file run_test.bat
# Cách 2: Chạy từ command prompt
run_test.bat
```

### Linux/Mac:
```bash
# Cấp quyền thực thi
chmod +x run_test.sh

# Chạy script
./run_test.sh

# Hoặc chạy trực tiếp
bash run_test.sh
```

### Python trực tiếp:
```bash
# Chạy test
python auto_test.py

# Phân tích kết quả
python analyze_results.py cbp_test_results_20240805_143022.csv
```

## Cấu hình

### Trong auto_test.py:
```python
# Thay đổi timeout (giây)
timeout = 600  # 10 phút

# Thêm solver khác
solvers = [
    ("ver_2.py", "ver_2"),
    ("ver_1^1.py", "ver_1^1"),  # Bỏ comment để test thêm
]

# Thay đổi thư mục test
test_directory = "/path/to/your/mtx/files"
```

## Output

### File CSV kết quả:
- `cbp_test_results_YYYYMMDD_HHMMSS.csv`
- Chứa: file_name, solver, vertices, edges, bandwidth, runtime, etc.

### Cột trong CSV:
- **file_name**: Tên file test
- **solver**: Tên solver (ver_2, ver_1^1, etc.)
- **vertices**: Số đỉnh
- **edges**: Số cạnh  
- **max_degree**: Bậc lớn nhất
- **success**: True/False - thành công hay không
- **bandwidth**: Kết quả bandwidth tìm được
- **runtime_sec**: Thời gian chạy (giây)
- **clauses**: Số mệnh đề SAT
- **variables**: Số biến SAT
- **timeout**: True/False - có timeout không
- **error_msg**: Thông báo lỗi (nếu có)

### File báo cáo:
- `cbp_analysis_report_YYYYMMDD_HHMMSS.txt`: Báo cáo chi tiết
- `cbp_analysis_plots_YYYYMMDD_HHMMSS.png`: Biểu đồ phân tích

## Ví dụ kết quả CSV:

```csv
file_name,solver,vertices,edges,bandwidth,runtime_sec,success
can___24.mtx,ver_2,24,68,5,12.34,True
jgl009.mtx,ver_2,9,24,2,0.45,True
ibm32.mtx,ver_2,32,90,7,45.67,True
```

## Troubleshooting

### Lỗi thường gặp:

1. **Python not found**
   - Cài đặt Python: https://python.org
   - Thêm Python vào PATH

2. **Module not found**
   ```bash
   pip install pysat pandas matplotlib seaborn
   ```

3. **File .mtx không tìm thấy**
   - Đặt file .mtx hoặc .mtx.gz vào thư mục gốc
   - Hoặc sửa `test_directory` trong auto_test.py

4. **Timeout quá ngắn**
   - Tăng giá trị `timeout` trong auto_test.py
   - Mặc định: 600 giây (10 phút)

5. **Memory error**
   - Test file nhỏ hơn (< 50 vertices)
   - Tăng RAM cho máy ảo

## Mở rộng

### Thêm solver mới:
```python
# Trong auto_test.py, thêm vào danh sách solvers:
solvers = [
    ("ver_2.py", "ver_2"),
    ("ver_3.py", "ver_3"),        # Solver mới
    ("other_solver.py", "other"), # Solver khác
]
```

### Thay đổi format output:
- Sửa `fieldnames` trong auto_test.py
- Thêm thông tin parsing trong `run_cbp_solver()`

### Thêm metrics:
- Sửa `get_graph_stats()` để tính thêm thông số đồ thị
- Thêm cột mới trong CSV header

## Tips

1. **Chạy test batch nhỏ trước**: Test vài file nhỏ trước khi chạy toàn bộ
2. **Monitor memory**: Đồ thị lớn có thể cần nhiều RAM
3. **Backup kết quả**: CSV files quan trọng nên backup
4. **Parallel testing**: Có thể modify để chạy song song nhiều test

## Liên hệ
Nếu có vấn đề, hãy kiểm tra:
1. Python version (>= 3.6)
2. Required packages đã cài đặt
3. File permissions (Linux/Mac)
4. File paths đúng
