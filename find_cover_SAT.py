from sage.all import *
from math import log2
from math import ceil
from itertools import combinations
from functools import reduce
from operator import mul
"""
The file save path: file *.eqs, *.cnf, *.out 
Need two tools:
(1) the ANF-to-CNF conveter: Bosphorus
    https://github.com/meelgroup/bosphorus
(2) the SAT Solver: Kissat
    https://github.com/arminbiere/kissat
"""
def pre_work():
    # the save path
    if not os.path.isdir("covers_eqs"):
        os.mkdir("covers_eqs")
    if os.path.exists("kissat") and os.path.exists("bosphorus"):
        os.system("chmod +x bosphorus kissat")
    else:
        print("##### Please install Bosphorus(ANF-to-CNF converter) and Kissat(SAT Solver) #####")
        print("##### Then place the executable file in the current directory #####")
        print("##### https://github.com/meelgroup/bosphorus #####")
        print("##### https://github.com/arminbiere/kissat #####")
        exit()
def list2_to_1(A):
    B_ = []
    for Ai in A:
        B_ += Ai
    return B_
def Boolean_Inner_Product(A, X):
    l = len(A)
    AX = 0
    for i in range(l):
        AX = AX + A[i] * X[i]
    return AX
def get_terms_str(n):
    from itertools import combinations
    inputs = [i for i in range(n)]
    x_terms = ["1"]
    for ki in range(1, n + 1):
        numbers = list(combinations(inputs, ki))
        for num_tuple in numbers:
            xi_list = ["x" + str(i) for i in num_tuple]
            xi_str = "*".join(xi_list)
            x_terms.append(xi_str)
    return x_terms
def get_terms_Boolean(n, B):
    x_items_str = get_terms_str(n=n)
    x_items_poly = [1]
    for x_items in x_items_str[1:]:
        x_list = x_items.split("*")
        xi = B(x_list[0])
        for xj in x_list[1:]:
            xi = xi * B(xj)
        x_items_poly.append(xi)
    return x_items_poly

def get_M_Boolean_monomials(n, B):
    from scipy.special import comb
    terms = get_terms_Boolean(n=n, B=B)
    M = []
    maxd = ceil(log2(n))

    idx = 0
    for d in range(maxd + 1):
        left = 1 + pow(2, d - 1)
        right = 1 + pow(2, d)
        if d == 0:
            left, right = 0, 2

        term_number = 0
        for i in range(left, right):
            term_number += comb(n, i)

        M.append(terms[idx:idx + int(term_number)])
        idx += int(term_number)

    return M
def poly_to_eqs(poly, n, eqs_basis=[]):
    x_items_str = get_terms_str(n=n)
    monomial_list = str(poly).replace(" ", "").split("+")
    monomial_coeffes = {}
    for xi in x_items_str:
        monomial_coeffes[xi] = []
    monomial_coeffes["1"] = []
    for monomial in monomial_list:
        if monomial[0] == "x":
            monomial_coeffes[monomial].append("1")
            continue
        first_x_index = monomial.find("x")
        if first_x_index == -1:
            monomial_coeffes["1"].append(monomial)
            continue
        xi = monomial[first_x_index:]
        coeff = monomial[:first_x_index-1]
        monomial_coeffes[xi].append(coeff)

    basic_eqs = []
    if len(eqs_basis) == 0:
        eqs_basis = x_items_str
    for xi in eqs_basis:
        eq = "+".join(monomial_coeffes[str(xi)])
        if len(eq) == 0:
            continue
        basic_eqs.append(eq)
    return basic_eqs


def get_values_from_kissat(an, file_name):
    with open(file_name, encoding="utf-8") as f:
        content = f.read()
        if "UNSATISFIABLE" in content or "caught signal" in content:
            print("UNSAT")
            return [0 for i in range(an)]

        vals_str = content.split("s SATISFIABLE\n")[1].split(
            "c ---- [ profiling ] ---------------------------------------------------------\n")[0]
    vals_str = vals_str.replace("v", "").replace("c", "").replace("\n", " ")
    vals_list = vals_str.split(" ")
    vals = []
    for si in vals_list:
        if len(si) < 1:
            continue
        vals.append(0 if "-" in si else 1)
        if len(vals) > an:
            break
    return vals
