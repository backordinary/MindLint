import ast
import logging
import re


def get_args(opt):
    """
    解析函数调用字符串，提取参数列表，支持嵌套函数调用和链式方法调用。
    """
    if isinstance(opt, int) or isinstance(opt, float):  # ✅ 处理数值类型
        return [str(opt)]  # 直接转换为字符串返回

    if not isinstance(opt, str):  # ✅ 确保 opt 是字符串
        print(f"[ERROR] get_args() 期望字符串，但接收到 {type(opt)}: {opt}")
        return []

    try:
        tree = ast.parse(opt.strip(), mode='eval')
        if isinstance(tree.body, ast.Call):
            return extract_args_from_call(tree.body)
        else:
            print(f"[ERROR] 无法解析的函数调用字符串: {opt}")
            return []
    except SyntaxError as e:
        print(f"[ERROR] 语法错误: {e}，字符串: {opt}")
        return []
    except Exception as e:
        print(f"[ERROR] 解析 {opt} 失败，异常: {e}")
        return []

def extract_args_from_call(node):
    """
    提取函数调用的参数，支持位置参数和关键字参数。
    """
    args = []

    # 解析位置参数
    for arg in node.args:
        if isinstance(arg, ast.Constant):
            args.append(repr(arg.value))  # 处理 "字符串" 和 数值
        elif isinstance(arg, ast.Name):
            args.append(arg.id)  # 变量名
        elif isinstance(arg, ast.Call):
            func_name = get_func_name(arg.func)
            nested_args = extract_args_from_call(arg)
            full_call = f"{func_name}({', '.join(nested_args)})"
            args.append(full_call)
        else:
            args.append(ast.unparse(arg))  # 其他情况转换回字符串

    # **解析关键字参数**
    kwargs = extract_kwargs_from_call(node)

    return args + kwargs  # ✅ 位置参数 + 关键字参数 一起返回

def extract_kwargs_from_call(node):
    """
    提取函数调用中的关键字参数（key=value）。
    """
    return [f"{kw.arg}={ast.unparse(kw.value)}" for kw in node.keywords]

def get_func_name(func_node):
    """
    获取函数名称，支持嵌套结构。
    """
    if isinstance(func_node, ast.Name):
        return func_node.id
    elif isinstance(func_node, ast.Attribute):
        return f"{get_func_name(func_node.value)}.{func_node.attr}"
    return ast.unparse(func_node)  # 其他情况转换回字符串


def get_values(args, var_list):
    """
    获取参数的实际值，如果参数是变量，则从 var_list 中查找其值。
    """
    values = []
    for arg in args:
        try:
            # 尝试将参数解析为字面量
            value = ast.literal_eval(arg)
        except (ValueError, SyntaxError):
            # 如果解析失败，认为参数是变量名，从 var_list 中查找其值
            value = next((assign[1] for assign in var_list if assign[0] == arg), arg)
        values.append(value)
    return values

def get_keywords(args, values):
    """
    将参数和对应的值分为位置参数和关键字参数。
    """
    new_args = []
    new_values = []
    for arg, value in zip(args, values):
        if '=' in arg:
            key, val = arg.split('=', 1)
            new_args.append(key.strip())
            new_values.append(val.strip())
        else:
            new_args.append(arg)
            new_values.append(value)
    return new_args, new_values
# 实际上这个函数对于所有的链式调用都可以使用


def extract_all_gates(opt):
    """
    提取调用链中的所有函数和类名
    示例：
        Circuit().h(0).cx(1,0) => ['Circuit()', 'h(0)', 'cx(1,0)']
        CNOT.on(0, 1) => ['CNOT', 'on(0, 1)']
    """
    opt = opt.replace(" ", "")
    results = []

    # 特例处理 CNOT.on(0, 1) => ['CNOT', 'on(0, 1)']
    if "." in opt and not opt.startswith("Circuit()"):
        parts = opt.split(".")
        if "(" in parts[0]:  # 说明类似 CNOT(...)，不需要拆
            pass
        elif len(parts) >= 2:
            results.append(parts[0])  # 类名
            call = ".".join(parts[1:])  # 剩下是链式
            matches = re.findall(r'\w+\([^()]*\)', call)
            results.extend(matches)
            return results

    # 常规链式调用，如 Circuit().h(0).x(1)
    matches = re.findall(r'\w+\([^()]*\)', opt)
    # 补上最前面的类名调用，如 Circuit()
    prefix_match = re.match(r'^\w+\(\)', opt)
    if prefix_match:
        class_call = prefix_match.group(0)
        if class_call not in matches:
            matches.insert(0, class_call)

    return matches



