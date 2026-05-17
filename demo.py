#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工业机械故障诊断助手 - 终端交互 Demo
零外部依赖，直接运行: python demo.py

功能:
  - 输入故障现象，返回诊断结果
  - 支持规则引擎 + 知识库查询
  - 交互式循环，输入 q 退出
"""
import sys
import os
from pathlib import Path

# 确保项目根目录在 sys.path 中
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from knowledge_base.loader import FaultKnowledgeBase
from rules_engine.engine import RulesEngine


# ANSI 颜色
class C:
    HEADER = '\033[95m'
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


def print_banner():
    print(f"""
{C.HEADER}{'='*60}
  工业机械核心部件故障诊断与维护助手  v0.1
  轴承 / 电机 / 规则引擎 + 知识库
{'='*60}{C.END}
  输入故障现象进行诊断 | 输入 {C.BOLD}q{C.END} 退出 | 输入 {C.BOLD}kb{C.END} 浏览知识库
""")


def diagnose(query: str, engine: RulesEngine, kb: FaultKnowledgeBase):
    """执行诊断并打印结果"""
    print(f"\n{C.BOLD}>> 诊断输入:{C.END} {query}")
    print(f"{C.DIM}{'─'*50}{C.END}")

    # 规则匹配
    results = engine.diagnose(query)

    if not results:
        print(f"  {C.WARN}未匹配到已知故障规则。{C.END}")
        print(f"  建议：尝试补充更多故障现象，如'振动'、'温度'、'噪声'等关键词。")

        # 模糊匹配：搜索知识库
        keywords = query.replace('，', ' ').replace('。', ' ').split()
        for kw in keywords:
            found = kb.search_faults_by_symptom(kw)
            if found:
                print(f"\n  {C.DIM}相关知识（按症状'{kw}'匹配）:{C.END}")
                for f in found[:2]:
                    print(f"    - {f.name}: {', '.join(f.symptoms[:3])}")
                break
        return

    print(f"  匹配到 {C.BOLD}{len(results)}{C.END} 条规则\n")

    for i, r in enumerate(results, 1):
        fault = kb.get_fault_by_id(r.fault_id)
        conf_color = C.OK if r.confidence >= 0.8 else (C.WARN if r.confidence >= 0.6 else C.DIM)
        bar_len = int(r.confidence * 20)
        bar = '█' * bar_len + '░' * (20 - bar_len)

        print(f"  {C.BOLD}[{i}] {r.message}{C.END}")
        print(f"      置信度: {conf_color}{bar} {r.confidence:.0%}{C.END}  |  匹配关键词: {', '.join(r.matched_keywords)}")

        if fault:
            print(f"      故障名称: {C.BOLD}{fault.name}{C.END} ({fault.component})")
            print(f"      严重程度: {C.WARN if fault.severity == '高' else C.END}{fault.severity}{C.END}")
            print(f"      相关部件: {', '.join(fault.related_parts)}")
            print(f"      可能原因:")
            for c in fault.causes:
                print(f"        {C.DIM}•{C.END} {c}")
            print(f"      解决方案:")
            for s in fault.solutions:
                print(f"        {C.OK}→{C.END} {s}")
            print(f"      预防措施:")
            for p in fault.prevention:
                print(f"        {C.DIM}◇{C.END} {p}")

            if fault.detection_method:
                print(f"      检测方法: {', '.join(fault.detection_method)}")
        print()


def browse_kb(kb: FaultKnowledgeBase):
    """浏览知识库"""
    print(f"\n{C.BOLD}知识库概览{C.END}")
    print(f"{C.DIM}{'─'*50}{C.END}")
    print(f"  轴承故障: {len(kb.bearing_faults)} 条")
    for f in kb.bearing_faults:
        sev = C.WARN + f.severity + C.END if f.severity == '高' else f.severity
        print(f"    {C.DIM}{f.id}{C.END} {f.name} [{sev}]")
        print(f"      症状: {', '.join(f.symptoms[:3])}")

    print(f"\n  电机故障: {len(kb.motor_faults)} 条")
    for f in kb.motor_faults:
        sev = C.WARN + f.severity + C.END if f.severity == '高' else f.severity
        print(f"    {C.DIM}{f.id}{C.END} {f.name} [{sev}]")
        print(f"      症状: {', '.join(f.symptoms[:3])}")

    print(f"\n  {C.DIM}维护计划:{C.END}")
    schedule = kb.get_maintenance_schedule()
    for period, items in schedule.items():
        print(f"    {C.BOLD}{period}{C.END}: {', '.join(items[:3])}")


def main():
    # 修复 Windows 控制台编码
    if sys.platform == "win32":
        os.system("chcp 65001 >nul 2>&1")
        sys.stdout.reconfigure(encoding='utf-8')

    # 初始化
    print(f"{C.DIM}正在加载知识库和规则引擎...{C.END}")
    kb = FaultKnowledgeBase()
    if not kb.load():
        print(f"{C.FAIL}知识库加载失败，请检查 fault_data.json{C.END}")
        sys.exit(1)

    engine = RulesEngine()
    if not engine.load_rules():
        print(f"{C.FAIL}规则引擎加载失败，请检查 rules.json{C.END}")
        sys.exit(1)

    print(f"{C.OK}知识库: {len(kb.all_faults)} 条故障知识{C.END}")
    print(f"{C.OK}规则引擎: {len(engine.rules)} 条诊断规则{C.END}")

    # 启动交互
    print_banner()

    # 推荐测试用例
    print(f"  {C.DIM}试试输入:{C.END}")
    examples = [
        "轴承振动大，有异常噪声",
        "电机温度很高，有异味",
        "电机启动困难，电流大",
        "轴承摩擦声明显，温度升高",
        "电机振动异常，基础松动"
    ]
    for ex in examples:
        print(f"    {C.DIM}> {ex}{C.END}")
    print()

    while True:
        try:
            user_input = input(f"{C.BOLD}请输入故障现象> {C.END}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}再见！{C.END}")
            break

        if not user_input:
            continue
        if user_input.lower() in ('q', 'quit', 'exit'):
            print(f"{C.DIM}再见！{C.END}")
            break
        if user_input.lower() == 'kb':
            browse_kb(kb)
            continue
        if user_input.lower() == 'help':
            print(f"  命令: {C.BOLD}q{C.END} 退出 | {C.BOLD}kb{C.END} 浏览知识库 | 直接输入故障现象进行诊断")
            continue

        diagnose(user_input, engine, kb)


if __name__ == "__main__":
    main()
