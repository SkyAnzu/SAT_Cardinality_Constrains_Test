#!/usr/bin/env python3
"""
Auto Test Script for Cyclic Bandwidth Problem
Run tests on multiple .mtx files and output results to CSV
"""

import os
import sys
import subprocess
import time
import csv
import glob
from datetime import datetime

def find_mtx_files(directory):
    """Find all .mtx and .mtx.gz files in directory and subdirectories"""
    patterns = ['*.mtx', '*.mtx.gz']
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(directory, '**', pattern), recursive=True))
    return sorted(list(set(files)))

def run_cbp_solver(script_path, mtx_file, timeout=12):
    """
    Run CBP solver with timeout and capture output.
    This version forces unbuffered output to prevent data loss on timeout.
    """
    start_time = time.time()
    output = ""
    stderr = ""
    timed_out = False
    return_code = 0

    def parse_output(output_text):
        """Parse solver output to extract results"""
        bandwidth = None
        last_successful_w = None
        last_successful_clauses = None
        last_successful_vars = None
        current_testing_w = None
        w_to_clauses = {}
        w_to_vars = {}

        lines = output_text.split('\n')

        for line in lines:
            if "FOUND! Minimum Cyclic Bandwidth (w) is:" in line:
                try:
                    bandwidth = int(line.split(":")[-1].strip())
                except (ValueError, IndexError):
                    pass
            elif "No solution found." in line:
                bandwidth = "NO_SOLUTION"
            elif "Testing with bandwidth w =" in line or "===== Testing with bandwidth w =" in line:
                try:
                    current_testing_w = int(line.split("w =")[-1].strip().replace("=====", "").strip())
                except (ValueError, IndexError):
                    pass
            elif "Generated" in line and "clauses with total" in line and "variables" in line:
                try:
                    import re
                    match = re.search(r'Generated (\d+) clauses with total (\d+) variables', line)
                    if match and current_testing_w is not None:
                        w_to_clauses[current_testing_w] = int(match.group(1))
                        w_to_vars[current_testing_w] = int(match.group(2))
                except (ValueError, IndexError):
                    pass
            elif ("Found solution with w =" in line or
                  "Solver result: SAT" in line or
                  ( "SAT" in line and "UNSAT" not in line.upper() )): # More robust SAT check
                try:
                    found_w = None
                    if "Found solution with w =" in line:
                        found_w = int(line.split("w =")[-1].strip())
                    elif current_testing_w is not None:
                        # This assumes SAT corresponds to the current w being tested
                        found_w = current_testing_w

                    if found_w is not None:
                        last_successful_w = found_w
                        if found_w in w_to_clauses:
                            last_successful_clauses = w_to_clauses[found_w]
                            last_successful_vars = w_to_vars[found_w]
                except (ValueError, IndexError):
                    pass
        
        timeout_at_w = current_testing_w if timed_out else None

        clauses_count = None
        vars_count = None
        if w_to_clauses:
            last_w = max(w_to_clauses.keys())
            clauses_count = w_to_clauses.get(last_w)
            vars_count = w_to_vars.get(last_w)

        return (bandwidth, last_successful_w, last_successful_clauses, 
                last_successful_vars, timeout_at_w, clauses_count, vars_count)

    try:
        try:
            # *** FIX: Added '-u' flag to force unbuffered output from the child script.
            # This is the critical change to prevent losing the last "SAT" message before a timeout.
            result = subprocess.run(
                [sys.executable, '-u', script_path, mtx_file],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=timeout
            )
            output = result.stdout
            stderr = result.stderr
            return_code = result.returncode
        except subprocess.TimeoutExpired as e:
            output = e.stdout if e.stdout else ""
            stderr = e.stderr if e.stderr else ""
            timed_out = True
            return_code = -1  # Custom code for timeout

        runtime = time.time() - start_time

        (bandwidth, last_w, last_clauses, last_vars,
         timeout_w, final_clauses, final_vars) = parse_output(output)

        return {
            'success': return_code == 0 and bandwidth is not None and bandwidth != "NO_SOLUTION",
            'return_code': return_code,
            'bandwidth': bandwidth,
            'runtime': runtime,
            'clauses': final_clauses,
            'variables': final_vars,
            'output': output,
            'error': stderr,
            'last_successful_w': last_w,
            'last_successful_clauses': last_clauses,
            'last_successful_vars': last_vars,
            'timeout_at_w': timeout_w
        }

    except Exception as e:
        return {
            'success': False, 'return_code': -99, 'bandwidth': None,
            'runtime': time.time() - start_time, 'clauses': None, 'variables': None,
            'output': "", 'error': str(e), 'last_successful_w': None,
            'last_successful_clauses': None, 'last_successful_vars': None, 'timeout_at_w': None
        }