def find_common_covers_eqs(F, n, maxd, ks, BA, M, prefix):
    ai = 0
    bi = len(F) * (n + 1 + sum(ks))
    for d in range(maxd):
        bi += 2 * ks[d] * (n + 1 + sum(ks[:d]))
    XC_star = M[0][:]
    eqs = []
    for d in range(maxd):
        factor_basis = list2_to_1(M[:d + 1])
        cover_basis = list2_to_1(M[:d + 2])
        n1 = len(factor_basis)
        n2 = len(cover_basis)
        n3 = len(XC_star)
        for i in range(ks[d]):
            Di1_coeffes = [BA[ai + j] for j in range(n3)]
            Di2_coeffes = [BA[ai + n3 + j] for j in range(n3)]
            ai += 2 * n3
            eqs += [str(Di1_coeffes[0]), str(Di2_coeffes[0])]
            Di1 = Boolean_Inner_Product(Di1_coeffes, XC_star)
            Di2 = Boolean_Inner_Product(Di2_coeffes, XC_star)
            Di1_star_coeffes = [BA[bi + j] for j in range(n1)]
            Di2_star_coeffes = [BA[bi + n1 + j] for j in range(n1)]
            Ci_star_coeffes = [BA[bi + 2 * n1 + j] for j in range(n2)]
            bi += 2 * n1 + n2
            Di1_star = Boolean_Inner_Product(Di1_star_coeffes, factor_basis)
            Di2_star = Boolean_Inner_Product(Di2_star_coeffes, factor_basis)
            Ci = Di1_star * Di2_star
            Ci_star = Boolean_Inner_Product(Ci_star_coeffes, cover_basis)

            eqs += poly_to_eqs(Di1 + Di1_star, n)
            eqs += poly_to_eqs(Di2 + Di2_star, n)
            eqs += poly_to_eqs(Ci + Ci_star, n)
            XC_star.append(Ci_star)
    n3 = len(XC_star)
    for f in F:
        f_star_coeffes = [BA[ai + i] for i in range(n3)]
        ai += n3
        f_star = Boolean_Inner_Product(f_star_coeffes, XC_star)
        eqs += poly_to_eqs(poly=f + f_star, n=n)
    with open(f"{prefix}.eqs", "w") as f:
        f.write("\n".join(eqs).replace("a", "x"))

def find_common_covers_result(F, n, maxd, ks, M, prefix):
    result = []
    an = len(F) * (n + 1 + sum(ks))
    for d in range(maxd):
        an += 2 * ks[d] * (n + 1 + sum(ks[:d]))
    VA = get_values_from_kissat(an=an, file_name=f"{prefix}.out")

    ai = 0
    XC_star = M[0][:]
    XC_str = ["1"] + [f"x{i}" for i in range(n)] + [f"M{i}" for i in range(sum(ks))]
    for d in range(maxd):
        n3 = len(XC_star)
        result.append(f"############## AND-depth from {d} to {d + 1} ##############")
        for i in range(ks[d]):
            Di1_coeffes = [VA[ai + j] for j in range(n3)]
            Di2_coeffes = [VA[ai + n3 + j] for j in range(n3)]
            ai += 2 * n3
            Di1 = Boolean_Inner_Product(Di1_coeffes, XC_star)
            Di2 = Boolean_Inner_Product(Di2_coeffes, XC_star)
            Ci = Di1 * Di2
            XC_star.append(Ci)

            Di1_terms = [XC_str[j] for j in range(n3) if Di1_coeffes[j] == 1]
            Di2_terms = [XC_str[j] for j in range(n3) if Di2_coeffes[j] == 1]
            result.append(f"M{sum(ks[:d]) + i}=({'+'.join(Di1_terms)})*({'+'.join(Di2_terms)})")

    result.append(f"############## build final targets ################")
    n3 = len(XC_star)
    for i in range(len(F)):
        f_coeffes = [VA[ai + i] for i in range(n3)]
        ai += n3
        f = Boolean_Inner_Product(f_coeffes, XC_star)

        f_terms = [XC_str[j] for j in range(n3) if f_coeffes[j] == 1]
        result.append(f"Y{i}={'+'.join(f_terms)}")
    result.append(f"###################################################")
    print("\n".join(result))

def prod(xs):
    if len(xs) == 0:
        return 1
    return reduce(mul, xs)
def at_most_weight_eqs(vars_, w):
    m = len(vars_)
    if w < 0:
        raise ValueError(f"Invalid weight w={w}.")
    if w >= m:
        return []
    eqs = []
    for S in combinations(vars_, w + 1):
        eqs.append(str(prod(S)))
    return eqs
