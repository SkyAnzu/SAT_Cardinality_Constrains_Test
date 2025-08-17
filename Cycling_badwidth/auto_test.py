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
        # Search in directory and all subdirectories (recursive covers both)
        files.extend(glob.glob(os.path.join(directory, '**', pattern), recursive=True))
    return sorted(list(set(files)))  # Remove duplicates with set()

def run_cbp_solver(script_path, mtx_file, timeout=12):
    """Run CBP solver with timeout and progressive output capture"""
    
    # Initialize variables to ensure they're in scope for except blocks
    output = ""
    stderr = ""
    last_successful_w = None
    last_successful_clauses = None
    last_successful_vars = None
    timeout_at_w = None
    start_time = time.time()  # Move start_time here
    timed_out = False  # Flag to track timeout
    
    def parse_output(output_text, process_return_code=None):
        """Parse solver output to extract results"""
        # Find bandwidth result
        bandwidth = None
        last_successful_w = None
        last_successful_clauses = None
        last_successful_vars = None
        timeout_at_w = None
        
        # Track current w being tested
        current_testing_w = None
        
        # Split output into lines for parsing
        lines = output_text.split('\n')
        
        # Track clauses/vars for each w value
        w_to_clauses = {}
        w_to_vars = {}
        current_w_for_generation = None
        
        for i, line in enumerate(lines):
            # Find final bandwidth result
            if "FOUND! Minimum Cyclic Bandwidth (w) is:" in line:
                try:
                    bandwidth = int(line.split(":")[-1].strip())
                except:
                    pass
            elif "No solution found." in line:
                bandwidth = "NO_SOLUTION"
            
            # Track current w being tested
            elif "Testing with bandwidth w =" in line or "===== Testing with bandwidth w =" in line:
                try:
                    current_testing_w = int(line.split("w =")[-1].strip().replace("=====", "").strip())
                    current_w_for_generation = current_testing_w
                except:
                    pass
            
            # Capture clauses/variables generation for current w
            elif "Generated" in line and "clauses with total" in line and "variables" in line:
                try:
                    import re
                    match = re.search(r'Generated (\d+) clauses with total (\d+) variables', line)
                    if match:
                        current_clauses = int(match.group(1))
                        current_vars = int(match.group(2))
                        
                        # Associate with current w being tested
                        if current_w_for_generation is not None:
                            w_to_clauses[current_w_for_generation] = current_clauses
                            w_to_vars[current_w_for_generation] = current_vars
                except:
                    pass
            
            # Capture successful SAT results
            elif ("Found solution with w =" in line or 
                  "Solver result: SAT" in line or
                  "SAT" in line):
                try:
                    if "Found solution with w =" in line:
                        found_w = int(line.split("w =")[-1].strip())
                        last_successful_w = found_w
                        # Get clauses/vars for this successful w
                        if found_w in w_to_clauses:
                            last_successful_clauses = w_to_clauses[found_w]
                            last_successful_vars = w_to_vars[found_w]
                    elif "Solver result: SAT" in line and current_w_for_generation is not None:
                        # SAT result for current w being tested
                        last_successful_w = current_w_for_generation
                        if current_w_for_generation in w_to_clauses:
                            last_successful_clauses = w_to_clauses[current_w_for_generation]
                            last_successful_vars = w_to_vars[current_w_for_generation]
                    elif ("SAT" in line and current_w_for_generation is not None and 
                          not any(skip_word in line.lower() for skip_word in ['solver', 'using', 'minisat', 'glucose', 'unsat'])):
                        # Generic SAT detection, but avoid false positives
                        last_successful_w = current_w_for_generation
                        if current_w_for_generation in w_to_clauses:
                            last_successful_clauses = w_to_clauses[current_w_for_generation]
                            last_successful_vars = w_to_vars[current_w_for_generation]
                except:
                    pass
        
        # If process was killed due to timeout, current_testing_w is likely where timeout occurred
        if process_return_code is None or process_return_code < 0:  # Process was killed
            timeout_at_w = current_testing_w
        
        # Get final clauses and variables count (last generated)
        clauses_count = None
        vars_count = None
        if w_to_clauses:
            # Get the last generated clauses/vars
            last_w = max(w_to_clauses.keys())
            clauses_count = w_to_clauses[last_w]
            vars_count = w_to_vars[last_w]
        
        return bandwidth, last_successful_w, last_successful_clauses, last_successful_vars, timeout_at_w, clauses_count, vars_count
    
    try:
        # Run script with simple subprocess
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, script_path, mtx_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout
            stderr = result.stderr
            timed_out = False
            
        except subprocess.TimeoutExpired as e:
            # Process timed out
            output = e.stdout if e.stdout else ""
            stderr = e.stderr if e.stderr else ""
            timed_out = True
        
        end_time = time.time()
        runtime = end_time - start_time
        
        # Parse output to get results
        bandwidth, last_successful_w, last_successful_clauses, last_successful_vars, timeout_at_w, clauses_count, vars_count = parse_output(output, -1 if timed_out else 0)
        
        # If timed out, return timeout result
        if timed_out:
            # Parse the output we did get to extract any useful information
            bandwidth_result, last_w, last_clauses, last_vars, timeout_w, final_clauses, final_vars = parse_output(output, -1)
            
            return {
                'success': False,
                'return_code': -1,  # Indicate timeout
                'bandwidth': bandwidth_result,  # Might be None if not found
                'runtime': runtime,
                'clauses': final_clauses,
                'variables': final_vars,
                'output': f"TIMEOUT after {runtime:.1f}s\n" + output,
                'error': f"Process killed due to timeout ({runtime:.1f}s)",
                'last_successful_w': last_w,
                'last_successful_clauses': last_clauses,
                'last_successful_vars': last_vars,
                'timeout_at_w': timeout_w
            }
        
        return {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'bandwidth': bandwidth,
            'runtime': runtime,
            'clauses': clauses_count,
            'variables': vars_count,
            'output': output,
            'error': stderr,
            'last_successful_w': None,
            'last_successful_clauses': None,
            'last_successful_vars': None,
            'timeout_at_w': timeout_at_w
        }
        
    except Exception as e:
        # Handle any other errors (file read errors, import errors, etc.)
        return {
            'success': False,
            'bandwidth': None,
            'runtime': 0,
            'clauses': None,
            'variables': None,
            'output': "",
            'error': str(e),
            'last_successful_w': None,
            'last_successful_clauses': None,
            'last_successful_vars': None,
            'timeout_at_w': None
        }