# **📌 全局变量存储 Simulator 量子比特数**
simulator_qubits = 999

# 全局变量：存储当前线路最大量子比特数
simulator_qubits = 999

def checker_IIS(var_list, att_line_numbers, opt_list, opt_line_numbers):
    """
    IIS 检查器：检查 Simulator 初始化及后续量子门是否超出初始状态范围。
      1. Simulator(...) 的 n_qubits 参数：
         - float → Error（不接受小数）
         - 非 int/float → Warning（请检查参数）
         - int <= 0 → Error（非正整数）
         - int > 0 → 合法，更新 simulator_qubits
      2. NoiseBackend(...) 同上
      3. 普遍性检查：on() 与无参门调用时，量子比特编号不得 >= simulator_qubits
      4. 特例：当 simulator_qubits==1 时，不得使用受控门
    """
    global simulator_qubits
    valid_backends = ['mqvector', 'mqvector_gpu', 'mqmatrix']
    issues = []

    # —— 1. 初始化 Simulator 参数检查 —— #
    for opt, lineno in zip(opt_list, opt_line_numbers):
        if 'Simulator' in opt:
            args = get_args(opt)
            values = get_values(args, var_list)

            # 参数不足
            if not values:
                msg = f"[ERROR] Simulator 初始化参数不足 (行 {lineno})"
                issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                print(msg)
                continue

            backend = values[0].strip('"').strip("'")
            print(f"[INFO] 解析到 backend 参数: {backend} (行 {lineno})")

            # —— 1.1 NoiseBackend 分支 —— #
            if backend.startswith('NoiseBackend('):
                noise_args = get_args(backend)
                noise_values = get_values(noise_args, var_list)

                if len(noise_values) < 3:
                    msg = (f"[ERROR] NoiseBackend 初始化参数不足 (行 {lineno})，"
                           f"参数: {noise_args}，值: {noise_values}")
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)
                    continue

                base_sim = noise_values[0].strip('"').strip("'")
                n_qubits = noise_values[1]
                # adder = noise_values[2]  # 可忽略

                if base_sim not in valid_backends:
                    msg = f"[ERROR] 无效的 base_sim: {base_sim} (行 {lineno})"
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)

                # —— 新增对 float 的检测 —— #
                if isinstance(n_qubits, float):
                    msg = (f"[ERROR] n_qubits 参数为小数，不接受小数 (行 {lineno})，值: {n_qubits}")
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)
                # 非 int/float 再作为 Warning
                elif not isinstance(n_qubits, int):
                    msg = (f"[WARNING] n_qubits 参数非字面量整数，无法确定大小，请检查 (行 {lineno})，值: {n_qubits}")
                    issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                    print(msg)
                else:
                    if n_qubits <= 0:
                        msg = f"[ERROR] n_qubits 不是正整数 (行 {lineno})，值: {n_qubits}"
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                        print(msg)
                    else:
                        simulator_qubits = n_qubits
                        print(f"[INFO] 记录全局变量: simulator_qubits = {simulator_qubits}")

            # —— 1.2 普通 Simulator 分支 —— #
            else:
                if backend not in valid_backends:
                    msg = f"[ERROR] 无效的 backend: {backend} (行 {lineno})"
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)

                if len(values) >= 2:
                    n_qubits = values[1]

                    if isinstance(n_qubits, float):
                        msg = (f"[ERROR] n_qubits 参数为小数，不接受小数 (行 {lineno})，值: {n_qubits}")
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                        print(msg)
                    elif not isinstance(n_qubits, int):
                        msg = (f"[WARNING] n_qubits 参数非字面量整数，无法确定大小，请检查 (行 {lineno})，值: {n_qubits}")
                        issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                        print(msg)
                    else:
                        if n_qubits <= 0:
                            msg = f"[ERROR] n_qubits 不是正整数 (行 {lineno})，值: {n_qubits}"
                            issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                            print(msg)
                        else:
                            simulator_qubits = n_qubits
                            print(f"[INFO] 记录全局变量: simulator_qubits = {simulator_qubits}")

    # —— 2. 普遍性检查：超出范围的 on() 与无参门 —— #
    none_para_gates = ["h","x","y","z","s","t","sx","swap","iswap","cnot"]
    for opt, lineno in zip(opt_list, opt_line_numbers):
        calls = extract_all_gates(opt)
        for call in calls:
            # on(...)
            if call.startswith("on("):
                vals = []
                for v in get_values(get_args(call), var_list):
                    if isinstance(v, list):
                        vals.extend(v)
                    elif v != 'None':
                        vals.append(v)
                ivals = [i for i in vals if isinstance(i, int)]
                if ivals and max(ivals) >= simulator_qubits:
                    msg = (f"[ERROR] `on()` 调用了 {max(ivals)} 号比特，"
                           f"超出最大支持的量子比特 {simulator_qubits} (行 {lineno})")
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)

            # none-para 门
            if "(" in call:
                g = call.split("(")[0]
                if g in none_para_gates:
                    vals = []
                    for v in get_values(get_args(call), var_list):
                        if isinstance(v, list):
                            vals.extend(v)
                        elif v != 'None':
                            vals.append(v)
                    ivals = [i for i in vals if isinstance(i, int)]
                    if ivals and max(ivals) >= simulator_qubits:
                        msg = (f"[ERROR] {g} 门调用了 {max(ivals)} 号比特，"
                               f"超出最大支持的量子比特 {simulator_qubits} (行 {lineno})")
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                        print(msg)

    # —— 3. 特例：单比特时不得使用受控门 —— #
    if simulator_qubits == 1:
        controlled = ["cs","ch","cx","cnot","cp","mcp","rcx","rccx","rcccx",
                      "crx","cry","crz","csdg","cswap","csx","cu","ccx",
                      "mcx","cy","cz","ccz"]
        for opt, lineno in zip(opt_list, opt_line_numbers):
            for call in extract_all_gates(opt):
                if "(" in call and call.split("(")[0] in controlled:
                    msg = (f"[ERROR] 受控门 {call.split('(')[0]} 被单量子比特线路调用 (行 {lineno})")
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    print(msg)

    print("[INFO] IIS 规则检查结束")
    return issues

