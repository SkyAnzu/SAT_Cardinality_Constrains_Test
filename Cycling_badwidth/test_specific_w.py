"""
Test riêng biệt cho w=4 và w=5 để debug
"""
import sys
sys.path.append('.')
from ver_2 import generate_clauses_for_cbp, get_X_var, get_K_var
from dataset_loader import load_mtx_graph_manual
from pysat.solvers import Glucose4

def test_single_w(n, edges, w):
    """Test một giá trị w cụ thể"""
    print(f"\n=== TEST w = {w} ===")
    
    clauses, total_vars = generate_clauses_for_cbp(n, edges, w)
    print(f"Số clauses: {len(clauses)}")
    print(f"Số biến: {total_vars}")
    
    # Test với solver
    with Glucose4(bootstrap_with=clauses) as solver:
        is_sat = solver.solve()
        print(f"Kết quả: {'SAT' if is_sat else 'UNSAT'}")
        
        if is_sat:
            model = solver.get_model()
            print("Model found! Kiểm tra một số assignment...")
            
            # Kiểm tra assignment của một số đỉnh
            for i in range(min(5, n)):  # Chỉ check 5 đỉnh đầu
                for j in range(1, n+1):
                    k_var = get_K_var(n, i, j)
                    if k_var <= len(model) and model[k_var-1] > 0:
                        print(f"  Đỉnh {i} được gán nhãn {j}")
                        break
    
    return is_sat

if __name__ == "__main__":
    # Đọc dữ liệu
    n_vertices, graph_edges = load_mtx_graph_manual("can___24.mtx")
    
    print(f"Đồ thị: {n_vertices} đỉnh, {len(graph_edges)} cạnh")
    
    # Test w=5
    result_5 = test_single_w(n_vertices, graph_edges, 5)
    
    # Test w=4  
    result_4 = test_single_w(n_vertices, graph_edges, 4)
    
    print(f"\n=== KẾT QUẢ ===")
    print(f"w=5: {'SAT' if result_5 else 'UNSAT'}")
    print(f"w=4: {'SAT' if result_4 else 'UNSAT'}")
    
    if result_4 and not result_5:
        print("⚠️ BẤT THƯỜNG: w=4 SAT nhưng w=5 UNSAT!")
    elif result_5 and not result_4:
        print("✅ BÌNH THƯỜNG: w=5 SAT, w=4 UNSAT")
