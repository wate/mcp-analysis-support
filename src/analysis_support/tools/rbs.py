"""PMBOK RBS (Risk Breakdown Structure) implementation."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class RiskCategory(Enum):
    """リスクカテゴリの定義"""
    TECHNICAL = "技術的リスク"
    EXTERNAL = "外部リスク"
    ORGANIZATIONAL = "組織リスク"
    PROJECT_MANAGEMENT = "プロジェクト管理リスク"


class RiskImpact(Enum):
    """リスクの影響度"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class RiskProbability(Enum):
    """リスクの発生確率"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class RiskItem:
    """個別のリスクアイテム"""
    def __init__(self, name: str, description: str, category: RiskCategory,
                 subcategory: str, probability: RiskProbability = RiskProbability.MEDIUM,
                 impact: RiskImpact = RiskImpact.MEDIUM):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.category = category
        self.subcategory = subcategory
        self.probability = probability
        self.impact = impact
        self.risk_score = probability.value * impact.value
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "probability": {
                "value": self.probability.value,
                "label": self._get_probability_label()
            },
            "impact": {
                "value": self.impact.value,
                "label": self._get_impact_label()
            },
            "risk_score": self.risk_score,
            "priority": self._get_priority_level(),
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_probability_label(self) -> str:
        labels = {
            RiskProbability.VERY_LOW: "非常に低い",
            RiskProbability.LOW: "低い",
            RiskProbability.MEDIUM: "中程度",
            RiskProbability.HIGH: "高い",
            RiskProbability.VERY_HIGH: "非常に高い"
        }
        return labels[self.probability]

    def _get_impact_label(self) -> str:
        labels = {
            RiskImpact.VERY_LOW: "非常に軽微",
            RiskImpact.LOW: "軽微",
            RiskImpact.MEDIUM: "中程度",
            RiskImpact.HIGH: "重大",
            RiskImpact.VERY_HIGH: "非常に重大"
        }
        return labels[self.impact]

    def _get_priority_level(self) -> str:
        if self.risk_score >= 16:
            return "最高優先"
        elif self.risk_score >= 12:
            return "高優先"
        elif self.risk_score >= 8:
            return "中優先"
        elif self.risk_score >= 4:
            return "低優先"
        else:
            return "最低優先"


class RBSAnalysis:
    """RBS分析セッション"""
    def __init__(self, project_name: str, project_type: str, context: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.project_name = project_name
        self.project_type = project_type
        self.context = context
        self.risks: List[RiskItem] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_risk(self, risk: RiskItem):
        """リスクを追加"""
        self.risks.append(risk)
        self.updated_at = datetime.now()

    def get_risks_by_category(self, category: RiskCategory) -> List[RiskItem]:
        """カテゴリ別のリスク取得"""
        return [risk for risk in self.risks if risk.category == category]

    def get_high_priority_risks(self) -> List[RiskItem]:
        """高優先度リスクの取得"""
        return [risk for risk in self.risks if risk.risk_score >= 12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "context": self.context,
            "risk_count": len(self.risks),
            "high_priority_count": len(self.get_high_priority_risks()),
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class RBS:
    """PMBOK Risk Breakdown Structure implementation"""

    def __init__(self):
        self.analyses: Dict[str, RBSAnalysis] = {}
        self.risk_templates = self._initialize_risk_templates()

    def _initialize_risk_templates(self) -> Dict[RiskCategory, Dict[str, List[str]]]:
        """リスクテンプレートの初期化"""
        return {
            RiskCategory.TECHNICAL: {
                "技術要件": [
                    "新技術の学習コスト",
                    "技術仕様の変更",
                    "技術的実現可能性の不確実性"
                ],
                "システム統合": [
                    "既存システムとの互換性",
                    "データ移行の複雑さ",
                    "システム性能の問題"
                ],
                "品質保証": [
                    "テスト不備による品質問題",
                    "セキュリティ脆弱性",
                    "スケーラビリティの問題"
                ]
            },
            RiskCategory.EXTERNAL: {
                "市場・競合": [
                    "市場環境の変化",
                    "競合他社の動向",
                    "顧客ニーズの変化"
                ],
                "規制・法律": [
                    "規制要件の変更",
                    "法律改正の影響",
                    "コンプライアンス違反"
                ],
                "外部依存": [
                    "外部ベンダーの遅延",
                    "サードパーティライブラリの問題",
                    "外部サービスの停止"
                ]
            },
            RiskCategory.ORGANIZATIONAL: {
                "人的リソース": [
                    "キーパーソンの離職",
                    "スキル不足",
                    "チーム間のコミュニケーション不足"
                ],
                "組織体制": [
                    "組織変更の影響",
                    "権限・責任の不明確",
                    "意思決定の遅延"
                ],
                "企業文化": [
                    "変革への抵抗",
                    "優先度の競合",
                    "リソース配分の問題"
                ]
            },
            RiskCategory.PROJECT_MANAGEMENT: {
                "スケジュール": [
                    "工期の遅延",
                    "依存関係の複雑化",
                    "マイルストーンの未達成"
                ],
                "予算・コスト": [
                    "予算超過",
                    "隠れたコストの発生",
                    "為替変動の影響"
                ],
                "スコープ・要件": [
                    "要件の変更・追加",
                    "スコープクリープ",
                    "ステークホルダー要求の変化"
                ]
            }
        }

    def create_structure(self, project_name: str, project_type: str, context: str = "") -> Dict[str, Any]:
        """RBS構造を作成"""
        analysis = RBSAnalysis(project_name, project_type, context)
        self.analyses[analysis.id] = analysis

        structure = {
            "analysis_id": analysis.id,
            "project_name": project_name,
            "project_type": project_type,
            "rbs_structure": self._build_structure_tree(),
            "recommended_focus": self._get_project_type_recommendations(project_type),
            "created_at": analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        return {
            "success": True,
            "message": f"📋 プロジェクト '{project_name}' のRBS構造を作成しました",
            "data": structure
        }

    def _build_structure_tree(self) -> Dict[str, Any]:
        """RBS構造ツリーの構築"""
        structure = {}
        for category in RiskCategory:
            subcategories = {}
            for subcat, risks in self.risk_templates[category].items():
                subcategories[subcat] = {
                    "risk_examples": risks,
                    "count": len(risks)
                }
            structure[category.value] = {
                "subcategories": subcategories,
                "total_examples": sum(len(risks) for risks in self.risk_templates[category].values())
            }
        return structure

    def _get_project_type_recommendations(self, project_type: str) -> List[str]:
        """プロジェクトタイプ別の推奨フォーカス領域"""
        recommendations = {
            "IT・システム開発": [
                "技術的リスクを最優先で検討",
                "システム統合とデータ移行に注意",
                "セキュリティ要件の早期確認"
            ],
            "インフラ・建設": [
                "外部環境要因（天候、規制）を重視",
                "安全管理と品質保証を最優先",
                "資材調達とサプライチェーン管理"
            ],
            "新商品開発": [
                "市場・競合リスクを重点分析",
                "技術的実現可能性の検証",
                "知的財産と特許の考慮"
            ],
            "組織変革": [
                "組織リスクを最重要視",
                "変革への抵抗とチェンジマネジメント",
                "コミュニケーション戦略の確立"
            ]
        }
        return recommendations.get(project_type, [
            "全カテゴリをバランスよく検討",
            "プロジェクト固有のリスクを特定",
            "ステークホルダー分析の実施"
        ])

    def identify_risks(self, analysis_id: str, category: str, subcategory: str,
                      custom_risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """カテゴリ別リスク識別"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        analysis = self.analyses[analysis_id]
        
        # カテゴリの検証
        try:
            risk_category = RiskCategory(category)
        except ValueError:
            return {
                "success": False,
                "message": f"❌ 無効なリスクカテゴリ: {category}"
            }

        # リスクの追加
        added_risks = []
        for risk_data in custom_risks:
            try:
                risk = RiskItem(
                    name=risk_data["name"],
                    description=risk_data["description"],
                    category=risk_category,
                    subcategory=subcategory,
                    probability=RiskProbability(risk_data.get("probability", 3)),
                    impact=RiskImpact(risk_data.get("impact", 3))
                )
                analysis.add_risk(risk)
                added_risks.append(risk.to_dict())
            except Exception as e:
                return {
                    "success": False,
                    "message": f"❌ リスク追加エラー: {str(e)}"
                }

        return {
            "success": True,
            "message": f"✅ {len(added_risks)}件のリスクを '{subcategory}' に追加しました",
            "data": {
                "analysis_id": analysis_id,
                "category": category,
                "subcategory": subcategory,
                "added_risks": added_risks,
                "total_risks": len(analysis.risks)
            }
        }

    def evaluate_risks(self, analysis_id: str) -> Dict[str, Any]:
        """リスク評価マトリックスの生成"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        analysis = self.analyses[analysis_id]
        
        if not analysis.risks:
            return {
                "success": False,
                "message": "❌ 評価対象のリスクがありません"
            }

        # リスクマトリックスの作成
        matrix = self._create_risk_matrix(analysis.risks)
        
        # 統計情報の計算
        stats = self._calculate_risk_statistics(analysis.risks)
        
        # 優先度別のグループ化
        priority_groups = self._group_risks_by_priority(analysis.risks)

        return {
            "success": True,
            "message": f"📊 {len(analysis.risks)}件のリスクを評価しました",
            "data": {
                "analysis_id": analysis_id,
                "project_name": analysis.project_name,
                "risk_matrix": matrix,
                "statistics": stats,
                "priority_groups": priority_groups,
                "recommendations": self._generate_risk_recommendations(analysis.risks)
            }
        }

    def _create_risk_matrix(self, risks: List[RiskItem]) -> Dict[str, Any]:
        """リスクマトリックスの作成"""
        matrix = {}
        for prob in range(1, 6):
            matrix[str(prob)] = {}
            for impact in range(1, 6):
                matrix[str(prob)][str(impact)] = []

        for risk in risks:
            prob_key = str(risk.probability.value)
            impact_key = str(risk.impact.value)
            matrix[prob_key][impact_key].append({
                "id": risk.id,
                "name": risk.name,
                "score": risk.risk_score
            })

        return matrix

    def _calculate_risk_statistics(self, risks: List[RiskItem]) -> Dict[str, Any]:
        """リスク統計の計算"""
        if not risks:
            return {}

        scores = [risk.risk_score for risk in risks]
        categories = {}
        for risk in risks:
            cat = risk.category.value
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        return {
            "total_risks": len(risks),
            "average_score": round(sum(scores) / len(scores), 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "high_priority_count": len([r for r in risks if r.risk_score >= 12]),
            "category_distribution": categories
        }

    def _group_risks_by_priority(self, risks: List[RiskItem]) -> Dict[str, List[Dict[str, Any]]]:
        """優先度別リスクグループ化"""
        groups = {
            "最高優先": [],
            "高優先": [],
            "中優先": [],
            "低優先": [],
            "最低優先": []
        }

        for risk in risks:
            priority = risk._get_priority_level()
            groups[priority].append(risk.to_dict())

        # 各グループを影響度とスコアでソート
        for priority in groups:
            groups[priority].sort(key=lambda x: (-x["risk_score"], -x["impact"]["value"]))

        return groups

    def _generate_risk_recommendations(self, risks: List[RiskItem]) -> List[str]:
        """リスク対策推奨事項の生成"""
        recommendations = []
        
        high_risks = [r for r in risks if r.risk_score >= 12]
        if high_risks:
            recommendations.append(f"🚨 {len(high_risks)}件の高優先度リスクに対する即座の対策が必要")
            
        category_counts = {}
        for risk in risks:
            cat = risk.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        max_category = max(category_counts, key=category_counts.get) if category_counts else None
        if max_category:
            recommendations.append(f"📊 {max_category}に集中したリスク対策を検討")

        if len(risks) > 10:
            recommendations.append("📋 リスク数が多いため、優先度に基づく段階的な対策を推奨")
        
        recommendations.extend([
            "🔍 定期的なリスク評価の実施",
            "📝 リスク対策計画の文書化",
            "👥 ステークホルダーとのリスク情報共有"
        ])
        
        return recommendations

    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """RBS分析の取得"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        analysis = self.analyses[analysis_id]
        return {
            "success": True,
            "message": f"📋 RBS分析 '{analysis.project_name}' の詳細",
            "data": {
                **analysis.to_dict(),
                "risks": [risk.to_dict() for risk in analysis.risks],
                "risk_summary": self._calculate_risk_statistics(analysis.risks) if analysis.risks else {}
            }
        }

    def list_analyses(self) -> Dict[str, Any]:
        """すべてのRBS分析の一覧取得"""
        if not self.analyses:
            return {
                "success": True,
                "message": "📋 RBS分析はまだ作成されていません",
                "data": {"analyses": []}
            }

        # 分析オブジェクトを作成日時でソート（新しい順）
        sorted_analyses = sorted(self.analyses.values(), key=lambda x: x.created_at, reverse=True)
        analyses_list = [analysis.to_dict() for analysis in sorted_analyses]

        return {
            "success": True,
            "message": f"📋 {len(analyses_list)}件のRBS分析",
            "data": {
                "analyses": analyses_list,
                "total_count": len(analyses_list)
            }
        }