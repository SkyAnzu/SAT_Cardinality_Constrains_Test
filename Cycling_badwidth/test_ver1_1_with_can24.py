#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for ver_1^1.py CBP implementation with can___24.mtx dataset
Tương tự như test đã làm với ver_2.py
"""

import sys
import os
import importlib.util
from dataset_loader import load_mtx_graph

def load_ver1_1_module():
    """Load ver_1^1.py module using importlib"""
    try:
        spec = importlib.util.spec_from_file_location("ver_1_1", 
            "d:\\NCKH\\SAT_Cardinality_Constrains_Test\\Cycling_badwidth\\ver_1^1.py")
        ver_1_1 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ver_1_1)
        return ver_1_1
    except Exception as e:
        print(f"Error loading ver_1^1.py: {e}")
        return None

def test_specific_bandwidth(ver_1_1, n, edges, w):
    """Test a specific bandwidth value"""
    print(f"\n===== Testing bandwidth w = {w} =====")
    try:
        from pysat.solvers import Glucose4
        
        clauses, total_vars = ver_1_1.generate_clauses_for_cbp(n, edges, w)
        print(f"Generated {len(clauses)} clauses with {total_vars} variables")
        
        with Glucose4(bootstrap_with=clauses) as solver:
            is_sat = solver.solve()
            result = "SAT" if is_sat else "UNSAT"
            print(f"Result: {result}")
            
            if is_sat:
                model = solver.get_model()
                print(f"Found satisfying assignment with {len(model)} variables")
                
                # Extract assignment
                assignment = {}
                for u in range(n):
                    for l in range(1, n + 1):
                        var = ver_1_1.get_var(n, u, l)
                        if var <= len(model) and model[var - 1] > 0:
                            assignment[u] = l
                            break
                
                print(f"Assignment: {assignment}")
                return True, assignment
            else:
                return False, None
                
    except Exception as e:
        print(f"Error testing w={w}: {e}")
        return False, None

def validate_assignment(assignment, edges, w, n):
    """Validate if assignment satisfies cyclic bandwidth constraint"""
    print(f"\n===== Validating assignment for w = {w} =====")
    
    def cyclic_distance(a, b, n):
        return min(abs(a - b), n - abs(a - b))
    
    valid = True
    violations = []
    
    for u, v in edges:
        if u in assignment and v in assignment:
            dist = cyclic_distance(assignment[u], assignment[v], n)
            if dist > w:
                violations.append((u, v, assignment[u], assignment[v], dist))
                valid = False
    
    if valid:
        print(f"✓ Assignment is VALID for w = {w}")
    else:
        print(f"✗ Assignment is INVALID for w = {w}")
        print(f"Found {len(violations)} violations:")
        for u, v, label_u, label_v, dist in violations[:5]:  # Show first 5 violations
            print(f"  Edge ({u},{v}): labels ({label_u},{label_v}), distance = {dist} > {w}")
        if len(violations) > 5:
            print(f"  ... and {len(violations) - 5} more violations")
    
    return valid

def main():
    print("Testing ver_1^1.py with can___24.mtx dataset")
    print("=" * 60)
    
    # Load ver_1^1.py module
    ver_1_1 = load_ver1_1_module()
    if ver_1_1 is None:
        return
    
    # Load the graph
    print("Loading can___24.mtx dataset...")
    try:
        n, edges = load_mtx_graph("bcspwr01.mtx")
        print(f"Graph loaded: {n} vertices, {len(edges)} edges")
        print(f"Sample edges: {edges[:10]}")
    except Exception as e:
        print(f"Error loading graph: {e}")
        return
    
    # Calculate bounds
    print(f"\n{'='*60}")
    print("CALCULATING BOUNDS")
    print(f"{'='*60}")
    
    # Calculate degree for each vertex
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    
    max_degree = max(degree) if degree else 0
    
    # Lower bound: ceil(max_degree / 2)
    import math
    lb = math.ceil(max_degree / 2)
    
    # Upper bound: n // 2
    ub = n // 2
    
    print(f"Max degree: {max_degree}")
    print(f"Lower bound (lb): {lb}")
    print(f"Upper bound (ub): {ub}")
    
    # Test specific bandwidth values from ub-1 down to lb
    print(f"\n{'='*60}")
    print("TESTING SPECIFIC BANDWIDTH VALUES (from ub-1 down to lb)")
    print(f"{'='*60}")
    
    results = {}
    test_range = list(range(ub-1, lb-1, -1))  # From ub-1 down to lb
    print(f"Testing bandwidths: {test_range}")
    
    for w in test_range:
        is_sat, assignment = test_specific_bandwidth(ver_1_1, n, edges, w)
        results[w] = (is_sat, assignment)
        
        if is_sat and assignment:
            validate_assignment(assignment, edges, w, n)
            print(f"w = {w} is SAT, trying smaller bandwidth...")
        else:
            print(f"w = {w} is UNSAT!")
            # First UNSAT result means w+1 is the optimal bandwidth
            optimal_w = w + 1
            print(f"\n{'='*60}")
            print(f"🎯 OPTIMAL CYCLIC BANDWIDTH FOUND: w = {optimal_w}")
            print(f"   (Since w = {w} is UNSAT, optimal is w = {optimal_w})")
            print(f"{'='*60}")
            break
    else:
        # If we tested all values and all were SAT, then lb is optimal
        print(f"\n{'='*60}")
        print(f"🎯 OPTIMAL CYCLIC BANDWIDTH FOUND: w = {lb}")
        print(f"   (All tested values were SAT, so lower bound {lb} is optimal)")
        print(f"{'='*60}")
    
    # Check if no solution found (shouldn't happen with proper bounds)
    if not any(results[w][0] for w in results if w in results):
        print(f"\n{'='*60}")
        print("❌ NO SOLUTION FOUND in the tested range")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