def find_MINW_covers_eqs(F, n, maxd, ks, BA, M, prefix, w):
    ai = 0
    bi = len(F) * (n + 1 + sum(ks))
    for d in range(maxd):
        bi += 2 * ks[d] * (n + 1 + sum(ks[:d]))

    XC_star = M[0][:]
    eqs = []
    all_D_coeffes = []
    for d in range(maxd):
        factor_basis = list2_to_1(M[:d + 1])
        cover_basis = list2_to_1(M[:d + 2])
        n1 = len(factor_basis)
        n2 = len(cover_basis)
        n3 = len(XC_star)
        for i in range(ks[d]):
            Di1_coeffes = [BA[ai + j] for j in range(n3)]
            Di2_coeffes = [BA[ai + n3 + j] for j in range(n3)]
            ai += 2 * n3
            eqs += [str(Di1_coeffes[0]), str(Di2_coeffes[0])]
            if d == 0:
                print("len", len(Di1_coeffes[1:]))
                eqs += at_most_weight_eqs(Di1_coeffes[1:], w)
                eqs += at_most_weight_eqs(Di2_coeffes[1:], w)
            if d == 1:
                print("len", len(Di1_coeffes[1:]))
                eqs += at_most_weight_eqs(Di1_coeffes[1:], w)
                eqs += at_most_weight_eqs(Di2_coeffes[1:], w)

            Di1 = Boolean_Inner_Product(Di1_coeffes, XC_star)
            Di2 = Boolean_Inner_Product(Di2_coeffes, XC_star)
            Di1_star_coeffes = [BA[bi + j] for j in range(n1)]
            Di2_star_coeffes = [BA[bi + n1 + j] for j in range(n1)]
            Ci_star_coeffes = [BA[bi + 2 * n1 + j] for j in range(n2)]
            bi += 2 * n1 + n2
            Di1_star = Boolean_Inner_Product(Di1_star_coeffes, factor_basis)
            Di2_star = Boolean_Inner_Product(Di2_star_coeffes, factor_basis)
            Ci = Di1_star * Di2_star
            Ci_star = Boolean_Inner_Product(Ci_star_coeffes, cover_basis)

            eqs += poly_to_eqs(Di1 + Di1_star, n)
            eqs += poly_to_eqs(Di2 + Di2_star, n)
            eqs += poly_to_eqs(Ci + Ci_star, n)
            XC_star.append(Ci_star)
    n3 = len(XC_star)
    for f in F:
        f_star_coeffes = [BA[ai + i] for i in range(n3)]
        ai += n3
        f_star = Boolean_Inner_Product(f_star_coeffes, XC_star)
        eqs += poly_to_eqs(poly=f + f_star, n=n)
    with open(f"{prefix}.eqs", "w") as f:
        f.write("\n".join(eqs).replace("a", "x"))


def find_covers_eqs_MINW(f, n, d, k, BA, M, prefix, w):
    factor_basis = list2_to_1(M[:d])
    cover_basis  = list2_to_1(M[:d + 1])

    max_depth_basis = M[d]
    n1 = len(factor_basis)
    n2 = len(cover_basis)
    cn = 2 * n1 + n2
    f_star = 0
    eqs = []
    for i in range(k):
        Di1_coeffes = [BA[i * cn + j] for j in range(n1)]
        Di2_coeffes = [BA[i * cn + n1 + j] for j in range(n1)]
        Ci_coeffes  = [BA[i * cn + 2 * n1 + j] for j in range(n2)]

        eqs += [
            str(Di1_coeffes[0]),
            str(Di2_coeffes[0])
        ]
        # print("len",len(Di1_coeffes[1:]))
        eqs += at_most_weight_eqs(Di1_coeffes[1:], w)
        eqs += at_most_weight_eqs(Di2_coeffes[1:], w)
        Di1 = Boolean_Inner_Product(Di1_coeffes, factor_basis)
        Di2 = Boolean_Inner_Product(Di2_coeffes, factor_basis)
        Ci  = Boolean_Inner_Product(Ci_coeffes, cover_basis)

        Ci_star = Di1 * Di2
        eqs += poly_to_eqs(Ci + Ci_star, n)
        f_star += Ci
    eqs += poly_to_eqs(
        poly=f + f_star,
        n=n,
        eqs_basis=max_depth_basis
    )

    eqs_save = "\n".join(eqs).replace("a", "x")
    with open(f"{prefix}.eqs", "w") as ff:
        ff.write(eqs_save)