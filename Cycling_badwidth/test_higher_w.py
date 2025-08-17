"""
Test với w=6 để xem có hợp lệ không
"""
import sys
sys.path.append('.')
from verify_assignment import test_and_verify
from dataset_loader import load_mtx_graph_manual

if __name__ == "__main__":
    # Đọc dữ liệu
    n_vertices, graph_edges = load_mtx_graph_manual("can___24.mtx")
    
    print(f"Đồ thị: {n_vertices} đỉnh, {len(graph_edges)} cạnh")
    
    # Test w=6, w=7, w=8
    for w in [6, 7, 8]:
        valid = test_and_verify(n_vertices, graph_edges, w)
        print(f"w={w}: {'VALID' if valid else 'INVALID'}")
        print("-" * 30)
