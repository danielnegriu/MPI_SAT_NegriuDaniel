# Cod de bază pentru compararea algoritmilor SAT în Python

import random
import time
import tracemalloc
from typing import List, Tuple, Optional

# Tipuri de date
Literal = int
Clause = List[Literal]
CNFFormula = List[Clause]

# Evaluare formula CNF cu o atribuire
def evaluate_formula(formula: CNFFormula, assignment: List[bool]) -> bool:
    for clause in formula:
        if not any((assignment[abs(lit) - 1] if lit > 0 else not assignment[abs(lit) - 1]) for lit in clause):
            return False
    return True

# Algoritm DPLL simplificat
def dpll(formula: CNFFormula, assignment: List[Optional[bool]]) -> bool:
    def unit_propagate():
        changed = True
        while changed:
            changed = False
            for clause in formula:
                unassigned = [lit for lit in clause if assignment[abs(lit) - 1] is None]
                values = [assignment[abs(lit) - 1] if lit > 0 else not assignment[abs(lit) - 1] for lit in clause if assignment[abs(lit) - 1] is not None]
                if all(v is False for v in values) and not unassigned:
                    return False  # conflict
                if len(unassigned) == 1 and all(v is False for v in values):
                    lit = unassigned[0]
                    assignment[abs(lit) - 1] = lit > 0
                    changed = True
        return True

    if not unit_propagate():
        return False
    if all(a is not None for a in assignment):
        return evaluate_formula(formula, [a if a is not None else False for a in assignment])

    var = next(i for i, a in enumerate(assignment) if a is None)
    for val in [True, False]:
        assignment_copy = assignment[:]
        assignment_copy[var] = val
        if dpll(formula, assignment_copy):
            return True
    return False

# WalkSAT simplificat
def walksat(formula: CNFFormula, max_flips: int = 10000, p: float = 0.5) -> Optional[List[bool]]:
    n_vars = max(abs(lit) for clause in formula for lit in clause)
    assignment = [random.choice([True, False]) for _ in range(n_vars)]
    for _ in range(max_flips):
        unsat_clauses = [clause for clause in formula if not any((assignment[abs(lit) - 1] if lit > 0 else not assignment[abs(lit) - 1]) for lit in clause)]
        if not unsat_clauses:
            return assignment
        clause = random.choice(unsat_clauses)
        if random.random() < p:
            var = abs(random.choice(clause)) - 1
        else:
            scores = []
            for lit in clause:
                var = abs(lit) - 1
                assignment[var] = not assignment[var]
                score = sum(any((assignment[abs(l) - 1] if l > 0 else not assignment[abs(l) - 1]) for l in c) for c in formula)
                scores.append((score, var))
                assignment[var] = not assignment[var]
            _, var = max(scores)
        assignment[var] = not assignment[var]
    return None

# Testare și măsurare performanță
def benchmark_solver(solver_fn, formula: CNFFormula, n_vars: int):
    start_time = time.perf_counter()
    tracemalloc.start()
    if solver_fn.__name__ == 'dpll':
        result = solver_fn(formula, [None] * n_vars)
    else:
        result = solver_fn(formula)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    duration = time.perf_counter() - start_time
    return result, duration, peak / 1024

# Citire formula CNF din fișier (format simplu: prima linie n m, urmate de m clauze cu câte 3 literali)
def read_formula_from_file(filename: str) -> Tuple[CNFFormula, int]:
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('c')]
        n_vars, n_clauses = map(int, lines[0].split())
        formula = [list(map(int, line.split())) for line in lines[1:1+n_clauses]]
    return formula, n_vars

if __name__ == "__main__":
    random.seed(42)
    filename = input("Introduceți numele fișierului cu formula CNF: ")
    formula, n_vars = read_formula_from_file(filename)

    for solver in [dpll, walksat]:
        result, duration, mem_kb = benchmark_solver(solver, formula, n_vars)
        print(f"{solver.__name__}: Result={result is not None}, Time={duration:.4f}s, Mem={mem_kb:.2f} KB")
