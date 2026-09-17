import re
import gurobipy as gp
from gurobipy import GRB
"""
The file save path: Need gurobi
"""

def solve_CNOT_matrix(M2, new_M1, minimize=True, enforce_invertible=True):
    """
    Solve for a binary matrix P such that P * M2 ≡ new_M1 (mod 2)
    M2: Input matrix, an n x n binary list
    new_M1: Output matrix, an n x n binary list
    minimize: Whether to minimize the total number of 1s in P, default True
    enforce_invertible: Whether to require P to be invertible (generate C_inv constraint), default True
    """
    n = len(new_M1)
    model = gp.Model("CNOT_min")
    P = {}
    for i in range(n):
        for j in range(n):
            P[i, j] = model.addVar(vtype=GRB.BINARY, name=f"c{i}_{j}")
    t = {}
    for i in range(n):
        for j in range(n):
            t[i, j] = model.addVar(vtype=GRB.INTEGER, name=f"t_{i}_{j}")
    if enforce_invertible:
        C_inv = {}
        t2 = {}
        for i in range(n):
            for j in range(n):
                C_inv[i, j] = model.addVar(vtype=GRB.BINARY, name=f"Cinv_{i}_{j}")
                t2[i, j] = model.addVar(vtype=GRB.INTEGER, name=f"t2_{i}_{j}")
                model.addConstr(
                    gp.quicksum(P[i, k] * C_inv[k, j] for k in range(n)) == 2 * t2[i, j] + (1 if i == j else 0),
                    name=f"inv_mod2_{i}_{j}"
                )

    if minimize:
        model.setObjective(gp.quicksum(P[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)
    else:
        model.setObjective(gp.quicksum(P[i, j] for i in range(n) for j in range(n)), GRB.MAXIMIZE)

    for i in range(n):
        for j in range(n):
            model.addConstr(
                gp.quicksum(P[i, k] * M2[k][j] for k in range(n)) == 2 * t[i, j] + new_M1[i][j],
                name=f"mod2_{i}_{j}"
            )

    model.optimize()

    if model.status == GRB.OPTIMAL:
        P_sol = [[int(P[i, j].X) for j in range(n)] for i in range(n)]
        obj_val = model.objVal
    else:
        P_sol = None
        obj_val = None

    return P_sol, obj_val, model.status
def read_linear_matrix_from_txt2(file_path, P):
    """
    Read from a txt file in the form:
    D0 = Q75 + Q2 + Q83
    D1 = Q88 + Q6
    Inputs:
    file_path: Path to the txt file
    P: List of bit positions involved in CNOT computation,
    e.g. [0,1,2,3,4,5,6,7,64,65,66,67,68,75,83,88]

    Outputs:
    names: List of names on the left-hand side of the equations, e.g. ["D0", "D1"]
    matrix: 0/1 matrix
    """

    pos_to_col = {q: idx for idx, q in enumerate(P)}
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip().replace(" ", "") for line in f if line.strip()]
    names = []
    matrix = []
    for line_idx, line in enumerate(lines):
        if "=" not in line:
            raise ValueError(f"第 {line_idx + 1} 行格式错误，没有 '=' ：{line}")
        left, right = line.split("=", 1)
        name = left.strip()
        if not name:
            raise ValueError(f"第 {line_idx + 1} 行左侧名称为空：{line}")
        names.append(name)
        row = [0] * len(P)
        vars_right = re.findall(r"Q(\d+)", right)
        for v in vars_right:
            q_num = int(v)
            if q_num not in pos_to_col:
                raise ValueError(
                    f"第 {line_idx + 1} 行引用了 Q{q_num}，"
                    f"但 Q{q_num} 不在给定的 P 列表中"
                )

            col = pos_to_col[q_num]
            row[col] ^= 1
        matrix.append(row)
    return names, matrix
"""output file_path"""
file_path1= "D:\CNOT_Optimization_MILP\data\output.txt"
X1 = [9, 15, 0, 7, 13, 2, 12, 14,1,8,10,11]+[i for i in range(44,58)]+[24,26,27,31,38,40,41,42]
name1, M1= read_linear_matrix_from_txt2(file_path1,X1)
"""input file_path"""
file_path2= "D:\CNOT_Optimization_MILP\data\input.txt"
name2, M2= read_linear_matrix_from_txt2(file_path2,X1)
new_M1=M1

m = len(new_M1)
p = len(M2)
n = len(new_M1[0])
model = gp.Model("CNOT_min_mpn")

C = {}
for i in range(m):
    for j in range(p):
        C[i,j] = model.addVar(vtype=GRB.BINARY, name=f"C_{i}_{j}")

t = {}
for i in range(m):
    for j in range(n):
        t[i,j] = model.addVar(vtype=GRB.INTEGER, name=f"t_{i}_{j}")
model.setObjective(
    gp.quicksum(C[i,j] for i in range(m) for j in range(p)),
    GRB.MINIMIZE
)
for i in range(m):
    for j in range(n):
        model.addConstr(
            gp.quicksum(C[i,k] * M2[k][j] for k in range(p)) == 2 * t[i,j] + new_M1[i][j],
            name=f"mod2_{i}_{j}"
        )

model.optimize()
if model.status == GRB.OPTIMAL:
    C_sol = [[int(C[i,j].X) for j in range(p)] for i in range(m)]
    for row in C_sol:
        print(row)
    print("\nMatrix C as a list of lists:")
    print(C_sol)
    print("\nObjective value (sum of all C[i,j]):", model.objVal)
else:
    print("No feasible solution found.")
"""the corresponding input and output bit positions in the circuit"""
inputs =[10, 54, 53, 47, 51, 48, 55, 45, 15, 57, 2, 13, 56, 14, 9, 0, 7, 12, 1, 8, 11, 44, 46, 49, 50, 52]+[24,26,27,31,38,40,41,42]
output = [i for i in range(58,66)]

CNOT_list = []

for row_idx, row in enumerate(C_sol):
    ones = [i for i, val in enumerate(row) if val == 1]
    if not ones:
        continue

    target_idx = row_idx
    target_qubit = output[target_idx]
    for control_idx in ones:
        control_qubit = inputs[control_idx]
        CNOT_list.append([control_qubit, target_qubit])
    output.append(target_qubit)

print("CNOT operations [control, target]:")
print("CNOT list",CNOT_list)

"""If the model takes too long to solve, 
the program can be terminated at any time to obtain the current best solution"""