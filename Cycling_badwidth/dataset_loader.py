import gzip
import numpy as np
from scipy.io import mmread
import os

def load_mtx_graph(file_path):
    """
    Read .mtx or .mtx.gz file and convert to edge list.
    
    Args:
        file_path (str): Path to .mtx or .mtx.gz file
        
    Returns:
        tuple: (n_vertices, edges) with:
            - n_vertices: number of vertices in the graph
            - edges: list of edges as [(u, v), ...]
    """
    try:
        print(f"Reading file: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Read matrix from file
        if file_path.endswith('.gz'):
            # Read compressed file
            matrix = mmread(file_path)
        else:
            # Read regular file
            matrix = mmread(file_path)
        
        print(f"Matrix size: {matrix.shape}")
        print(f"Non-zero elements: {matrix.nnz}")
        
        # Convert to COO format for easier processing
        if hasattr(matrix, 'tocoo'):
            coo_matrix = matrix.tocoo()
        else:
            coo_matrix = matrix
        
        # Get number of vertices (assume square matrix)
        n_vertices = max(matrix.shape[0], matrix.shape[1])
        
        # Create edge list
        edges = []
        for i, j in zip(coo_matrix.row, coo_matrix.col):
            # Convert from 1-indexed to 0-indexed if needed
            u, v = int(i), int(j)
            
            # Avoid self-loops and duplicate edges
            if u != v and (v, u) not in edges:
                edges.append((u, v))
        
        print(f"Number of vertices: {n_vertices}")
        print(f"Number of edges: {len(edges)}")
        
        return n_vertices, edges
        
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None, None

def load_mtx_graph_manual(file_path):
    """
    Read .mtx/.mtx.gz file manually (without scipy).
    For cases when scipy is not available.
    
    Args:
        file_path (str): Path to .mtx or .mtx.gz file
        
    Returns:
        tuple: (n_vertices, edges)
    """
    try:
        print(f"Reading file manually: {file_path}")
        
        # Open file (compressed or not)
        if file_path.endswith('.gz'):
            file_handle = gzip.open(file_path, 'rt')
        else:
            file_handle = open(file_path, 'r')
        
        with file_handle as f:
            lines = f.readlines()
        
        # Skip comment lines (starting with %)
        data_lines = []
        header_found = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('%'):
                continue
            elif not header_found:
                # First non-comment line is the header
                header = line.split()
                rows, cols, entries = int(header[0]), int(header[1]), int(header[2])
                n_vertices = max(rows, cols)
                header_found = True
                print(f"Header: {rows} x {cols}, {entries} entries")
            else:
                data_lines.append(line)
        
        # Read edges
        edges = []
        for line in data_lines:
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    # Convert from 1-indexed to 0-indexed
                    u, v = int(parts[0]) - 1, int(parts[1]) - 1
                    
                    # Avoid self-loops and duplicate edges
                    if u != v and (v, u) not in edges:
                        edges.append((u, v))
        
        print(f"Number of vertices: {n_vertices}")
        print(f"Number of edges: {len(edges)}")
        
        return n_vertices, edges
        
    except Exception as e:
        print(f"Error reading file manually {file_path}: {str(e)}")
        return None, None

def print_graph_stats(n_vertices, edges):
    """
    Print basic graph statistics.
    """
    if edges is None:
        print("No graph data to analyze.")
        return
    
    # Calculate vertex degrees
    degree = [0] * n_vertices
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    
    max_degree = max(degree) if degree else 0
    min_degree = min(degree) if degree else 0
    avg_degree = sum(degree) / len(degree) if degree else 0
    
    print("\n=== GRAPH STATISTICS ===")
    print(f"Number of vertices: {n_vertices}")
    print(f"Number of edges: {len(edges)}")
    print(f"Maximum degree: {max_degree}")
    print(f"Minimum degree: {min_degree}")
    print(f"Average degree: {avg_degree:.2f}")
    print(f"Graph density: {2 * len(edges) / (n_vertices * (n_vertices - 1)):.4f}")

# Usage example
if __name__ == "__main__":
    # Change this path to your .mtx.gz file
    file_path = "example.mtx.gz"
    
    # Try reading with scipy first
    n, edges = load_mtx_graph(file_path)
    
    # If unsuccessful, try manual reading
    if n is None:
        print("Trying manual reading...")
        n, edges = load_mtx_graph_manual(file_path)
    
    # Print statistics
    if n is not None:
        print_graph_stats(n, edges)
    else:
        print("Cannot read data file.")
