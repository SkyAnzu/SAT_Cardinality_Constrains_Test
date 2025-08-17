from pysat.formula import CNF
from pysat.card import CardEnc
from pysat.solvers import Glucose4

import math

def get_X_var(n, i, j):
    """Map variable X_ij: vertex i assigned label <= j"""
    if i < 0 or i >= n or j < 1 or j > n:
        raise ValueError(f"Invalid X variable indices: i={i}, j={j}, n={n}")
    return i * n + j

def get_K_var(n, i, j):
    """Map variable K_ij: vertex i assigned label j"""
    if i < 0 or i >= n or j < 1 or j > n:
        raise ValueError(f"Invalid K variable indices: i={i}, j={j}, n={n}")
    return n * n + i * n + j

def validate_clauses(clauses):
    """Check and clean clauses"""
    clean_clauses = []
    for i, clause in enumerate(clauses):
        if not clause:  # Skip empty clauses
            continue
        clean_clause = []
        for lit in clause:
            if lit == 0:  # Skip literal 0
                continue
            if not isinstance(lit, int):
                raise ValueError(f"Clause {i} contains non-integer literal: {lit}")
            clean_clause.append(lit)
        if clean_clause:  # Only add non-empty clauses
            clean_clauses.append(clean_clause)
    return clean_clauses

def generate_clauses_for_cbp(n, edges, w):
    clauses = []
    top_id = 2 * n * n + 1  # First variable for auxiliary variables
    
    # 1. X_in = 1: Every vertex has label <= n
    for i in range(n):
        x_in = get_X_var(n, i, n)
        clauses.append([x_in])
    
    # 2. X_ij → X_i,j+1: If vertex i has label <= j then also has label <= j+1
    for i in range(n):
        for j in range(1, n):
            x_ij = get_X_var(n, i, j)
            x_ij_next = get_X_var(n, i, j+1)
            clauses.append([-x_ij, x_ij_next])
    
    # 3. Define K_ij through X_ij: K_ij ↔ X_ij ∧ ¬X_i,j-1
    for i in range(n):
        for j in range(1, n + 1):
            k_ij = get_K_var(n, i, j)
            x_ij = get_X_var(n, i, j)
            
            if j > 1:
                x_ij_prev = get_X_var(n, i, j-1)
                # K_ij ↔ (X_ij ∧ ¬X_i,j-1)
                clauses.append([-k_ij, x_ij])           # K_ij → X_ij
                clauses.append([-k_ij, -x_ij_prev])     # K_ij → ¬X_i,j-1
                clauses.append([k_ij, -x_ij, x_ij_prev]) # (X_ij ∧ ¬X_i,j-1) → K_ij
            else:
                # Case j = 1: K_i1 = X_i1 (since there is no X_i0)
                clauses.append([-k_ij, x_ij])           # K_i1 → X_i1
                clauses.append([k_ij, -x_ij])           # X_i1 → K_i1

    # 4. Constraint each label used at most once: ΣK_ij <= 1 (for each j)
    for j in range(1, n + 1):
        literals = [get_K_var(n, i, j) for i in range(n)]
        # Each label is used at most once
        cnf_atmost = CardEnc.atmost(lits=literals, bound=1, top_id=top_id)
        clauses.extend(cnf_atmost.clauses)
        top_id = cnf_atmost.nv + 1
    
    # 5. Bandwidth constraints for edges according to new specification
    for u, v in edges:
        for k in range(1, n + 1):
            k_uk = get_K_var(n, u, k)
            
            # Case 1: n-w > k > w+1: K_u,k → ¬X_v,k-w-1 ∧ X_v,k+w
            if 1+w < k < n-w:
                # ¬X_v,k-w-1 (if k-w-1 >= 1)
                if k-w-1 >= 1:
                    x_vkw_1 = get_X_var(n, v, k-w-1)
                    clauses.append([-k_uk, -x_vkw_1])
                
                # X_v,k+w (if k+w <= n)
                if k+w <= n:
                    x_vkw = get_X_var(n, v, k+w)
                    clauses.append([-k_uk, x_vkw])
                    
            # Case 2: w+1 >= k >= 1: K_u,k → ¬X_v,n-w+k-1 ∨ X_v,k+w
            elif 1 <= k <= w+1:
                literals = []
                
                # ¬X_v,n-w+k-1 (if n-w+k-1 >= 1)
                if n-w+k-1 >= 1:
                    x_vnwk_1 = get_X_var(n, v, n-w+k-1)
                    literals.append(-x_vnwk_1)
                
                # X_v,k+w (if k+w <= n)
                if k+w <= n:
                    x_vkw = get_X_var(n, v, k+w)
                    literals.append(x_vkw)
                
                if literals:
                    clauses.append([-k_uk] + literals)
                
            # Case 3: n >= k >= n-w: K_u,k → X_v,k-w ∨ X_v,k+w-n
            elif n-w <= k <= n:
                literals = []
                
                # X_v,k-w (if k-w >= 1)
                if k-w >= 1:
                    x_vkw1 = get_X_var(n, v, k-w-1)
                    literals.append(-x_vkw1)
                
                # X_v,k+w-n (if k+w-n >= 1)
                if k+w-n >= 1:
                    x_vkwn = get_X_var(n, v, k+w-n)
                    literals.append(x_vkwn)
                
                if literals:
                    clauses.append([-k_uk] + literals)

    # Validate and clean clauses
    clean_clauses = validate_clauses(clauses)
    print(f"   => Cleaned {len(clauses)} -> {len(clean_clauses)} clauses")
    
    return clean_clauses, top_id - 1

