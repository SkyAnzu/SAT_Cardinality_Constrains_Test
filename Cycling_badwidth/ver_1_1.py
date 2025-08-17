
from pysat.formula import CNF
from pysat.card import CardEnc
from pysat.solvers import Glucose4


def get_var(n, u, l):
    """Ánh xạ (đỉnh u, nhãn l) sang một biến số nguyên (1-based index)."""
    return u * n + (l - 1) + 1



def generate_clauses_for_cbp(n, edges, w):
    """
    Tạo ra tất cả các mệnh đề CNF cho bài toán CBP với bandwidth w.
    Hàm này sử dụng CardEnc của PySAT để xử lý các ràng buộc đếm.
    """
    clauses = []
    top_id = n * n + 1  # Biến đầu tiên cho các biến phụ

    # --- Ràng buộc cơ bản: Dùng CardEnc.equals(bound=1) ---
    # 1. Mỗi đỉnh có đúng một nhãn
    for u in range(n):
        literals = [get_var(n, u, l) for l in range(1, n + 1)]
        cnf = CardEnc.equals(lits=literals, bound=1, top_id=top_id)
        clauses.extend(cnf.clauses)
        top_id = cnf.nv + 1  # Cập nhật top_id cho lần tiếp theo

    # 2. Mỗi nhãn được dùng bởi đúng một đỉnh
    for l in range(1, n + 1):
        literals = [get_var(n, u, l) for u in range(n)]
        cnf = CardEnc.equals(lits=literals, bound=1, top_id=top_id)
        clauses.extend(cnf.clauses)
        top_id = cnf.nv + 1  # Cập nhật top_id cho lần tiếp theo

    # --- Ràng buộc Bandwidth theo 3 trường hợp ---
    unique_edges = list(set(tuple(sorted(edge)) for edge in edges))
    for u, v in unique_edges:
        for k in range(1, n + 1):
            var_uk = get_var(n, u, k)

            # Trường hợp 1: n - w > k > w
            if k > w and k < n - w:
                for l in range(1, k - w):
                    clauses.append([-var_uk, -get_var(n, v, l)])
                for l in range(k + w + 1, n + 1):
                    clauses.append([-var_uk, -get_var(n, v, l)])

            # Trường hợp 2: w >= k >= 1
            elif 1 <= k <= w:
                # Theo ảnh: x_u^k → (Σx_v^l = 1) ∨ (Σx_v^l' = 1) với l = 1 to k+w và l' = n-w+k to n
                literals_1 = [get_var(n, v, l) for l in range(1, min(k+w+1, n+1))]
                literals_2 = [get_var(n, v, l) for l in range(max(n-w+k, 1), n+1)]
                
                # Loại bỏ trùng lặp nếu hai khoảng chồng chéo
                all_literals = list(set(literals_1 + literals_2))
                
                # Mã hóa: IF var_uk THEN ExactlyOne(all_literals)
                if len(all_literals) > 1:
                    cnf = CardEnc.equals(lits=all_literals, bound=1, top_id=top_id)
                    top_id = cnf.nv + 1
                    for clause in cnf.clauses:
                        clauses.append([-var_uk] + clause)
                elif len(all_literals) == 1:
                    clauses.append  ([-var_uk, all_literals[0]])

            # Trường hợp 3: n >= k >= n-w
            elif n-w <= k <= n:
                # Theo ảnh: x_u^k → (Σx_v^l = 1) ∨ (Σx_v^l' = 1) với l = 1 to w+k-n và l' = k-w to n
                literals_1 = [get_var(n, v, l) for l in range(1, min(w+k-n+1, n+1))]
                literals_2 = [get_var(n, v, l) for l in range(max(k-w, 1), n+1)]
                
                # Loại bỏ trùng lặp nếu hai khoảng chồng chéo
                all_literals = list(set(literals_1 + literals_2))
                
                # Mã hóa: IF var_uk THEN ExactlyOne(all_literals)
                if len(all_literals) > 1:
                    cnf = CardEnc.equals(lits=all_literals, bound=1, top_id=top_id)
                    top_id = cnf.nv + 1
                    for clause in cnf.clauses:
                        clauses.append([-var_uk] + clause)
                elif len(all_literals) == 1:
                    clauses.append([-var_uk, all_literals[0]])
    return clauses, top_id - 1

# =================================================================
# DRIVER CODE
# =================================================================

def solve_cbp(n, edges):
    """
    Hàm chính để giải CBP, tìm kiếm tuyến tính từ LB lên UB.
    Khi gặp SAT đầu tiên, đó là w tối ưu.
    """
    # Tính bậc lớn nhất của đồ thị
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    max_degree = max(degree)
    
    # Tính low_w (LB) và high_w (UB)
    import math
    low_w = math.ceil(max_degree / 2)  # Lower bound
    high_w = n // 2  # Upper bound = floor(n/2)
    
    print(f"   => Lower Bound (LB): {low_w}")
    print(f"   => Upper Bound (UB): {high_w}")
    print(f"   => Search strategy: Linear from {low_w} up to {high_w} until first SAT")
    
    best_w = None
    
    # Linear search từ LB lên UB - khi gặp SAT đầu tiên, đó là tối ưu
    for w in range(low_w, high_w + 1):
        print(f"\n===== Đang kiểm tra với bandwidth w = {w} =====")
        
        clauses, total_vars = generate_clauses_for_cbp(n, edges, w)
        print(f"   => Đã tạo {len(clauses)} mệnh đề với tổng số {total_vars} biến.")

        with Glucose4(bootstrap_with=clauses) as solver:
            is_sat = solver.solve()
            print(f"   => Kết quả của Solver: {'SAT' if is_sat else 'UNSAT'}")
            if is_sat:
                print(f"   => ✅ Tìm thấy nghiệm với w = {w}")
                best_w = w
                break  # Tìm thấy w nhỏ nhất, dừng ngay
            else:
                print(f"   => ❌ Không có nghiệm với w = {w}")
    
    if best_w is None:
        print(f"\n   => ❌ Không tìm thấy nghiệm nào trong khoảng [{low_w}, {high_w}]")
        
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