def get_graph_stats(mtx_file):
    """Get basic graph information"""
    try:
        # Import dataset_loader
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from dataset_loader import load_mtx_graph
        
        n_vertices, graph_edges = load_mtx_graph(mtx_file)
        if n_vertices is None or graph_edges is None:
            return None, None, None
            
        # Calculate maximum degree
        degree = [0] * n_vertices
        for u, v in graph_edges:
            degree[u] += 1
            degree[v] += 1
        max_degree = max(degree) if degree else 0
        
        return n_vertices, len(graph_edges), max_degree
    except Exception as e:
        # Handle any errors during graph loading or processing
        return None, None, None

def main():
    # Configuration
    test_directory = "Dataset"  # Directory containing .mtx files
    solvers = [
        ("ver_2.py", "ver_2"),
        ("ver_2_5.py", "ver_2_5"),
    ]
    timeout = 12 

    # Find test files
    mtx_files = find_mtx_files(test_directory)
    print(f"Found {len(mtx_files)} test files:")
    for f in mtx_files:
        print(f"  - {os.path.basename(f)}")
    
    if not mtx_files:
        print("No .mtx files found!")
        return
    
    # Create CSV result file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"cbp_test_results_{timestamp}.csv"
    
    # CSV Header
    fieldnames = [
        'file_name', 'solver', 'vertices', 'edges', 'max_degree',
        'success', 'bandwidth', 'runtime_sec', 'clauses', 'variables',
        'timeout', 'timeout_at_w', 'last_successful_w', 'last_successful_clauses', 'last_successful_vars',
        'error_msg'
    ]
    
    print(f"\nStarting test with {len(solvers)} solver(s)...")
    print(f"Results will be saved to: {csv_file}")
    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_tests = len(mtx_files) * len(solvers)
        current_test = 0
        
        for mtx_file in mtx_files:
            file_name = os.path.basename(mtx_file)
            print(f"\nTesting file: {file_name}")
            
            # Get graph information
            vertices, edges, max_degree = get_graph_stats(mtx_file)
            
            for solver_script, solver_name in solvers:
                current_test += 1
                print(f"  [{current_test}/{total_tests}] {solver_name}... ", end="", flush=True)
                
                if not os.path.exists(solver_script):
                    print(f"SKIP (file not found)")
                    writer.writerow({
                        'file_name': file_name,
                        'solver': solver_name,
                        'vertices': vertices,
                        'edges': edges,
                        'max_degree': max_degree,
                        'success': False,
                        'bandwidth': None,
                        'runtime_sec': 0,
                        'clauses': None,
                        'variables': None,
                        'timeout': False,
                        'timeout_at_w': None,
                        'last_successful_w': None,
                        'last_successful_clauses': None,
                        'last_successful_vars': None,
                        'error_msg': f"Solver script '{solver_script}' not found"
                    })
                    continue
                
                # Run test
                result = run_cbp_solver(solver_script, mtx_file, timeout)
                
                # Display results
                if result['success'] and result['bandwidth'] is not None and result['bandwidth'] != "NO_SOLUTION":
                    print(f"SUCCESS w={result['bandwidth']} ({result['runtime']:.1f}s)")
                elif result['success'] and result['bandwidth'] == "NO_SOLUTION":
                    print(f"NO_SOLUTION ({result['runtime']:.1f}s)")
                elif (result.get('return_code') == -1 or  # Our timeout indicator
                      "TIMEOUT" in result['output'] or 
                      "Process killed due to timeout" in result.get('error', '') or
                      result.get('timeout_at_w') is not None):
                    # Process was killed due to timeout
                    timeout_info = f"TIMEOUT ({timeout}s)"
                    if result.get('timeout_at_w'):
                        timeout_info += f" at w={result['timeout_at_w']}"
                    
                    # Always show last successful SAT result if available
                    if result.get('last_successful_w'):
                        timeout_info += f" | Last SAT: w={result['last_successful_w']}"
                        if result.get('last_successful_clauses') and result.get('last_successful_vars'):
                            timeout_info += f" ({result['last_successful_clauses']} clauses, {result['last_successful_vars']} vars)"
                    else:
                        timeout_info += " | No SAT found before timeout"
                    
                    print(timeout_info)
                    
                    # Also print detailed timeout information
                    if result.get('last_successful_w'):
                        print(f"    --> Best result before timeout: SAT at w={result['last_successful_w']}")
                    if result.get('timeout_at_w'):
                        print(f"    --> Timeout occurred while testing w={result['timeout_at_w']}")
                    
                    # Show last few lines of output for debugging
                    if result['output']:
                        output_lines = [line for line in result['output'].split('\n')[-10:] if line.strip()]
                        if output_lines:
                            print(f"    --> Last output lines:")
                            for line in output_lines[-3:]:  # Show last 3 non-empty lines
                                if line.strip():
                                    print(f"        {line.strip()}")
                else:
                    print(f"FAILED")
                    # Show full error details for debugging
                    if result['error']:
                        print(f"    Full Error:\n{result['error']}")
                    print(f"    Return code: {result.get('return_code', 'unknown')}")
                    if result['output']:
                        print(f"    Last output lines:")
                        output_lines = result['output'].split('\n')[-5:]
                        for line in output_lines:
                            if line.strip():
                                print(f"      {line}")
                
                # Write to CSV
                is_timeout = (result.get('return_code') == -1 or  # Our timeout indicator
                            "TIMEOUT" in result['output'] or 
                            "Process killed due to timeout" in result.get('error', '') or
                            result.get('timeout_at_w') is not None)            
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
                    'error_msg': result['error'][:200] if result['error'] else ""  # Limit error message length
                })
    
    print(f"\nCompleted! Results saved to {csv_file}")
    print(f"Total tests: {total_tests}")

if __name__ == "__main__":
    main()
