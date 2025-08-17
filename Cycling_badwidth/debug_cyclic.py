"""
Debug constraint logic với ví dụ cụ thể
"""

def debug_cyclic_constraint():
    """
    Debug với ví dụ đơn giản: đồ thị 2 đỉnh, 1 cạnh
    Đỉnh 0 gán nhãn 1, đỉnh 1 gán nhãn 3
    Cyclic distance = min(|1-3|, 4-|1-3|) = min(2, 2) = 2
    """
    n = 4  # 4 đỉnh để có thể test
    u, v = 0, 1  # Cạnh (0,1)
    w = 2  # Test với bandwidth w=2
    
    print(f"=== DEBUG: n={n}, cạnh ({u},{v}), w={w} ===")
    print(f"Giả sử: đỉnh {u} gán nhãn 1, đỉnh {v} gán nhãn 3")
    print(f"Cyclic distance = min(|1-3|, {n}-|1-3|) = min(2, 2) = 2")
    print(f"Với w={w}: 2 <= {w}? {2 <= w} {'✓' if 2 <= w else '✗'}")
    
    # Kiểm tra constraint cho u=0, k=1 (đỉnh 0 gán nhãn 1)
    k = 1
    print(f"\n--- Kiểm tra constraint cho K_{u},{k} (đỉnh {u} gán nhãn {k}) ---")
    
    # Xác định trường hợp
    case1 = w < k < n-w  # 2 < 1 < 2 = False
    case2 = 1 <= k <= w  # 1 <= 1 <= 2 = True  
    case3 = n-w <= k <= n  # 2 <= 1 <= 4 = False
    
    print(f"Trường hợp 1 (w < k < n-w): {w} < {k} < {n-w} = {case1}")
    print(f"Trường hợp 2 (1 ≤ k ≤ w): 1 ≤ {k} ≤ {w} = {case2}")
    print(f"Trường hợp 3 (n-w ≤ k ≤ n): {n-w} ≤ {k} ≤ {n} = {case3}")
    
    if case2:
        print(f"\n→ Áp dụng trường hợp 2: K_{u},{k} → X_{v},{n-w+k} ∨ ¬X_{v},{w+k+1}")
        j1 = n-w+k  # 4-2+1 = 3
        j2 = w+k+1  # 2+1+1 = 4
        print(f"→ K_{u},{k} → X_{v},{j1} ∨ ¬X_{v},{j2}")
        print(f"→ K_0,1 → X_1,3 ∨ ¬X_1,4")
        
        print(f"\nNếu đỉnh 1 gán nhãn 3:")
        print(f"- X_1,3 = true (vì 3 ≥ 3)")
        print(f"- X_1,4 = false (vì 3 < 4)")
        print(f"- ¬X_1,4 = true")
        print(f"- X_1,3 ∨ ¬X_1,4 = true ∨ true = true ✓")
        print(f"→ Constraint thỏa mãn!")
        
        print(f"\nNhưng cyclic distance = 2 ≤ w={w}, nên assignment hợp lệ!")
        print(f"Vậy tại sao verify lại báo vi phạm?")

if __name__ == "__main__":
    debug_cyclic_constraint()