def checker_IM(var_list, att_line_numbers, opt_list, opt_line_numbers):
    """
    📌 Incorrect Measurement检查器：
    检查量子比特被测量后是否继续作为控制位被使用。
    """
    issues = []
    measured_qubits = set()
    controlled_gate = [
        "h", "x", "y", "z", "s", "t", "sx", "swap", "iswap",
        "cs", "ch", "cx","cnot", "cp", "mcp", "rcx", "rccx", "rcccx",
        "crx", "cry", "crz", "csdg", "cswap", "csx", "cu",
        "ccx", "mcx", "cy", "cz", "ccz"
    ]

    for opt, lineno in zip(opt_list, opt_line_numbers):
        gate_calls = extract_all_gates(opt)
        for idx, chainCall in enumerate(gate_calls):
            gate_name = chainCall.split("(")[0]  # 保持大小写敏感

            # ✅ 处理 measure_all
            if gate_name == "measure_all":
                for i in range(simulator_qubits):
                    measured_qubits.add(i)
                continue

            # ✅ 处理 measure(...),measure的第二个参数不代表控制位
            if gate_name == "measure":
                args = get_args(chainCall)
                values = get_values(args, var_list)
                v = values[0]
                if isinstance(v, list):
                    msg = f"[ERROR] measure 门只能定义在一个qubit上 (行 {lineno})"
                    print(msg)
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                else:
                    try:
                        measured_qubits.add(int(v))
                    except Exception:
                        continue
                continue

            # ✅ 处理 Measure(...)
            if gate_name == "Measure":
                # 若下一个调用为 on(...)，则需要一并分析
                next_call = gate_calls[idx + 1] if idx + 1 < len(gate_calls) else ""
                if next_call.startswith("on("):
                    on_args = get_args(next_call)
                    on_values = get_values(on_args, var_list)
                    if isinstance(on_values[0], list):
                        msg = f"[ERROR] measure 门只能定义在一个qubit上 (行 {lineno})"
                        print(msg)
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                    if len(on_values) >= 2:
                        msg = f"[ERROR] Measure 门不应包含控制位 (行 {lineno})"
                        print(msg)
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})

                    # 记录 obj_qubits 被测量
                    obj_part = on_values[0] if on_values else None
                    if isinstance(obj_part, list):
                        measured_qubits.update([int(q) for q in obj_part if isinstance(q, int)])
                    elif isinstance(obj_part, int):
                        measured_qubits.add(obj_part)
                continue

            # ✅ 检查控制门是否作用于 measured_qubits
            if gate_name in controlled_gate:
                args = get_args(chainCall)
                values = get_values(args, var_list)
                if len(values) > 1:
                    ctrl_candidates = values[1]

                    if isinstance(ctrl_candidates, list):
                        for ctrl in ctrl_candidates:
                            if isinstance(ctrl, int) and ctrl in measured_qubits:
                                msg = f"[WARNING] 被测量的 qubit {ctrl} 被用作控制位 ({gate_name}) (行 {lineno})"
                                print(msg)
                                issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                    else:
                        try:
                            if int(ctrl_candidates) in measured_qubits:
                                msg = f"[WARNING] 被测量的 qubit {ctrl_candidates} 被用作控制位 ({gate_name}) (行 {lineno})"
                                print(msg)
                                issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                        except Exception:
                            continue

            # ✅ 检查 Gate().on(obj, ctrl) 的调用
            if gate_name == "on" and idx > 0:
                prev_gate = gate_calls[idx - 1].split("(")[0]
                args = get_args(chainCall)
                values = get_values(args, var_list)
                if prev_gate != "Measure":
                    if len(values) >= 2:
                        ctrl_part = values[1]
                        if isinstance(ctrl_part, list):
                            for ctrl in ctrl_part:
                                if isinstance(ctrl, int) and ctrl in measured_qubits:
                                    msg = f"[WARNING] 被测量的 qubit {ctrl} 被用作控制位 (.on 调用) (行 {lineno})"
                                    print(msg)
                                    issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                        else:
                            try:
                                if int(ctrl_part) in measured_qubits:
                                    msg = f"[WARNING] 被测量的 qubit {ctrl_part} 被用作控制位 (.on 调用) (行 {lineno})"
                                    print(msg)
                                    issues.append({"type": "Warning", "lineno": lineno, "msg": msg})
                            except Exception:
                                pass
    print("[INFO] IM 规则检查完成")
    return issues