def get_graph_stats(mtx_file):
    """Get basic graph information"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from dataset_loader import load_mtx_graph

        n_vertices, graph_edges = load_mtx_graph(mtx_file)
        if n_vertices is None or graph_edges is None:
            return None, None, None

        if n_vertices == 0:
            return 0, 0, 0
        degree = [0] * n_vertices
        for u, v in graph_edges:
            degree[u] += 1
            degree[v] += 1
        max_degree = max(degree) if degree else 0

        return n_vertices, len(graph_edges), max_degree
    except Exception as e:
        print(f"Error getting stats for {mtx_file}: {e}")
        return None, None, None

def main():
    # Configuration
    test_directory = "Dataset"
    solvers = [
        ("ver_2.py", "ver_2"),
        ("ver_2_5.py", "ver_2_5"),
    ]
    timeout = 12

    mtx_files = find_mtx_files(test_directory)
    print(f"Found {len(mtx_files)} test files.")
    if not mtx_files:
        print("No .mtx files found!")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"cbp_test_results_{timestamp}.csv"

    fieldnames = [
        'file_name', 'solver', 'vertices', 'edges', 'max_degree',
        'success', 'bandwidth', 'runtime_sec', 'clauses', 'variables',
        'timeout', 'timeout_at_w', 'last_successful_w', 'last_successful_clauses', 'last_successful_vars',
        'error_msg'
    ]

    print(f"\nStarting test with {len(solvers)} solver(s)...")
    print(f"Results will be saved to: {csv_file}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_tests = len(mtx_files) * len(solvers)
        current_test = 0

        for mtx_file in mtx_files:
            file_name = os.path.basename(mtx_file)
            print(f"\nTesting file: {file_name}")
            vertices, edges, max_degree = get_graph_stats(mtx_file)

            for solver_script, solver_name in solvers:
                current_test += 1
                print(f"  [{current_test}/{total_tests}] {solver_name}... ", end="", flush=True)

                if not os.path.exists(solver_script):
                    print("SKIP (file not found)")
                    writer.writerow({
                        'file_name': file_name, 'solver': solver_name,
                        'vertices': vertices, 'edges': edges, 'max_degree': max_degree,
                        'success': False, 'error_msg': f"Solver script '{solver_script}' not found"
                    })
                    continue

                result = run_cbp_solver(solver_script, mtx_file, timeout)
                is_timeout = result.get('return_code') == -1

                if result['success']:
                    print(f"SUCCESS w={result['bandwidth']} ({result['runtime']:.1f}s)")
                elif is_timeout:
                    timeout_info = f"TIMEOUT ({timeout}s)"
                    if result.get('timeout_at_w'):
                        timeout_info += f" at w={result['timeout_at_w']}"
                    if result.get('last_successful_w'):
                        timeout_info += f" | Last SAT: w={result['last_successful_w']}"
                    print(timeout_info)
                else:
                    print(f"FAILED (code: {result.get('return_code')})")
                    if result['error']:
                        print(f"      Error: {result['error'].strip().splitlines()[-1]}")

                writer.writerow({
                    'file_name': file_name,
                    'solver': solver_name,
                    'vertices': vertices,
                    'edges': edges,
                    'max_degree': max_degree,
                    'success': result['success'],
                    'bandwidth': result['bandwidth'],
                    'runtime_sec': round(result['runtime'], 2),
                    'clauses': result['clauses'],
                    'variables': result['variables'],
                    'timeout': is_timeout,
                    'timeout_at_w': result.get('timeout_at_w'),
                    'last_successful_w': result.get('last_successful_w'),
                    'last_successful_clauses': result.get('last_successful_clauses'),
                    'last_successful_vars': result.get('last_successful_vars'),
                    'error_msg': result['error'][:200] if result['error'] else ""
                })

    print(f"\nCompleted! Results saved to {csv_file}")

if __name__ == "__main__":
    main()
