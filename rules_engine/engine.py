# -*- coding: utf-8 -*-
"""
规则引擎 - 基于关键词匹配的故障诊断
支持 JSON 格式规则文件（零依赖）
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuleResult:
    """规则匹配结果"""
    rule_name: str
    fault_id: str
    confidence: float
    message: str
    matched_keywords: List[str]


class RulesEngine:
    """故障诊断规则引擎"""

    def __init__(self, rules_path: Optional[str] = None):
        # 优先使用 JSON，回退 YAML
        default_json = Path(__file__).parent / "rules.json"
        default_yaml = Path(__file__).parent / "rules.yaml"
        if rules_path:
            self.rules_path = Path(rules_path)
        elif default_json.exists():
            self.rules_path = default_json
        elif default_yaml.exists():
            self.rules_path = default_yaml
        else:
            self.rules_path = default_json
        self.rules: List[dict] = []

    def load_rules(self) -> bool:
        """加载规则文件（自动识别 JSON/YAML）"""
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.rules_path.suffix == '.json':
                data = json.loads(content)
            else:
                # 尝试 YAML（如果已安装）
                try:
                    import yaml
                    data = yaml.safe_load(content)
                except ImportError:
                    # 简单 YAML 解析 fallback
                    data = self._simple_yaml_parse(content)

            self.rules = data.get("rules", [])
            return True
        except Exception as e:
            print(f"加载规则失败: {e}")
            return False

    def _simple_yaml_parse(self, content: str) -> dict:
        """极简 YAML 解析器（仅支持本项目规则格式）"""
        import re
        data = {"rules": []}
        current_rule = None
        current_cond = None
        in_conclusion = False

        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 规则开始
            if stripped.startswith('- name:'):
                if current_rule:
                    data["rules"].append(current_rule)
                current_rule = {"name": stripped.split(':', 1)[1].strip().strip('"\''), "conditions": [], "conclusion": {}}
                current_cond = None
                in_conclusion = False
            elif current_rule:
                if stripped.startswith('conditions:'):
                    current_cond = None
                elif stripped.startswith('conclusion:'):
                    in_conclusion = True
                    current_cond = None
                elif in_conclusion:
                    if 'fault_id:' in stripped:
                        current_rule["conclusion"]["fault_id"] = stripped.split(':', 1)[1].strip().strip('"\'')
                    elif 'confidence:' in stripped:
                        current_rule["conclusion"]["confidence"] = float(stripped.split(':', 1)[1].strip())
                    elif 'message:' in stripped:
                        current_rule["conclusion"]["message"] = stripped.split(':', 1)[1].strip().strip('"\'')
                elif stripped.startswith('- type:'):
                    current_cond = {"type": stripped.split(':', 1)[1].strip().strip('"\'')}
                    current_rule["conditions"].append(current_cond)
                elif current_cond is not None:
                    if 'keywords:' in stripped:
                        kws = re.findall(r'"([^"]+)"', stripped)
                        current_cond["keywords"] = kws
                    elif 'match_type:' in stripped:
                        current_cond["match_type"] = stripped.split(':', 1)[1].strip().strip('"\'')
                    elif 'min_match:' in stripped:
                        current_cond["min_match"] = int(stripped.split(':', 1)[1].strip())

        if current_rule:
            data["rules"].append(current_rule)
        return data

    def diagnose(self, user_input: str) -> List[RuleResult]:
        """
        对用户输入进行规则诊断

        Args:
            user_input: 用户描述的故障现象

        Returns:
            匹配的规则结果列表，按置信度降序排列
        """
        results = []
        input_lower = user_input.lower()

        for rule in self.rules:
            conditions = rule.get("conditions", [])
            all_matched = []

            for cond in conditions:
                keywords = cond.get("keywords", [])
                match_type = cond.get("match_type", "any")
                min_match = cond.get("min_match", 1)

                matched = [kw for kw in keywords if kw in input_lower]

                if match_type == "all" and len(matched) == len(keywords):
                    all_matched.extend(matched)
                elif match_type == "any" and len(matched) >= min_match:
                    all_matched.extend(matched)

            if all_matched:
                conclusion = rule.get("conclusion", {})
                results.append(RuleResult(
                    rule_name=rule.get("name", ""),
                    fault_id=conclusion.get("fault_id", ""),
                    confidence=conclusion.get("confidence", 0.5),
                    message=conclusion.get("message", ""),
                    matched_keywords=list(set(all_matched))
                ))

        # 按置信度降序排列
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results


if __name__ == "__main__":
    engine = RulesEngine()
    if engine.load_rules():
        print(f"✅ 加载 {len(engine.rules)} 条规则")

        test_cases = [
            "电机温度很高，有异味",
            "轴承振动大，有异常噪声",
            "电机启动困难，电流很大",
            "轴承摩擦声明显，温度升高"
        ]
        for case in test_cases:
            print(f"\n🔍 输入: {case}")
            results = engine.diagnose(case)
            for r in results:
                print(f"  → [{r.confidence:.0%}] {r.message} (匹配: {r.matched_keywords})")