def checker_PE(var_list, att_line_numbers, opt_list, opt_line_numbers):
    issues = []
    # 检查量子比特是否在控制位和受控位上重复
    none_para_gates = ["h","x","y","z","s","t","sx","swap","iswap","cnot"]
    for opt, lineno in zip(opt_list, opt_line_numbers):
        gate_calls = extract_all_gates(opt)  # ✅ 获取所有量子门
        for chainCall in gate_calls:
            if chainCall.startswith("on("):
                on_args = get_args(chainCall)
                on_values = get_values(on_args, var_list)
                # 控制位和受控位可能是int也可能是list[int]
                flat_values = []
                if len(on_args) > 2 :
                    msg = f"[ERROR] On的调用有多余的参数"
                    print(msg)
                    issues.append({"type": "Error", "lineno": lineno, "msg": msg})
                for val in on_values:
                    if isinstance(val, list):
                        flat_values.extend(val)
                    elif val != 'None':
                        flat_values.append(val)

                if flat_values:
                    if len(flat_values) != len(set(flat_values)):
                        msg = f"[ERROR] 控制位和受控位当中有元素重复"
                        print(msg)
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})

            # ✅ 提取门名和参数部分，如 h(0), swap(1,2) 等
            if "(" in chainCall:
                gate_name = chainCall.split("(")[0]
                args = get_args(chainCall)
                values = get_values(args, var_list)
                flat_values = []
                for val in values:
                    if isinstance(val, list):
                        flat_values.extend(val)
                    elif val != 'None':
                        flat_values.append(val)
                # ✅ 检查不带额外参数的门
                if gate_name in none_para_gates and flat_values:
                    if len(flat_values) != len(set(flat_values)):
                        msg = f"[ERROR] 控制位和受控位当中有元素重复"
                        print(msg)
                        issues.append({"type": "Error", "lineno": lineno, "msg": msg})
    print("[INFO] PE 规则检查完成")
    return issues