def solve_cbp(n, edges):
    """
    Main function to solve CBP, linear search on w to find the smallest value.
    """
    # Calculate maximum degree of the graph
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    max_degree = max(degree)
    
    # Calculate low_w (LB) and high_w (UB)
    import math
    low_w = math.ceil(max_degree / 2)  # Lower bound
    high_w = n // 2  # Upper bound = floor(n/2)
    
    print(f"   => Lower Bound (LB): {low_w}")
    print(f"   => Upper Bound (UB): {high_w}")
    print(f"   => Search strategy: Linear from {high_w} down to {low_w}, stop at first UNSAT")
    
    best_w = None
    
    # Linear search from UB down to LB - when first UNSAT encountered, w+1 is optimal
    for w in range(high_w, low_w - 1, -1):  # Decreasing from high_w to low_w
        print(f"\n===== Testing with bandwidth w = {w} =====")
        
        clauses, total_vars = generate_clauses_for_cbp(n, edges, w)
        print(f"   => Generated {len(clauses)} clauses with total {total_vars} variables.")

        with Glucose4(bootstrap_with=clauses) as solver:
            is_sat = solver.solve()
            print(f"   => Solver result: {'SAT' if is_sat else 'UNSAT'}")
            if is_sat:
                print(f"   =>  Found solution with w = {w}")
                best_w = w  # Update best_w but don't stop, continue searching for smaller w
            else:
                print(f"   => No solution with w = {w}")
                print(f"   => First UNSAT encountered! Stopping search.")
                break  # First UNSAT encountered, stop immediately
    
    if best_w is not None:
        print(f"==================================================")
        print(f"[*] FOUND! Minimum Cyclic Bandwidth (w) is: {best_w}")
        print(f"==================================================")
    else:
        print(f"\n   =>  No solution found in range [{low_w}, {high_w}]")
        print(f"   => All w values might be UNSAT")
    
    return best_w

if __name__ == '__main__':
    import sys
    from dataset_loader import load_mtx_graph, load_mtx_graph_manual, print_graph_stats
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print(" Please provide path to .mtx or .mtx.gz data file")
        print("Usage: python ver_2_5.py <path_to_file.mtx.gz>")
        sys.exit(1)
    
    # Read from .mtx.gz file
    file_path = sys.argv[1]
    print(f"Reading data from file: {file_path}")
    
    # Try reading with scipy first
    n_vertices, graph_edges = load_mtx_graph(file_path)
    
    # If unsuccessful, try manual reading
    if n_vertices is None:
        print("Scipy not available or error, trying manual reading...")
        n_vertices, graph_edges = load_mtx_graph_manual(file_path)
    
    if n_vertices is None or graph_edges is None:
        print(" Cannot read data file. Exiting program.")
        sys.exit(1)
    
    # Print graph statistics
    print_graph_stats(n_vertices, graph_edges)
    
    # Check graph size
    if n_vertices > 50:
        response = input(f"\n Graph has {n_vertices} vertices, might take long time. Continue? (y/n): ")
        if response.lower() != 'y':
            print("Stopping program.")
            sys.exit(0)
    
    # Solve CBP
    print("\nStarting Cyclic Bandwidth Problem solving...")
    final_w = solve_cbp(n_vertices, graph_edges)
    
    print("\n==================================================")
    if final_w is not None:
        print(f"[*] FOUND! Minimum Cyclic Bandwidth (w) is: {final_w}")
    else:
        print("[*] No solution found.")
    print("==================================================") 