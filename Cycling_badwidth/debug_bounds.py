"""
Debug script để kiểm tra bounds checking trong constraint edges của ver_2.py
"""

def debug_edge_constraint_bounds(n, w):
    """Debug bounds checking cho edge constraints"""
    print(f"\n=== DEBUG EDGE CONSTRAINT BOUNDS: n={n}, w={w} ===")
    
    # Phân tích các trường hợp
    case1_range = []
    case2_range = []
    case3_range = []
    
    for k in range(1, n + 1):
        # Trường hợp 1: w < k < n-w
        if w < k < n-w:
            case1_range.append(k)
        
        # Trường hợp 2: 1 <= k <= w
        elif 1 <= k <= w:
            case2_range.append(k)
        
        # Trường hợp 3: n-w <= k <= n
        elif n-w <= k <= n:
            case3_range.append(k)
    
    print(f"Trường hợp 1 (w < k < n-w): k ∈ {case1_range}")
    print(f"Trường hợp 2 (1 ≤ k ≤ w): k ∈ {case2_range}")
    print(f"Trường hợp 3 (n-w ≤ k ≤ n): k ∈ {case3_range}")
    
    # Kiểm tra bounds cho từng trường hợp
    print(f"\n--- BOUNDS CHECKING ---")
    
    # Case 1: bounds luôn OK
    if case1_range:
        print(f"\nCase 1: k ∈ {case1_range}")
        for k in case1_range:
            bound1 = k - w  # X_v,k-w
            bound2 = k + w + 1  # X_v,k+w+1
            print(f"  k={k}: X_v,{bound1} ∧ ¬X_v,{bound2}")
            print(f"    Bounds check: {bound1} ≥ 1? {bound1 >= 1}, {bound2} ≤ {n}? {bound2 <= n}")
    
    # Case 2: cần check bounds
    if case2_range:
        print(f"\nCase 2: k ∈ {case2_range}")
        for k in case2_range:
            bound1 = n - w + k  # X_v,n-w+k
            bound2 = w + k + 1  # X_v,w+k+1
            print(f"  k={k}: X_v,{bound1} ∨ ¬X_v,{bound2}")
            
            # Check bounds
            valid1 = bound1 >= 1
            valid2 = bound2 <= n
            print(f"    Bound 1: {bound1} ≥ 1? {valid1}")
            print(f"    Bound 2: {bound2} ≤ {n}? {valid2}")
            
            # Count valid literals
            valid_literals = int(valid1) + int(valid2)
            print(f"    Valid literals: {valid_literals}/2")
            if valid_literals == 0:
                print(f"    ⚠️  NO VALID LITERALS - clause will be empty!")
    
    # Case 3: cần check bounds
    if case3_range:
        print(f"\nCase 3: k ∈ {case3_range}")
        for k in case3_range:
            bound1 = k - w - 1  # X_v,k-w-1
            bound2 = w + k - n  # X_v,w+k-n
            print(f"  k={k}: ¬X_v,{bound1} ∨ X_v,{bound2}")
            
            # Check bounds
            valid1 = bound1 >= 1
            valid2 = bound2 >= 1
            print(f"    Bound 1: {bound1} ≥ 1? {valid1}")
            print(f"    Bound 2: {bound2} ≥ 1? {valid2}")
            
            # Count valid literals
            valid_literals = int(valid1) + int(valid2)
            print(f"    Valid literals: {valid_literals}/2")
            if valid_literals == 0:
                print(f"    ⚠️  NO VALID LITERALS - clause will be empty!")

def analyze_problematic_cases():
    """Phân tích các trường hợp có thể gây vấn đề"""
    print(f"\n{'='*60}")
    print("PHÂN TÍCH CÁC TRƯỜNG HỢP CÓ THỂ GÂY VẤN ĐỀ")
    print(f"{'='*60}")
    
    test_cases = [
        (4, 2),   # n=4, w=2 - graph nhỏ
        (6, 3),   # n=6, w=3 - nguy hiểm: w+k+1 có thể > n
        (8, 4),   # n=8, w=4 - nguy hiểm
        (10, 5),  # n=10, w=5 - nguy hiểm  
        (24, 12), # n=24, w=12 - w=n/2, rất nguy hiểm
        (24, 5),  # can___24.mtx case
    ]
    
    for n, w in test_cases:
        debug_edge_constraint_bounds(n, w)
        
        # Check overlap between cases
        case1_condition = lambda k: w < k < n-w
        case2_condition = lambda k: 1 <= k <= w
        case3_condition = lambda k: n-w <= k <= n
        
        overlaps = []
        gaps = []
        
        for k in range(1, n + 1):
            matches = []
            if case1_condition(k):
                matches.append("1")
            if case2_condition(k):
                matches.append("2")
            if case3_condition(k):
                matches.append("3")
            
            if len(matches) > 1:
                overlaps.append((k, matches))
            elif len(matches) == 0:
                gaps.append(k)
        
        if overlaps:
            print(f"  ⚠️  OVERLAPS: {overlaps}")
        if gaps:
            print(f"  ⚠️  GAPS: k ∈ {gaps} không thuộc case nào!")
        
        print(f"  Range coverage: Case1={w+1}-{n-w-1}, Case2=1-{w}, Case3={n-w}-{n}")
        print()

if __name__ == "__main__":
    analyze_problematic_cases()