def checker_CE(var_list, att_line_numbers, opt_list, opt_line_numbers):
    issues = []

    print("[INFO] CE 规则检查完成")
    return issues

# **📌 规则检查字典**
Rules = {
    'IIS': checker_IIS,
    'IM' : checker_IM,
    'PE' : checker_PE,
}

# **📌 规则描述**
Description = {
    'IIS': 'Incorrect Initial State',
    'IM': 'Incorrect Measurement',
    'PE' : 'Parameters Error',
}

# **📌 结果存储**
Results = {rule: False for rule in Rules.keys()}

# **📌 MindQuantum 静态分析类**
from concurrent.futures import ThreadPoolExecutor

class MindLint:
    def __init__(self):
        self.rules = Rules
        self.results = {key: False for key in Rules.keys()}
        self.report_errors = []
        self.report_warnings = []

    def check(self, var_list, att_line_numbers, opt_list, opt_line_numbers, file_lines):
        print("\n========================= 🚀 开始代码分析 🚀 =========================\n")
        global simulator_qubits
        simulator_qubits = 999
        # 优先执行 IIS
        if "IIS" in self.rules:
            print("[INFO] 先运行 `checker_IIS` 以确保 `simulator_qubits` 变量存储")
            issues = self.rules["IIS"](var_list, att_line_numbers, opt_list, opt_line_numbers)
            for issue in issues:
                self._record_issue("IIS", issue, file_lines)

        # 执行其他规则
        remaining_rules = [k for k in self.rules if k != "IIS"]

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda task: (task, self.rules[task](var_list, att_line_numbers, opt_list, opt_line_numbers)),
                remaining_rules
            )
            for task, issues in results:
                if issues is None:
                    continue
                elif isinstance(issues, int):
                    # 直接是一个错误行号
                    self._record_issue(task, issues, file_lines)
                elif isinstance(issues, list):
                    # 是一个包含多个警告的列表
                    for issue in issues:
                        self._record_issue(task, issue, file_lines)
                else:
                    print(f"[WARNING] 无法识别的返回值类型来自规则 {task}：{issues}")


        print("\n========================= ✅ 代码分析完成 ✅ =========================\n")

    def _record_issue(self, task, issue, file_lines):
        self.results[task] = True
        line = file_lines[int(issue["lineno"]) - 1]
        msg = f"Type: {task} - {Description[task]}\n{issue['type']} at line {issue['lineno']}: {line}\n{issue['msg']}"

        if issue["type"] == "Error":
            self.report_errors.append(msg)
            print(f"[❌] 错误: {msg}")
        elif issue["type"] == "Warning":
            self.report_warnings.append(msg)
            print(f"[⚠️] 警告: {msg}")
    def get_report(self):
        """
        生成错误与警告报告，打印输出并返回结构化结果。

        返回值:
            {
                "errors": List[str],
                "warnings": List[str]
            }
        """
        print("\n========================= 📋 检查报告 =========================\n")

        report_errors = getattr(self, "report_errors", [])
        report_warnings = getattr(self, "report_warnings", [])

        if report_errors:
            print("❌ 错误列表（Errors）:")
            for i, err in enumerate(report_errors, 1):
                print(f"{i}. {err}\n")
        else:
            print("✅ 没有发现错误（Errors）\n")

        if report_warnings:
            print("⚠️ 警告列表（Warnings）:")
            for i, warn in enumerate(report_warnings, 1):
                print(f"{i}. {warn}\n")
        else:
            print("✅ 没有发现警告（Warnings）\n")

        print("========================= 🧾 报告结束 =========================\n")

        return {
            "errors": report_errors,
            "warnings": report_warnings
        }