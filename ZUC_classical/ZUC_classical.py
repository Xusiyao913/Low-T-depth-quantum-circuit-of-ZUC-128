from find_cover_SAT import *
import subprocess
import time
import os
import signal

def ZUC_S0_P23_classical():
    print("ZUC_S0_P23 classical result:")
    pre_work()
    n = 8
    a_variable = ["a" + str(i) for i in range(100000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0, x1, x2, x3 = B("x0"), B("x1"), B("x2"), B("x3")
    x4, x5, x6, x7 = B("x4"), B("x5"), B("x6"), B("x7")
    M = get_M_Boolean_monomials(n=n, B=B)
    ZUC_Sbox_ANF = [x0*x1*x3*x7 + x0*x1*x3 + x0*x1*x5 + x0*x1*x6 + x0*x1*x7 + x0*x2*x3 + x0*x2*x5 + x0*x2*x6 + x0*x2*x7 + x0*x3*x5 + x0*x3*x6 + x0*x3 + x0*x5 + x0*x6 + x0*x7 + x1*x2*x3*x5 + x1*x2*x3*x6 + x1*x2*x5 + x1*x2*x6 + x1*x2*x7 + x1*x3*x7 + x1*x5 + x1*x6 + x1 + x2*x3 + x2 + x3*x5 + x3*x6 + x3*x7 + x3 + x5*x7 + x6*x7 + x6,
                    x0*x1*x2*x4 + x0*x1*x3 + x0*x1*x6 + x0*x1*x7 + x0*x1 + x0*x2*x3*x6 + x0*x2*x3*x7 + x0*x2*x3 + x0*x2*x6 + x0*x2*x7 + x0*x3*x6 + x0*x3*x7 + x0 + x1*x2*x3*x4 + x1*x2*x3*x6 + x1*x2*x3*x7 + x1*x2*x4 + x1*x2 + x1*x3*x4 + x1*x3 + x1*x6 + x1*x7 + x1 + x2*x3*x4 + x2*x3 + x2*x4 + x2*x6 + x2*x7 + x3*x4 + x4*x6 + x4*x7 + x6,
                    x0*x1*x2*x4 + x0*x1*x2*x5 + x0*x1*x2*x6 + x0*x1*x3*x6 + x0*x1*x3 + x0*x1*x4 + x0*x1*x5 + x0*x1*x6 + x0*x2*x3*x6 + x0*x2*x3 + x0*x2*x4 + x0*x2*x5 + x0*x2*x6 + x0*x3*x4 + x0*x3*x5 + x0*x4 + x0*x5 + x0 + x1*x2*x3*x6 + x1*x2*x6 + x1*x2 + x1*x3*x4 + x1*x3*x5 + x1*x3 + x1*x4 + x1*x5 + x2*x3*x4 + x2*x3*x5 + x2*x3*x6 + x2*x4 + x2*x5 + x3*x6 + x3 + x4*x6 + x5*x6 + x5 + x6 + 1,
                    x0*x1*x2*x4 + x0*x1*x2*x7 + x0*x1*x2 + x0*x1*x3*x4 + x0*x1*x3*x7 + x0*x1*x3 + x0*x2*x3*x5 + x0*x2*x3 + x0*x3*x4 + x0*x3*x7 + x0*x3 + x0*x5 + x1*x2*x4 + x1*x2*x5 + x1*x2*x7 + x1*x3 + x1*x4 + x1*x7 + x2*x3*x4 + x2*x3*x7 + x2*x3 + x2*x4 + x2*x5 + x2*x7 + x2 + x3*x4 + x3*x5 + x3*x7 + x4*x5 + x4 + x5*x7 + x5 + 1]
    maxd = 2
    #ks: the number of Toffoli gates for each layer
    ks = [16,4]
    prefix = "covers_eqs/ZUC_Sbox"
    find_common_covers_eqs(F=ZUC_Sbox_ANF, n=n, maxd=maxd, ks=ks, BA=BA, M=M, prefix=prefix)
    for file in [
        f"{prefix}.cnf",
        f"{prefix}.out",
        f"{prefix}.bosphorus.err",
        f"{prefix}.kissat.err"
    ]:
        if os.path.exists(file):
            os.remove(file)

    print("Running bosphorus...")
    print("当前工作目录:", os.getcwd())
    print("bosphorus 是否存在:", os.path.exists("./bosphorus"))
    print("bosphorus 是否可执行:", os.access("./bosphorus", os.X_OK))
    print("eqs 是否存在:", os.path.exists(f"{prefix}.eqs"))
    if os.path.exists(f"{prefix}.eqs"):
        print("eqs file size =", os.path.getsize(f"{prefix}.eqs") / 1024 / 1024, "MB")
    ret1 = subprocess.run(
        [
            "./bosphorus",
            "--anfread", f"{prefix}.eqs",
            "--cnfwrite", f"{prefix}.cnf",
            "--verb", "0"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("bosphorus returncode =", ret1.returncode)
    if ret1.stdout:
        print("bosphorus stdout:")
        print(ret1.stdout)

    if ret1.stderr:
        print("bosphorus stderr:")
        print(ret1.stderr)

    if ret1.returncode != 0:
        if ret1.returncode == -9:
            raise RuntimeError("bosphorus 被 SIGKILL 杀掉了，大概率是内存不够")
        elif ret1.returncode == 137:
            raise RuntimeError("bosphorus 被 killed，退出码 137，大概率是内存不够")
        else:
            raise RuntimeError(f"bosphorus 运行失败，returncode = {ret1.returncode}")

    cnf_size = os.path.getsize(f"{prefix}.cnf") / 1024 / 1024
    print(f"CNF file size = {cnf_size:.2f} MB")

    with open(f"{prefix}.cnf", "r") as f:
        for line in f:
            if line.startswith("p cnf"):
                print("CNF header:", line.strip())
                break

    print("Running kissat...")

    with open(f"{prefix}.out", "w") as fout:
        ret2 = subprocess.run(
            [
                "./kissat",
                f"{prefix}.cnf",
                "--sat"
            ],
            stdout=fout,
            stderr=subprocess.PIPE,
            text=True
        )

    print("kissat returncode =", ret2.returncode)

    if ret2.stderr:
        print("kissat stderr:")
        print(ret2.stderr)

    if ret2.returncode == -signal.SIGKILL:
        raise RuntimeError("kissat 被 SIGKILL 杀掉了，通常是内存不够")

    if ret2.returncode == 137:
        raise RuntimeError("kissat 被 killed，退出码 137，通常是内存不够")

    if ret2.returncode == 10:
        print("kissat result: SATISFIABLE")

    elif ret2.returncode == 20:
        print("kissat result: UNSATISFIABLE")
        raise RuntimeError("该约束不可满足，找不到满足条件的 cover")    

    elif ret2.returncode == 0:
        print("kissat finished with returncode 0")

    else:
        raise RuntimeError(f"kissat 异常退出，returncode = {ret2.returncode}")
    with open(f"{prefix}.out", "r") as f:
        out_content = f.read()

    if "s SATISFIABLE" not in out_content and "s UNSATISFIABLE" not in out_content:
        print("kissat 输出最后 1000 个字符：")
        print(out_content[-1000:])
        raise RuntimeError("kissat 没有正常结束，不能读取结果")
    find_common_covers_result(F=ZUC_Sbox_ANF, n=n, maxd=maxd, ks=ks, M=M, prefix=prefix)

def ZUC_S0_P2_classical_MINW():
    print("ZUC_S0_P2 classical result:")
    # pre_work()
    n = 4
    a_variable = ["a" + str(i) for i in range(10000)]
    x_variable = ["x" + str(i) for i in range(n)]
    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0,x1,x2,x3 = B("x0"),B("x1"),B("x2"),B("x3")
    M = get_M_Boolean_monomials(n=n, B=B)

    ZUC_Sbox_ANF = [x0 * x2 * x3 + x1 * x2 * x3 + x0 * x1 + x0 * x2 + x0 * x3 + x1 + x2 + 1
            , x0 * x1 * x2 + x0 * x1 * x3 + x0 * x3 + x1 * x2 + x2 * x3 + x1 + x2 + x3
            , x0 * x1 * x2 + x0 * x1 + x0 * x2 + x0 * x3 + x1 * x3 + x2 * x3 + x0 + x1 + x2
            , x1 * x2 * x3 + x0 * x1 + x0 * x2 + x0 * x3 + x1 * x2 + x0 + x1 + x3]

    maxd = 2
    ks = [2,4]
    w=2
    prefix = "covers_eqs/ZUC_Sbox"
    find_MINW_covers_eqs(F=ZUC_Sbox_ANF, n=n, maxd=maxd, ks=ks, BA=BA, M=M, prefix=prefix, w=w)
    for file in [
        f"{prefix}.cnf",
        f"{prefix}.out",
        f"{prefix}.bosphorus.err",
        f"{prefix}.kissat.err"
    ]:
        if os.path.exists(file):
            os.remove(file)

    print("Running bosphorus...")

    print("当前工作目录:", os.getcwd())
    print("bosphorus 是否存在:", os.path.exists("./bosphorus"))
    print("bosphorus 是否可执行:", os.access("./bosphorus", os.X_OK))
    print("eqs 是否存在:", os.path.exists(f"{prefix}.eqs"))

    if os.path.exists(f"{prefix}.eqs"):
        print("eqs file size =", os.path.getsize(f"{prefix}.eqs") / 1024 / 1024, "MB")

    ret1 = subprocess.run(
        [
            "./bosphorus",
            "--anfread", f"{prefix}.eqs",
            "--cnfwrite", f"{prefix}.cnf",
            "--verb", "0"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("bosphorus returncode =", ret1.returncode)

    if ret1.stdout:
        print("bosphorus stdout:")
        print(ret1.stdout)

    if ret1.stderr:
        print("bosphorus stderr:")
        print(ret1.stderr)

    if ret1.returncode != 0:
        if ret1.returncode == -9:
            raise RuntimeError("bosphorus 被 SIGKILL 杀掉了，大概率是内存不够")
        elif ret1.returncode == 137:
            raise RuntimeError("bosphorus 被 killed，退出码 137，大概率是内存不够")
        else:
            raise RuntimeError(f"bosphorus 运行失败，returncode = {ret1.returncode}")

    cnf_size = os.path.getsize(f"{prefix}.cnf") / 1024 / 1024
    print(f"CNF file size = {cnf_size:.2f} MB")

    with open(f"{prefix}.cnf", "r") as f:
        for line in f:
            if line.startswith("p cnf"):
                print("CNF header:", line.strip())
                break

    print("Running kissat...")

    with open(f"{prefix}.out", "w") as fout:
        ret2 = subprocess.run(
            [
                "./kissat",
                f"{prefix}.cnf",
                "--sat"
            ],
            stdout=fout,
            stderr=subprocess.PIPE,
            text=True
        )

    print("kissat returncode =", ret2.returncode)

    if ret2.stderr:
        print("kissat stderr:")
        print(ret2.stderr)

    if ret2.returncode == -signal.SIGKILL:
        raise RuntimeError("kissat 被 SIGKILL 杀掉了，通常是内存不够")

    if ret2.returncode == 137:
        raise RuntimeError("kissat 被 killed，退出码 137，通常是内存不够")

    if ret2.returncode == 10:
        print("kissat result: SATISFIABLE")

    elif ret2.returncode == 20:
        print("kissat result: UNSATISFIABLE")
        raise RuntimeError("该约束不可满足，找不到满足条件的 cover")

    elif ret2.returncode == 0:
        print("kissat finished with returncode 0")

    else:
        raise RuntimeError(f"kissat 异常退出，returncode = {ret2.returncode}")
    with open(f"{prefix}.out", "r") as f:
        out_content = f.read()

    if "s SATISFIABLE" not in out_content and "s UNSATISFIABLE" not in out_content:
        print("kissat 输出最后 1000 个字符：")
        print(out_content[-1000:])
        raise RuntimeError("kissat 没有正常结束，不能读取结果")

    find_common_covers_result(F=ZUC_Sbox_ANF, n=n, maxd=maxd, ks=ks, M=M, prefix=prefix)
def ZUC_S0_P1_classical_MINW():
    print("ZUC_S0_P1 classical result:")
    # pre_work()
    n = 4
    a_variable = ["a" + str(i) for i in range(10000)]
    x_variable = ["x" + str(i) for i in range(n)]

    # Boolean polynomial ring variable (a, x)
    B = BooleanPolynomialRing(names=(a_variable + x_variable))
    BA = [B(a) for a in a_variable]
    x0,x1,x2,x3 = B("x0"),B("x1"),B("x2"),B("x3")
    M = get_M_Boolean_monomials(n=n, B=B)

    ZUC_S0P1_ANF = [x0 + x2 + x0 * x2 + x2 * x3 + 1,
                    x1 + x3 + x1 * x2 + x1 * x3,
                    x1 + x3 + x0 * x3 + x1 * x3,
                    x0 + x2 + x0 * x2 + x0 * x1 + 1]
    maxd = 1
    ks = [4]
    w = 2
    prefix = "covers_eqs/ZUC_Sbox"
    find_MINW_covers_eqs(F=ZUC_S0P1_ANF, n=n, maxd=maxd, ks=ks, BA=BA, M=M, prefix=prefix, w=w)
    for file in [
        f"{prefix}.cnf",
        f"{prefix}.out",
        f"{prefix}.bosphorus.err",
        f"{prefix}.kissat.err"
    ]:
        if os.path.exists(file):
            os.remove(file)

    print("Running bosphorus...")

    print("当前工作目录:", os.getcwd())
    print("bosphorus 是否存在:", os.path.exists("./bosphorus"))
    print("bosphorus 是否可执行:", os.access("./bosphorus", os.X_OK))
    print("eqs 是否存在:", os.path.exists(f"{prefix}.eqs"))

    if os.path.exists(f"{prefix}.eqs"):
        print("eqs file size =", os.path.getsize(f"{prefix}.eqs") / 1024 / 1024, "MB")

    ret1 = subprocess.run(
        [
            "./bosphorus",
            "--anfread", f"{prefix}.eqs",
            "--cnfwrite", f"{prefix}.cnf",
            "--verb", "0"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("bosphorus returncode =", ret1.returncode)

    if ret1.stdout:
        print("bosphorus stdout:")
        print(ret1.stdout)

    if ret1.stderr:
        print("bosphorus stderr:")
        print(ret1.stderr)

    if ret1.returncode != 0:
        if ret1.returncode == -9:
            raise RuntimeError("bosphorus 被 SIGKILL 杀掉了，大概率是内存不够")
        elif ret1.returncode == 137:
            raise RuntimeError("bosphorus 被 killed，退出码 137，大概率是内存不够")
        else:
            raise RuntimeError(f"bosphorus 运行失败，returncode = {ret1.returncode}")

    cnf_size = os.path.getsize(f"{prefix}.cnf") / 1024 / 1024
    print(f"CNF file size = {cnf_size:.2f} MB")

    with open(f"{prefix}.cnf", "r") as f:
        for line in f:
            if line.startswith("p cnf"):
                print("CNF header:", line.strip())
                break

    print("Running kissat...")

    with open(f"{prefix}.out", "w") as fout:
        ret2 = subprocess.run(
            [
                "./kissat",
                f"{prefix}.cnf",
                "--sat"
            ],
            stdout=fout,
            stderr=subprocess.PIPE,
            text=True
        )

    print("kissat returncode =", ret2.returncode)

    if ret2.stderr:
        print("kissat stderr:")
        print(ret2.stderr)

    if ret2.returncode == -signal.SIGKILL:
        raise RuntimeError("kissat 被 SIGKILL 杀掉了，通常是内存不够")

    if ret2.returncode == 137:
        raise RuntimeError("kissat 被 killed，退出码 137，通常是内存不够")

    if ret2.returncode == 10:
        print("kissat result: SATISFIABLE")

    elif ret2.returncode == 20:
        print("kissat result: UNSATISFIABLE")
        raise RuntimeError("该约束不可满足，找不到满足条件的 cover")

    elif ret2.returncode == 0:
        print("kissat finished with returncode 0")

    else:
        raise RuntimeError(f"kissat 异常退出，returncode = {ret2.returncode}")
    with open(f"{prefix}.out", "r") as f:
        out_content = f.read()

    if "s SATISFIABLE" not in out_content and "s UNSATISFIABLE" not in out_content:
        print("kissat 输出最后 1000 个字符：")
        print(out_content[-1000:])
        raise RuntimeError("kissat 没有正常结束，不能读取结果")

    find_common_covers_result(F=ZUC_S0P1_ANF, n=n, maxd=maxd, ks=ks, M=M, prefix=prefix)
t1 = time.time()
ZUC_S0_P23_classical()
# ZUC_S0_P2_classical_MINW()
# ZUC_S0_P1_classical_MINW()
t2 = time.time()
print("ZUC classical:", t2-t1)