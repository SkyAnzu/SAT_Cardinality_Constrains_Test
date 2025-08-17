"""
Kiểm tra constraint cụ thể cho một vi phạm trong kết quả SAT
"""
import sys
sys.path.append('.')

def check_specific_violation():
    """
    Kiểm tra vi phạm cụ thể: Cạnh (17,0): nhãn 23 → 7, cyclic_dist = 8 > 4
    """
    n = 24
    w = 4
    u, v = 17, 0  # Cạnh
    label_u, label_v = 23, 7  # Nhãn từ SAT solver
    
    print(f"=== KIỂM TRA VI PHẠM CỤ THỂ ===")
    print(f"Cạnh ({u},{v}): nhãn {label_u} → {label_v}")
    print(f"Cyclic distance = min(|{label_u}-{label_v}|, {n}-|{label_u}-{label_v}|)")
    
    dist1 = abs(label_u - label_v)  # |23-7| = 16
    dist2 = n - dist1  # 24-16 = 8
    cyclic_dist = min(dist1, dist2)  # min(16, 8) = 8
    
    print(f"Cyclic distance = min({dist1}, {dist2}) = {cyclic_dist}")
    print(f"w = {w}, vi phạm: {cyclic_dist} > {w}? {cyclic_dist > w}")
    
    # Kiểm tra constraint cho K_u,k với k = label_u = 23
    k = label_u
    print(f"\n--- Kiểm tra constraint K_{u},{k} ---")
    
    # Xác định trường hợp
    case1 = w < k < n-w  # 4 < 23 < 20 = False (vì 23 > 20)
    case2 = 1 <= k <= w  # 1 <= 23 <= 4 = False
    case3 = n-w <= k <= n  # 20 <= 23 <= 24 = True
    
    print(f"Trường hợp 1: {w} < {k} < {n-w} = {case1}")
    print(f"Trường hợp 2: 1 ≤ {k} ≤ {w} = {case2}")  
    print(f"Trường hợp 3: {n-w} ≤ {k} ≤ {n} = {case3}")
    
    if case3:
        print(f"\n→ Áp dụng trường hợp 3: K_{u},{k} → ¬X_{v},{k-w-1} ∨ X_{v},{w+k-n}")
        j1 = k-w-1  # 23-4-1 = 18
        j2 = w+k-n  # 4+23-24 = 3
        
        print(f"→ K_{u},{k} → ¬X_{v},{j1} ∨ X_{v},{j2}")
        print(f"→ K_17,23 → ¬X_0,18 ∨ X_0,3")
        
        print(f"\nVới đỉnh {v} gán nhãn {label_v}:")
        print(f"- X_0,18 = false (vì {label_v} < 18)")
        print(f"- X_0,3 = true (vì {label_v} ≥ 3)")
        print(f"- ¬X_0,18 ∨ X_0,3 = true ∨ true = true ✓")
        
        print(f"\n🤔 Constraint thỏa mãn nhưng cyclic distance vi phạm!")
        print(f"Điều này có nghĩa là constraint KHÔNG ĐÚNG!")
    
    # Cũng kiểm tra constraint ngược lại K_v,label_v
    print(f"\n--- Kiểm tra constraint ngược K_{v},{label_v} ---")
    k2 = label_v  # 7
    
    case1_rev = w < k2 < n-w  # 4 < 7 < 20 = True
    case2_rev = 1 <= k2 <= w  # 1 <= 7 <= 4 = False
    case3_rev = n-w <= k2 <= n  # 20 <= 7 <= 24 = False
    
    print(f"Trường hợp 1: {w} < {k2} < {n-w} = {case1_rev}")
    print(f"Trường hợp 2: 1 ≤ {k2} ≤ {w} = {case2_rev}")
    print(f"Trường hợp 3: {n-w} ≤ {k2} ≤ {n} = {case3_rev}")
    
    if case1_rev:
        print(f"\n→ Áp dụng trường hợp 1: K_{v},{k2} → X_{u},{k2-w} ∧ ¬X_{u},{k2+w+1}")
        j3 = k2-w    # 7-4 = 3
        j4 = k2+w+1  # 7+4+1 = 12
        
        print(f"→ K_{v},{k2} → X_{u},{j3} ∧ ¬X_{u},{j4}")
        print(f"→ K_0,7 → X_17,3 ∧ ¬X_17,12")
        
        print(f"\nVới đỉnh {u} gán nhãn {label_u}:")
        print(f"- X_17,3 = true (vì {label_u} ≥ 3)")
        print(f"- X_17,12 = true (vì {label_u} ≥ 12)")
        print(f"- ¬X_17,12 = false")
        print(f"- X_17,3 ∧ ¬X_17,12 = true ∧ false = FALSE ❌")
        
        print(f"\n💡 Constraint này VI PHẠM! Đây chính là lý do!")

if __name__ == "__main__":
    check_specific_violation()
