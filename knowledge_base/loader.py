"""
知识库数据结构和加载器
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from pathlib import Path


@dataclass
class FaultKnowledge:
    """故障知识数据结构"""
    id: str
    name: str
    component: str
    symptoms: List[str]
    causes: List[str]
    solutions: List[str]
    prevention: List[str]
    severity: str  # "低"、"中"、"高"
    related_parts: List[str]
    typical_frequency: Optional[str] = None
    typical_parameter: Optional[str] = None
    detection_method: Optional[List[str]] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "component": self.component,
            "symptoms": self.symptoms,
            "causes": self.causes,
            "solutions": self.solutions,
            "prevention": self.prevention,
            "severity": self.severity,
            "related_parts": self.related_parts,
            "typical_frequency": self.typical_frequency,
            "typical_parameter": self.typical_parameter,
            "detection_method": self.detection_method
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FaultKnowledge":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            component=data.get("component", ""),
            symptoms=data.get("symptoms", []),
            causes=data.get("causes", []),
            solutions=data.get("solutions", []),
            prevention=data.get("prevention", []),
            severity=data.get("severity", "中"),
            related_parts=data.get("related_parts", []),
            typical_frequency=data.get("typical_frequency"),
            typical_parameter=data.get("typical_parameter"),
            detection_method=data.get("detection_method", [])
        )


class FaultKnowledgeBase:
    """故障知识库管理器"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path(__file__).parent / "fault_data.json"
        self.bearing_faults: List[FaultKnowledge] = []
        self.motor_faults: List[FaultKnowledge] = []
        self.common_knowledge: dict = {}
        self.all_faults: List[FaultKnowledge] = []
        
    def load(self) -> bool:
        """加载知识库数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载轴承故障知识
            for item in data.get("bearing_faults", []):
                fault = FaultKnowledge.from_dict(item)
                self.bearing_faults.append(fault)
                self.all_faults.append(fault)
            
            # 加载电机故障知识
            for item in data.get("motor_faults", []):
                fault = FaultKnowledge.from_dict(item)
                self.motor_faults.append(fault)
                self.all_faults.append(fault)
            
            # 加载通用知识
            self.common_knowledge = data.get("common_knowledge", {})
            
            return True
        except Exception as e:
            print(f"加载知识库失败: {e}")
            return False
    
    def get_fault_by_id(self, fault_id: str) -> Optional[FaultKnowledge]:
        """根据ID获取故障知识"""
        for fault in self.all_faults:
            if fault.id == fault_id:
                return fault
        return None
    
    def get_faults_by_component(self, component: str) -> List[FaultKnowledge]:
        """根据部件类型获取故障知识"""
        return [f for f in self.all_faults if f.component == component]
    
    def search_faults_by_symptom(self, symptom_keyword: str) -> List[FaultKnowledge]:
        """根据症状关键词搜索故障"""
        results = []
        keyword = symptom_keyword.lower()
        for fault in self.all_faults:
            for symptom in fault.symptoms:
                if keyword in symptom.lower():
                    results.append(fault)
                    break
        return results
    
    def get_maintenance_schedule(self) -> dict:
        """获取维护计划"""
        return self.common_knowledge.get("maintenance_intervals", {})
    
    def get_all_symptoms(self) -> List[str]:
        """获取所有症状列表（去重）"""
        symptoms = set()
        for fault in self.all_faults:
            symptoms.update(fault.symptoms)
        return list(symptoms)
    
    def summarize_for_rag(self) -> List[dict]:
        """生成用于RAG检索的知识片段"""
        documents = []
        for fault in self.all_faults:
            # 每个故障生成多个文档片段
            doc1 = {
                "id": f"{fault.id}_symptoms",
                "content": f"故障名称：{fault.name}（{fault.component}）\n症状：{', '.join(fault.symptoms)}\n严重程度：{fault.severity}",
                "metadata": {"fault_id": fault.id, "type": "symptoms"}
            }
            doc2 = {
                "id": f"{fault.id}_causes",
                "content": f"故障名称：{fault.name}\n可能原因：{', '.join(fault.causes)}",
                "metadata": {"fault_id": fault.id, "type": "causes"}
            }
            doc3 = {
                "id": f"{fault.id}_solutions",
                "content": f"故障名称：{fault.name}\n解决方案：{', '.join(fault.solutions)}\n预防措施：{', '.join(fault.prevention)}",
                "metadata": {"fault_id": fault.id, "type": "solutions"}
            }
            documents.extend([doc1, doc2, doc3])
        return documents


if __name__ == "__main__":
    # 测试代码
    kb = FaultKnowledgeBase()
    if kb.load():
        print(f"✅ 知识库加载成功")
        print(f"  轴承故障: {len(kb.bearing_faults)} 条")
        print(f"  电机故障: {len(kb.motor_faults)} 条")
        print(f"  总计: {len(kb.all_faults)} 条")
        
        # 测试搜索
        print("\n🔍 搜索症状 '振动':")
        results = kb.search_faults_by_symptom("振动")
        for r in results:
            print(f"  - {r.name} (ID: {r.id})")
        
        # 生成RAG文档
        print(f"\n📚 生成RAG文档: {len(kb.summarize_for_rag())} 条")
    else:
        print("❌ 知识库加载失败")
