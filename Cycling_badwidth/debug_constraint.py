"""
Debug script để kiểm tra logic bandwidth constraint
"""

def debug_bandwidth_constraint(n, w, k):
    """Debug logic cho các trường hợp bandwidth constraint"""
    print(f"\n=== DEBUG: n={n}, w={w}, k={k} ===")
    
    # Trường hợp 1: n-w > k > w
    case1_condition = w < k < n-w
    print(f"Trường hợp 1: {w} < {k} < {n-w} = {case1_condition}")
    if case1_condition:
        print(f"  → X_v,{k-w} ∧ ¬X_v,{k+w+1}")
        print(f"  → Kiểm tra bounds: k-w={k-w} >= 1? {k-w >= 1}")
        print(f"  → Kiểm tra bounds: k+w+1={k+w+1} <= {n}? {k+w+1 <= n}")
    
    # Trường hợp 2: w >= k >= 1  
    case2_condition = 1 <= k <= w
    print(f"Trường hợp 2: 1 <= {k} <= {w} = {case2_condition}")
    if case2_condition:
        print(f"  → X_v,{n-w+k} ∨ ¬X_v,{w+k+1}")
        print(f"  → Kiểm tra bounds: n-w+k={n-w+k} >= 1? {n-w+k >= 1}")
        print(f"  → Kiểm tra bounds: w+k+1={w+k+1} <= {n}? {w+k+1 <= n}")
    
    # Trường hợp 3: n >= k >= n-w
    case3_condition = n-w <= k <= n
    print(f"Trường hợp 3: {n-w} <= {k} <= {n} = {case3_condition}")
    if case3_condition:
        print(f"  → ¬X_v,{k-w-1} ∨ X_v,{w+k-n}")
        print(f"  → Kiểm tra bounds: k-w-1={k-w-1} >= 1? {k-w-1 >= 1}")
        print(f"  → Kiểm tra bounds: w+k-n={w+k-n} >= 1? {w+k-n >= 1}")

if __name__ == "__main__":
    # Test với đồ thị 24 đỉnh
    n = 24
    
    print("=== KIỂM TRA VỚI w=4 ===")
    w = 4
    for k in range(1, n+1):
        debug_bandwidth_constraint(n, w, k)
        if k > 10:  # Chỉ test một số giá trị đầu
            break
    
    print("\n" + "="*50)
    print("=== KIỂM TRA VỚI w=5 ===")
    w = 5
    for k in range(1, n+1):
        debug_bandwidth_constraint(n, w, k)
        if k > 10:  # Chỉ test một số giá trị đầu
            break
