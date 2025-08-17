from pysat.solvers import Glucose3
import math

def generate_variables(n):
    for i in range (n):
        for j in range (n):
            return i * n + j + 1
        
def generate_new_variables(end, length):
    for i in range (end + 1, end + math.ceil(math.log(length, 2)) + 1):
        return i
    
def generate_binary_combinations(n):
    binary_combinations = []
    for i in range (1 << n):
        binary_combinations.append(format(i, '0' + str(n) + 'b'))
    return binary_combinations

def binary_encoding(clauses, target, new_variables):
    for i in range (len(new_variables)):
        clauses.append([-target, new_variables[i]])

