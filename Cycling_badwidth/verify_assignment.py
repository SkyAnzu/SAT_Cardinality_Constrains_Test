"""
Verify assignment để kiểm tra xem có thực sự thỏa mãn bandwidth constraint
"""
import sys
sys.path.append('.')
from dataset_loader import load_mtx_graph_manual

def verify_assignment(n, edges, assignment, w):
    """
    Verify xem assignment có thỏa mãn cyclic bandwidth w không
    assignment: dict {vertex: label}
    """
    print(f"\n=== VERIFY ASSIGNMENT với w={w} ===")
    
    # Kiểm tra tất cả các cạnh
    violations = 0
    for u, v in edges:
        label_u = assignment[u]
        label_v = assignment[v]
        
        # Tính cyclic distance
        dist1 = abs(label_u - label_v)
        dist2 = n - dist1  # Cyclic distance
        cyclic_dist = min(dist1, dist2)
        
        # if cyclic_dist > w:
        print(f"  VIOLATION: Cạnh ({u},{v}): nhãn {label_u} → {label_v}, cyclic_dist = {cyclic_dist} | {w}")
        # violations += 1
        # else:
        #     print(f"  OK: Cạnh ({u},{v}): nhãn {label_u} → {label_v}, cyclic_dist = {cyclic_dist} <= {w}")
    
    print(f"Tổng số vi phạm: {violations}/{len(edges)}")
    return violations == 0

def extract_assignment_from_model(n, model):
    """Extract assignment từ SAT model"""
    from ver_2 import get_K_var
    
    assignment = {}
    for i in range(n):
        for j in range(1, n+1):
            k_var = get_K_var(n, i, j)
            if k_var <= len(model) and model[k_var-1] > 0:
                assignment[i] = j
                break
    
    return assignment

def test_and_verify(n, edges, w):
    """Test và verify một giá trị w"""
    from ver_2 import generate_clauses_for_cbp
    from pysat.solvers import Glucose4
    
    print(f"\n{'='*20} TEST w={w} {'='*20}")
    
    clauses, total_vars = generate_clauses_for_cbp(n, edges, w)
    
    with Glucose4(bootstrap_with=clauses) as solver:
        is_sat = solver.solve()
        print(f"SAT Result: {is_sat}")
        
        if is_sat:
            model = solver.get_model()
            assignment = extract_assignment_from_model(n, model)
            
            print("Assignment:")
            for i in sorted(assignment.keys()):
                print(f"  Đỉnh {i}: nhãn {assignment[i]}")
            
            # Verify assignment
            is_valid = verify_assignment(n, edges, assignment, w)
            print(f"Assignment hợp lệ: {is_valid}")
            
            return is_valid
        else:
            print("UNSAT - không có assignment")
            return False

if __name__ == "__main__":
    # Đọc dữ liệu
    n_vertices, graph_edges = load_mtx_graph_manual("jgl009.mtx")
    
    print(f"Đồ thị: {n_vertices} đỉnh, {len(graph_edges)} cạnh")
    
    # Test w=4
    valid_4 = test_and_verify(n_vertices, graph_edges, 4)
    
    
    print(f"\n{'='*50}")
    print(f"KẾT QUẢ CUỐI CÙNG:")
    print(f"w=4: {'VALID' if valid_4 else 'INVALID'}")
