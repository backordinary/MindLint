import ast

class Ast_parser:
    def __init__(self) -> None:
        self.file_text = None
        self.root = None
        self.assign_list = []
        self.call_list = []

    def parser(self, file_text):
        """ 解析 Python 代码并生成 AST 语法树 """
        self.file_text = file_text
        try:
            self.root = ast.parse(file_text)
            print("[INFO] AST 解析成功")
        except SyntaxError as e:
            print(f"[ERROR] 语法错误: {e}")
            self.root = None
        return self.root

    def extract_variable_assign(self):
        """ 提取所有变量赋值语句 """
        if self.root is None:
            return []

        self.assign_list = []  # 清空列表，避免重复存储
        for node in ast.walk(self.root):
            if isinstance(node, ast.Assign):
                self.assign_list.append(node)
        return self.assign_list

    def extract_function_calls(self):
        """ 提取所有函数调用语句 """
        if self.root is None:
            return []

        self.call_list = []  # 清空列表，避免重复存储
        for node in ast.walk(self.root):
            if isinstance(node, ast.Call):
                self.call_list.append(node)
        return self.call_list


def process_constant(node):
    if isinstance(node.value, int):
        return str(node.value)
    elif isinstance(node.value, str):
        return '"' + node.value + '"'
    return str(node.value)

def process_args(args):
    """解析函数参数"""
    result = []
    for arg in args:
        if isinstance(arg, ast.Constant):
            result.append(process_constant(arg))
        elif isinstance(arg, ast.Name):
            result.append(process_name(arg))
        elif isinstance(arg, ast.Call):
            result.append(process_call(arg))
        elif isinstance(arg, ast.Attribute):
            result.append(process_attribute(arg))
        elif isinstance(arg, ast.Subscript):
            result.append(process_subscript(arg))
        elif isinstance(arg, ast.List):
            result.append(process_list(arg))
        elif isinstance(arg, ast.keyword):
            value = process_keyword(arg)
            if value:
                result.append(value)
        elif isinstance(arg, ast.UnaryOp) and isinstance(arg.op, ast.USub) and isinstance(arg.operand, ast.Constant):
            # 处理负数常量
            result.append(f"-{arg.operand.value}")
    return ','.join(filter(None, result))  # 过滤 None 值，避免 join 出错


def process_keyword(node):
    """ 解析关键字参数 """
    label = node.arg
    value = ""
    if isinstance(node.value, ast.Constant):
        value = process_constant(node.value)
    elif isinstance(node.value, ast.Name):
        value = process_name(node.value)
    elif isinstance(node.value, ast.Call):
        value = process_call(node.value)
    elif isinstance(node.value, ast.Attribute):
        value = process_attribute(node.value)
    elif isinstance(node.value, ast.Subscript):
        value = process_subscript(node.value)
    elif isinstance(node.value, ast.List):
        value = process_list(node.value)

    return f"{label}={value}" if value else label  # 确保返回值不是 None

def process_list(node):
    """ 解析列表 """
    result = []
    for arg in node.elts:
        if isinstance(arg, ast.Constant):
            result.append(process_constant(arg))
        elif isinstance(arg, ast.Name):
            result.append(process_name(arg))
        elif isinstance(arg, ast.Call):
            result.append(process_call(arg))
        elif isinstance(arg, ast.Attribute):
            result.append(process_attribute(arg))
        elif isinstance(arg, ast.Subscript):
            result.append(process_subscript(arg))
        elif isinstance(arg, ast.List):
            result.append(process_list(arg))
    return '[' + ','.join(result) + ']'

def process_index(node):
    """ 解析索引操作 """
    if isinstance(node, ast.Constant):
        return process_constant(node)
    elif isinstance(node, ast.Name):
        return process_name(node)
    elif isinstance(node, ast.Call):
        return process_call(node)
    elif isinstance(node, ast.Attribute):
        return process_attribute(node)
    elif isinstance(node, ast.Subscript):
        return process_subscript(node)
    return ''

def process_subscript(node):
    """ 解析下标操作 """
    label = '[' + process_index(node.slice) + ']'
    if isinstance(node.value, ast.Name):
        label = process_name(node.value) + label
    return label

def process_name(node):
    """ 解析变量名称 """
    return str(node.id)

def process_attribute(node):
    """ 解析对象属性 """
    label = '.' + node.attr
    if isinstance(node.value, ast.Call):
        label = process_call(node.value) + label
    elif isinstance(node.value, ast.Attribute):
        label = process_attribute(node.value) + label
    elif isinstance(node.value, ast.Name):
        label = process_name(node.value) + label
    return label

def process_call(node):
    """ 解析函数调用 """
    args = node.args + node.keywords
    label = '(' + process_args(args) + ')'
    if isinstance(node.func, ast.Call):
        label = process_call(node.func) + label
    elif isinstance(node.func, ast.Attribute):
        label = process_attribute(node.func) + label
    elif isinstance(node.func, ast.Name):
        label = process_name(node.func) + label
    return label

def process_dict(node):
    """ 解析字典 """
    if node.keys is None or node.values is None:
        return "{}", []

    results = []
    assign_list = []
    for key, value in zip(node.keys, node.values):
        k_label = process_index(key)
        v_label = process_index(value)
        results.append(f"{k_label}:{v_label}")
        assign_list.append((k_label, v_label))

    return "{" + ','.join(results) + "}", assign_list

def get_attributes(assign_list):
    """ 获取变量赋值的属性 """
    attributes = []
    dict_assign = None
    line_numbers = []
    for assign in assign_list:
        if isinstance(assign.targets[0], ast.Tuple):
            name = ','.join([var.id for var in assign.targets[0].elts if isinstance(var, ast.Name)])
        elif isinstance(assign.targets[0], ast.Name):
            name = assign.targets[0].id
        elif isinstance(assign.targets[0], ast.Subscript):
            name = process_subscript(assign.targets[0])
        else:
            name = "UNKNOWN"

        value = "UNKNOWN"
        if isinstance(assign.value, ast.Constant):
            value = assign.value.value
        elif isinstance(assign.value, ast.Call):
            value = process_call(assign.value)
        elif isinstance(assign.value, ast.Attribute):
            value = process_attribute(assign.value)
        elif isinstance(assign.value, ast.Dict):
            value, dict_assign = process_dict(assign.value)

        attributes.append((name, str(value)))
        line_numbers.append(assign.lineno)

    if dict_assign:
        attributes.extend(dict_assign)

    return attributes, line_numbers

def get_operations(call_list):
    """ 获取函数调用信息 """
    operations = []
    line_numbers = []
    for call in call_list:
        detail = process_call(call)
        operations.append(detail)
        line_numbers.append(call.lineno)
    return operations, line_numbers
