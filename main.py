import os
import sys
import argparse
from mindLint import MindLint
from ast_operations import Ast_parser, get_attributes, get_operations

def save_report(report: dict, file_path: str):
    """将结构化报告保存为可读性强的文本文件（根据错误/警告自动加后缀）."""
    target_dir = os.path.dirname(file_path)
    result_dir = os.path.join(target_dir, 'result')
    os.makedirs(result_dir, exist_ok=True)

    # 确定基本文件名
    filename = os.path.basename(file_path).replace('.py', '')

    # 根据错误/警告情况修改文件名
    if report["errors"]:
        filename = f"{filename}_e"
    elif report["warnings"]:
        filename = f"{filename}_w"
    else:
        filename = filename

    result_file_path = os.path.join(result_dir, f"result_{filename}.txt")

    # 构建人类可读文本内容
    report_text = ""

    if not report["errors"] and not report["warnings"]:
        report_text = "no error or warining\n"
    else:
        if report["errors"]:
            report_text += "❌ [Errors]\n"
            report_text += "------------------------\n"
            for err in report["errors"]:
                report_text += f"{err.strip()}\n"
            report_text += "\n"

        if report["warnings"]:
            report_text += "⚠️ [Warnings]\n"
            report_text += "------------------------\n"
            for warn in report["warnings"]:
                report_text += f"{warn.strip()}\n"

    # 保存到文件
    try:
        with open(result_file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"📄 报告已保存至：{result_file_path}")
    except Exception as e:
        print(f"[❌] 报告保存失败：{e}")


def read_file(file_path):
    """读取单个文件内容。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content, content.split('\n')
    except Exception as e:
        print(f"[❌] 无法读取文件：{file_path}，错误：{e}")
        return None, None


def parse_ast(file_content):
    """构建AST并提取变量赋值与函数调用。"""
    ast_parser = Ast_parser()
    root = ast_parser.parser(file_content)
    assign_list = ast_parser.extract_variable_assign()
    call_list = ast_parser.extract_function_calls()
    return assign_list, call_list

def analyze_file(file_path):
    """分析单个文件流程。"""
    print(f"\n📂 分析文件: {file_path}")
    file_content, file_lines = read_file(file_path)
    if not file_content:
        return

    assign_list, call_list = parse_ast(file_content)
    attributes, att_line_numbers = get_attributes(assign_list)
    operations, opt_line_numbers = get_operations(call_list)

    # 输出提取信息
    print('\n📌 MQ_Attributes:')
    print('==========================================')
    print(attributes, '\n')

    print('📌 MQ_Operations:')
    print('==========================================')
    print(operations, '\n')

    checker = MindLint()
    checker.check(attributes, att_line_numbers, operations, opt_line_numbers, file_lines)

    report = checker.get_report()
    print('\n📋 检查报告:')
    print('==========================================')
    print(report)

    save_report(report, file_path)  # ✅ 保存报告

def analyze_folder(folder_path):
    """分析文件夹内所有 Python 文件。"""
    print(f"\n📁 分析文件夹: {folder_path}")
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                analyze_file(file_path)


def parse_args():
    """命令行参数解析。"""
    parser = argparse.ArgumentParser(description='MindQuantum量子代码静态分析器')
    parser.add_argument('--mode', type=int, choices=[0, 1], required=True, help='模式选择：0为文件夹模式，1为单文件模式')
    parser.add_argument('--path', type=str, required=True, help='目标文件或文件夹路径')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == 1:
        if os.path.isfile(args.path):
            analyze_file(args.path)
        else:
            print(f"[❌] 文件路径不存在或不是文件：{args.path}")
    elif args.mode == 0:
        if os.path.isdir(args.path):
            analyze_folder(args.path)
        else:
            print(f"[❌] 文件夹路径不存在或不是目录：{args.path}")


if __name__ == '__main__':
    main()
