
from pysat.formula import CNF
from pysat.formula import VPool
from pysat.card import CardEnc
from pysat.solvers import Glucose4


def get_var(n, u, l):
    """Ánh xạ (đỉnh u, nhãn l) sang một biến số nguyên (1-based index)."""
    return u * n + (l - 1) + 1

def get_cyclic_dist(n, l1, l2):
    """Tính khoảng cách cyclic giữa hai nhãn."""
    dist = abs(l1 - l2)
    return min(dist, n - dist)


def generate_clauses_for_cbp(n, edges, w, vpool):
    """
    Tạo ra tất cả các mệnh đề CNF cho bài toán CBP với bandwidth w.
    Hàm này sử dụng CardEnc của PySAT để xử lý các ràng buộc đếm.
    """
    clauses = []

    # --- Ràng buộc cơ bản: Dùng CardEnc.equals(bound=1) ---
    # 1. Mỗi đỉnh có đúng một nhãn
    for u in range(n):
        literals = [get_var(n, u, l) for l in range(1, n + 1)]
        cnf = CardEnc.equals(lits=literals, bound=1, vpool=vpool)
        clauses.extend(cnf.clauses)

    # 2. Mỗi nhãn được dùng bởi đúng một đỉnh
    for l in range(1, n + 1):
        literals = [get_var(n, u, l) for u in range(n)]
        cnf = CardEnc.equals(lits=literals, bound=1, vpool=vpool)
        clauses.extend(cnf.clauses)

    # --- Ràng buộc Bandwidth theo 3 trường hợp ---
    unique_edges = list(set(tuple(sorted(edge)) for edge in edges))
    for u, v in unique_edges:
        for k in range(1, n + 1):
            var_uk = get_var(n, u, k)

            # Trường hợp 1: k ở giữax``
            if k > w and k < n - w:
                for l in range(1, k - w):
                    clauses.append([-var_uk, -get_var(n, v, l)])
                for l in range(k + w + 1, n + 1):
                    clauses.append([-var_uk, -get_var(n, v, l)])

            # Trường hợp 2 & 3: k gần đầu/cuối
            else:
                allowed_labels = [l for l in range(1, n + 1) if l != k and get_cyclic_dist(n, k, l) <= w]
                
                if not allowed_labels:
                    clauses.append([-var_uk])
                    continue
                
                allowed_literals = [get_var(n, v, l) for l in allowed_labels]
                
                # Mã hóa logic: IF var_uk THEN ExactlyOne(allowed_literals)
                exo_cnf = CardEnc.equals(lits=allowed_literals, bound=1, vpool=vpool)
                
                # (¬var_uk ∨ C) cho mỗi mệnh đề C trong exo_cnf
                for clause in exo_cnf.clauses:
                    clauses.append([-var_uk] + clause)
    
    return clauses

# =================================================================
# DRIVER CODE
# =================================================================

def solve_cbp(n, edges):
    """
    Hàm chính để giải CBP, tìm kiếm nhị phân trên w.
    """
    best_w = None
    
    low_w, high_w = 1, n // 2
    while low_w <= high_w:
        w = (low_w + high_w) // 2
        print(f"\n===== Đang kiểm tra với bandwidth w = {w} =====")
        
        # VPool quản lý việc tạo các biến cơ bản và biến phụ cho CardEnc
        vpool = VPool()
        
        clauses = generate_clauses_for_cbp(n, edges, w, vpool)
        print(f"   => Đã tạo {len(clauses)} mệnh đề với tổng số {vpool.top} biến.")

        with Glucose4(bootstrap_with=clauses) as solver:
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