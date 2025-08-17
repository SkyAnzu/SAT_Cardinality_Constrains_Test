from pysat.solvers import Glucose3

def get_var(n, u, l):
    """
    Ánh xạ (đỉnh u, nhãn l) sang một biến số nguyên (1-based index).
    n: tổng số đỉnh.
    u: chỉ số đỉnh (0 đến n-1).
    l: nhãn (1 đến n).
    """
    return u * n + (l - 1) + 1

def at_most_one(literals):
    """
    Tạo mệnh đề At-Most-One bằng Binomial/Pairwise encoding.
    Hàm này không sử dụng itertools.
    Trả về một danh sách các mệnh đề.
    """
    clauses = []
    for i in range(len(literals)):
        for j in range(i + 1, len(literals)):
            clauses.append([-literals[i], -literals[j]])
    return clauses

def exactly_one(literals):
    """
    Tạo mệnh đề Exactly-One.
    Trả về một danh sách các mệnh đề.
    """
    clauses = [literals]  # At least one
    clauses.extend(at_most_one(literals)) # At most one
    return clauses

def get_cyclic_dist(n, l1, l2):
    """Tính khoảng cách cyclic giữa hai nhãn."""
    dist = abs(l1 - l2)
    return min(dist, n - dist)

def generate_clauses_for_cbp(n, edges, w):
    """
    Tạo ra tất cả các mệnh đề CNF cho bài toán CBP với bandwidth w,
    sử dụng mô hình 3 trường hợp.
    Hàm này không sử dụng itertools.
    Trả về một danh sách tất cả các mệnh đề đã được tạo.
    """
    clauses = []

    # Ràng buộc cơ bản: Mỗi đỉnh/nhãn được sử dụng đúng một lần
    # Ràng buộc này đảm bảo kết quả là một hoán vị hợp lệ.
    for i in range(n):
        # Mỗi đỉnh u=i có đúng 1 nhãn
        clauses.extend(exactly_one([get_var(n, i, l) for l in range(1, n + 1)]))
        # Mỗi nhãn l=i+1 được dùng bởi đúng 1 đỉnh
        clauses.extend(exactly_one([get_var(n, u, i + 1) for u in range(n)]))

    # Ràng buộc Bandwidth theo 3 trường hợp
    # Đảm bảo các cạnh được duyệt một chiều để tránh trùng lặp
    unique_edges = list(set(tuple(sorted(edge)) for edge in edges))
    
    for u, v in unique_edges:
        for k in range(1, n + 1):
            var_uk = get_var(n, u, k) # Biến điều kiện: x_u^k

            # Trường hợp 1: k ở giữa
            if k > w and k < n - w:
                for l in range(1, k - w):
                    clauses.append([-var_uk, -get_var(n, v, l)])
                for l in range(k + w + 1, n + 1):
                    clauses.append([-var_uk, -get_var(n, v, l)])

            # Trường hợp 2 & 3: k gần đầu/cuối
            else:
                # 1. Xác định tập các nhãn được phép cho v
                allowed_labels = [l for l in range(1, n + 1) if l != k and get_cyclic_dist(n, k, l) <= w]

                if not allowed_labels:
                    clauses.append([-var_uk])
                    continue
                
                allowed_literals = [get_var(n, v, l) for l in allowed_labels]
                
                # 2. Mã hóa: IF var_uk THEN ExactlyOne(allowed_literals)
                # 2a. Conditional At-Least-One: (¬var_uk ∨ B1 ∨ B2 ...)
                clauses.append([-var_uk] + allowed_literals)
                
                # 2b. Conditional At-Most-One: (¬var_uk ∨ ¬Bi ∨ ¬Bj)
                for i in range(len(allowed_literals)):
                    for j in range(i + 1, len(allowed_literals)):
                        clauses.append([-var_uk, -allowed_literals[i], -allowed_literals[j]])
    
    return clauses


def solve_cbp(n, edges):
    """
    Hàm chính để giải CBP, tìm kiếm nhị phân trên w.
    """
    best_w = None
    
    low_w, high_w = 1, n // 2
    while low_w <= high_w:
        w = (low_w + high_w) // 2
        print(f"\n===== Đang kiểm tra với bandwidth w = {w} =====")

        
        clauses = generate_clauses_for_cbp(n, edges, w)
        print(f"   => Đã tạo {len(clauses)}.")

        with Glucose3(bootstrap_with=clauses) as solver:
            is_sat = solver.solve()
            print(f"   => Kết quả của Solver: {'SAT' if is_sat else 'UNSAT'}")
            if is_sat:
                best_w = w
                high_w = w - 1
            else:
                low_w = w + 1
    return best_w

if __name__ == '__main__':
    n_vertices = 10
    graph_edges = [
        (0, 1), (0, 4), (0, 5), (0, 7), (1, 3), (1, 6), (2, 4), (2, 9),
        (3, 8), (4, 6), (5, 6), (5, 9), (7, 8)
    ]
    final_w = solve_cbp(n_vertices, graph_edges)
    print("\n==================================================")
    if final_w is not None:
        print(f"[*] TÌM THẤY! Cyclic Bandwidth (w) nhỏ nhất là: {final_w}")
    else:
        print("[*] Không tìm thấy lời giải nào.")
    print("==================================================")