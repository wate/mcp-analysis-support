"""m-SHELL Model implementation for Human Factors Analysis."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class MShellElement(Enum):
    """m-SHELLモデルの6要素"""
    MACHINE = "Machine"
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    ENVIRONMENT = "Environment"
    LIVEWARE_CENTRAL = "Liveware-Central"
    LIVEWARE_OTHER = "Liveware-Other"


class AnalysisSeverity(Enum):
    """分析項目の重要度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ElementAnalysis:
    """要素別分析結果"""
    def __init__(self, element: MShellElement, findings: List[str], 
                 severity: AnalysisSeverity = AnalysisSeverity.MEDIUM,
                 recommendations: List[str] = None):
        self.id = str(uuid.uuid4())[:8]
        self.element = element
        self.findings = findings or []
        self.severity = severity
        self.recommendations = recommendations or []
        self.analyzed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "element": self.element.value,
            "element_jp": self._get_element_japanese(),
            "findings": self.findings,
            "severity": {
                "value": self.severity.value,
                "label": self._get_severity_label()
            },
            "recommendations": self.recommendations,
            "analyzed_at": self.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_element_japanese(self) -> str:
        jp_names = {
            MShellElement.MACHINE: "機械・設備",
            MShellElement.SOFTWARE: "ソフトウェア・手順",
            MShellElement.HARDWARE: "ハードウェア・物理環境",
            MShellElement.ENVIRONMENT: "環境・条件",
            MShellElement.LIVEWARE_CENTRAL: "中心人物・主要オペレーター",
            MShellElement.LIVEWARE_OTHER: "他者・チーム・組織"
        }
        return jp_names[self.element]

    def _get_severity_label(self) -> str:
        labels = {
            AnalysisSeverity.LOW: "軽微",
            AnalysisSeverity.MEDIUM: "中程度",
            AnalysisSeverity.HIGH: "重要",
            AnalysisSeverity.CRITICAL: "致命的"
        }
        return labels[self.severity]


class InterfaceAnalysis:
    """要素間インターフェース分析"""
    def __init__(self, element1: MShellElement, element2: MShellElement,
                 interface_issues: List[str], interaction_quality: int = 5):
        self.id = str(uuid.uuid4())[:8]
        self.element1 = element1
        self.element2 = element2
        self.interface_issues = interface_issues or []
        self.interaction_quality = max(1, min(10, interaction_quality))  # 1-10スケール
        self.analyzed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "interface": f"{self.element1.value} ↔ {self.element2.value}",
            "interface_jp": f"{self._get_jp_name(self.element1)} ↔ {self._get_jp_name(self.element2)}",
            "issues": self.interface_issues,
            "quality_score": self.interaction_quality,
            "quality_level": self._get_quality_level(),
            "analyzed_at": self.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_jp_name(self, element: MShellElement) -> str:
        jp_names = {
            MShellElement.MACHINE: "機械",
            MShellElement.SOFTWARE: "SW",
            MShellElement.HARDWARE: "HW",
            MShellElement.ENVIRONMENT: "環境",
            MShellElement.LIVEWARE_CENTRAL: "中心人物",
            MShellElement.LIVEWARE_OTHER: "他者"
        }
        return jp_names[element]

    def _get_quality_level(self) -> str:
        if self.interaction_quality >= 8:
            return "良好"
        elif self.interaction_quality >= 6:
            return "普通"
        elif self.interaction_quality >= 4:
            return "要改善"
        else:
            return "問題あり"


class MShellAnalysis:
    """m-SHELL分析セッション"""
    def __init__(self, system_name: str, analysis_purpose: str, context: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.system_name = system_name
        self.analysis_purpose = analysis_purpose
        self.context = context
        self.element_analyses: Dict[str, ElementAnalysis] = {}
        self.interface_analyses: List[InterfaceAnalysis] = []
        self.overall_assessment: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_element_analysis(self, analysis: ElementAnalysis):
        """要素分析を追加"""
        self.element_analyses[analysis.element.value] = analysis
        self.updated_at = datetime.now()

    def add_interface_analysis(self, analysis: InterfaceAnalysis):
        """インターフェース分析を追加"""
        self.interface_analyses.append(analysis)
        self.updated_at = datetime.now()

    def get_critical_issues(self) -> List[ElementAnalysis]:
        """致命的問題の取得"""
        return [analysis for analysis in self.element_analyses.values() 
                if analysis.severity == AnalysisSeverity.CRITICAL]

    def get_interface_problems(self) -> List[InterfaceAnalysis]:
        """インターフェース問題の取得"""
        return [analysis for analysis in self.interface_analyses 
                if analysis.interaction_quality < 6]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "system_name": self.system_name,
            "analysis_purpose": self.analysis_purpose,
            "context": self.context,
            "element_count": len(self.element_analyses),
            "interface_count": len(self.interface_analyses),
            "critical_issues": len(self.get_critical_issues()),
            "interface_problems": len(self.get_interface_problems()),
            "overall_assessment": self.overall_assessment,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class MShell:
    """m-SHELL Model implementation for Human Factors Analysis"""

    def __init__(self):
        self.analyses: Dict[str, MShellAnalysis] = {}
        self.analysis_templates = self._initialize_analysis_templates()
        self.interface_matrix = self._initialize_interface_matrix()

    def _initialize_analysis_templates(self) -> Dict[MShellElement, Dict[str, List[str]]]:
        """分析テンプレートの初期化"""
        return {
            MShellElement.MACHINE: {
                "設計・機能": [
                    "機器の設計は使用目的に適しているか",
                    "必要な機能が適切に実装されているか",
                    "異常時の動作は予測可能か"
                ],
                "信頼性・保守性": [
                    "故障率は許容範囲内か",
                    "保守・点検は容易に実行できるか",
                    "部品交換は迅速に行えるか"
                ],
                "操作性": [
                    "操作は直感的で分かりやすいか",
                    "エラーを防ぐ仕組みがあるか",
                    "緊急時の操作は容易か"
                ]
            },
            MShellElement.SOFTWARE: {
                "手順・プロセス": [
                    "作業手順は明確に定義されているか",
                    "例外処理の手順は整備されているか",
                    "手順書は最新の状態に保たれているか"
                ],
                "プログラム・システム": [
                    "ソフトウェアは仕様通りに動作するか",
                    "ユーザーインターフェースは使いやすいか",
                    "データの整合性は保たれているか"
                ],
                "規則・基準": [
                    "関連法規・規制に準拠しているか",
                    "社内規定は適切に整備されているか",
                    "業界標準に合致しているか"
                ]
            },
            MShellElement.HARDWARE: {
                "物理的環境": [
                    "作業スペースは十分確保されているか",
                    "照明・温度は適切に管理されているか",
                    "騒音レベルは許容範囲内か"
                ],
                "インターフェース": [
                    "操作パネルは見やすく配置されているか",
                    "表示装置は判読しやすいか",
                    "操作系統は使いやすい配置か"
                ],
                "安全設備": [
                    "安全装置は適切に配置されているか",
                    "緊急停止装置にアクセスしやすいか",
                    "防護設備は十分に機能するか"
                ]
            },
            MShellElement.ENVIRONMENT: {
                "作業環境": [
                    "温度・湿度は快適な範囲か",
                    "換気は十分に行われているか",
                    "振動・衝撃の影響はないか"
                ],
                "組織環境": [
                    "組織風土は安全を重視しているか",
                    "報告・相談しやすい雰囲気か",
                    "継続的改善の仕組みがあるか"
                ],
                "外部環境": [
                    "気象条件の影響を考慮しているか",
                    "周辺施設からの影響はないか",
                    "法的・社会的制約を理解しているか"
                ]
            },
            MShellElement.LIVEWARE_CENTRAL: {
                "知識・技能": [
                    "必要な知識・技能を習得しているか",
                    "経験は業務に十分活用されているか",
                    "継続的な学習・向上に取り組んでいるか"
                ],
                "身体的・心理的状態": [
                    "健康状態は良好か",
                    "疲労・ストレス管理はできているか",
                    "モチベーションは維持されているか"
                ],
                "判断・意思決定": [
                    "状況判断は適切に行えるか",
                    "優先順位の設定は妥当か",
                    "リスクの認識・評価は適切か"
                ]
            },
            MShellElement.LIVEWARE_OTHER: {
                "チーム・協調": [
                    "チーム内のコミュニケーションは円滑か",
                    "役割分担は明確に定義されているか",
                    "相互支援の仕組みがあるか"
                ],
                "組織・管理": [
                    "管理体制は適切に構築されているか",
                    "情報共有は効果的に行われているか",
                    "意思決定プロセスは迅速か"
                ],
                "外部関係者": [
                    "関係機関との連携は良好か",
                    "顧客・利用者との関係は適切か",
                    "協力会社との調整は円滑か"
                ]
            }
        }

    def _initialize_interface_matrix(self) -> Dict[Tuple[MShellElement, MShellElement], List[str]]:
        """要素間インターフェースの分析ポイント初期化"""
        matrix = {}
        elements = list(MShellElement)
        
        for i, elem1 in enumerate(elements):
            for j, elem2 in enumerate(elements):
                if i < j:  # 重複を避ける
                    key = (elem1, elem2)
                    matrix[key] = self._get_interface_checkpoints(elem1, elem2)
        
        return matrix

    def _get_interface_checkpoints(self, elem1: MShellElement, elem2: MShellElement) -> List[str]:
        """要素間インターフェースのチェックポイント取得"""
        interface_patterns = {
            (MShellElement.MACHINE, MShellElement.SOFTWARE): [
                "機械制御ソフトウェアは適切に動作するか",
                "機械からのフィードバック情報は正確か",
                "ソフトウェア更新時の機械への影響は検証されているか"
            ],
            (MShellElement.MACHINE, MShellElement.HARDWARE): [
                "機械と操作盤の配置関係は適切か",
                "表示・警告装置は機械の状態を正確に反映するか",
                "物理的な接続・配線に問題はないか"
            ],
            (MShellElement.MACHINE, MShellElement.ENVIRONMENT): [
                "環境条件は機械の性能に影響しないか",
                "機械からの発熱・騒音・振動は環境に悪影響を与えないか",
                "清掃・保守作業用のスペースは確保されているか"
            ],
            (MShellElement.MACHINE, MShellElement.LIVEWARE_CENTRAL): [
                "オペレーターは機械の操作方法を熟知しているか",
                "機械の異常を適切に判断できるか",
                "緊急時の対応手順は身についているか"
            ],
            (MShellElement.MACHINE, MShellElement.LIVEWARE_OTHER): [
                "保守担当者との連携は円滑か",
                "機械情報の共有は適切に行われているか",
                "交代時の申し送り事項は明確か"
            ],
            (MShellElement.SOFTWARE, MShellElement.HARDWARE): [
                "ソフトウェアとハードウェアの互換性に問題はないか",
                "画面表示と物理操作の対応関係は明確か",
                "入力デバイスの応答性は適切か"
            ],
            (MShellElement.SOFTWARE, MShellElement.ENVIRONMENT): [
                "環境変化がソフトウェア動作に影響しないか",
                "ネットワーク環境は安定しているか",
                "データバックアップ環境は整備されているか"
            ],
            (MShellElement.SOFTWARE, MShellElement.LIVEWARE_CENTRAL): [
                "ユーザーインターフェースは直感的か",
                "エラーメッセージは理解しやすいか",
                "操作手順は論理的に設計されているか"
            ],
            (MShellElement.SOFTWARE, MShellElement.LIVEWARE_OTHER): [
                "複数ユーザー間での情報共有は適切か",
                "アクセス権限の管理は適正か",
                "協調作業の支援機能は充実しているか"
            ],
            (MShellElement.HARDWARE, MShellElement.ENVIRONMENT): [
                "ハードウェアは環境条件に対して十分な耐性があるか",
                "設置場所の物理的制約は考慮されているか",
                "メンテナンス用のアクセス経路は確保されているか"
            ],
            (MShellElement.HARDWARE, MShellElement.LIVEWARE_CENTRAL): [
                "操作性・視認性は十分考慮されているか",
                "人間工学的な配慮がなされているか",
                "長時間使用時の疲労軽減策はあるか"
            ],
            (MShellElement.HARDWARE, MShellElement.LIVEWARE_OTHER): [
                "共用設備の使用ルールは明確か",
                "保守・点検作業の安全性は確保されているか",
                "機器の設定変更権限は適切に管理されているか"
            ],
            (MShellElement.ENVIRONMENT, MShellElement.LIVEWARE_CENTRAL): [
                "作業環境は集中力を維持できるレベルか",
                "健康・安全への配慮は十分か",
                "ストレス要因の軽減策はあるか"
            ],
            (MShellElement.ENVIRONMENT, MShellElement.LIVEWARE_OTHER): [
                "コミュニケーションを促進する環境か",
                "チームワークを支援する物理的配置か",
                "組織風土は協力的か"
            ],
            (MShellElement.LIVEWARE_CENTRAL, MShellElement.LIVEWARE_OTHER): [
                "役割分担は明確で適切か",
                "情報共有・報告の仕組みは機能しているか",
                "相互支援・バックアップ体制は整っているか"
            ]
        }
        
        return interface_patterns.get((elem1, elem2), interface_patterns.get((elem2, elem1), [
            f"{elem1.value}と{elem2.value}の相互作用を分析",
            "インターフェース品質の評価",
            "改善点の特定"
        ]))

    def create_analysis(self, system_name: str, analysis_purpose: str, context: str = "") -> Dict[str, Any]:
        """m-SHELL分析を開始"""
        analysis = MShellAnalysis(system_name, analysis_purpose, context)
        self.analyses[analysis.id] = analysis

        return {
            "success": True,
            "message": f"🔍 システム '{system_name}' のm-SHELL分析を開始しました",
            "data": {
                "analysis_id": analysis.id,
                "system_name": system_name,
                "analysis_purpose": analysis_purpose,
                "available_elements": [elem.value for elem in MShellElement],
                "element_descriptions": self._get_element_descriptions(),
                "created_at": analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def _get_element_descriptions(self) -> Dict[str, str]:
        """要素の説明を取得"""
        return {
            "Machine": "機械・設備・装置（物理的なシステムの中核）",
            "Software": "ソフトウェア・手順・規則（システムの論理的側面）",
            "Hardware": "ハードウェア・物理環境・インターフェース（システムの物理的境界）",
            "Environment": "環境・条件・文脈（システムを取り巻く状況）",
            "Liveware-Central": "中心人物・主要オペレーター（システムの中核となる人）",
            "Liveware-Other": "他者・チーム・組織（中心人物と関わる人々）"
        }

    def analyze_element(self, analysis_id: str, element: str, findings: List[str],
                       severity: int = 2, recommendations: List[str] = None) -> Dict[str, Any]:
        """特定要素の分析実行"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        try:
            element_enum = MShellElement(element)
        except ValueError:
            return {
                "success": False,
                "message": f"❌ 無効な要素: {element}"
            }

        try:
            severity_enum = AnalysisSeverity(severity)
        except ValueError:
            return {
                "success": False,
                "message": f"❌ 無効な重要度: {severity} (1-4の範囲で指定)"
            }

        analysis = self.analyses[analysis_id]
        element_analysis = ElementAnalysis(element_enum, findings, severity_enum, recommendations or [])
        analysis.add_element_analysis(element_analysis)

        return {
            "success": True,
            "message": f"✅ {element_analysis._get_element_japanese()}の分析を記録しました",
            "data": {
                "analysis_id": analysis_id,
                "element_analysis": element_analysis.to_dict(),
                "available_checkpoints": self.analysis_templates.get(element_enum, {}),
                "progress": f"{len(analysis.element_analyses)}/6要素"
            }
        }

    def analyze_interface(self, analysis_id: str, element1: str, element2: str,
                         issues: List[str], quality_score: int = 5) -> Dict[str, Any]:
        """要素間インターフェース分析"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        try:
            elem1 = MShellElement(element1)
            elem2 = MShellElement(element2)
        except ValueError:
            return {
                "success": False,
                "message": f"❌ 無効な要素: {element1} または {element2}"
            }

        if elem1 == elem2:
            return {
                "success": False,
                "message": "❌ 同じ要素同士のインターフェース分析はできません"
            }

        analysis = self.analyses[analysis_id]
        interface_analysis = InterfaceAnalysis(elem1, elem2, issues, quality_score)
        analysis.add_interface_analysis(interface_analysis)

        # 該当インターフェースのチェックポイント取得
        checkpoints = self.interface_matrix.get((elem1, elem2)) or \
                     self.interface_matrix.get((elem2, elem1)) or []

        return {
            "success": True,
            "message": f"✅ {interface_analysis.to_dict()['interface_jp']}のインターフェース分析を記録しました",
            "data": {
                "analysis_id": analysis_id,
                "interface_analysis": interface_analysis.to_dict(),
                "suggested_checkpoints": checkpoints,
                "total_interfaces": len(analysis.interface_analyses)
            }
        }

    def evaluate_system(self, analysis_id: str) -> Dict[str, Any]:
        """システム全体評価"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        analysis = self.analyses[analysis_id]

        if not analysis.element_analyses and not analysis.interface_analyses:
            return {
                "success": False,
                "message": "❌ 評価対象の分析データがありません"
            }

        # 全体評価の生成
        evaluation = self._generate_system_evaluation(analysis)
        analysis.overall_assessment = evaluation["summary"]

        return {
            "success": True,
            "message": f"📊 システム '{analysis.system_name}' の全体評価を完了しました",
            "data": {
                "analysis_id": analysis_id,
                "system_name": analysis.system_name,
                "evaluation": evaluation,
                "critical_issues": [issue.to_dict() for issue in analysis.get_critical_issues()],
                "interface_problems": [prob.to_dict() for prob in analysis.get_interface_problems()],
                "recommendations": self._generate_system_recommendations(analysis)
            }
        }

    def _generate_system_evaluation(self, analysis: MShellAnalysis) -> Dict[str, Any]:
        """システム全体評価の生成"""
        element_scores = {}
        total_severity = 0
        element_count = len(analysis.element_analyses)

        for elem_analysis in analysis.element_analyses.values():
            severity_score = 5 - elem_analysis.severity.value  # 逆転（高い方が良い）
            element_scores[elem_analysis.element.value] = severity_score
            total_severity += severity_score

        avg_element_score = total_severity / element_count if element_count > 0 else 0

        # インターフェース評価
        interface_scores = [ia.interaction_quality for ia in analysis.interface_analyses]
        avg_interface_score = sum(interface_scores) / len(interface_scores) if interface_scores else 0

        # 総合スコア
        overall_score = (avg_element_score * 0.6 + avg_interface_score * 0.4) if interface_scores else avg_element_score

        return {
            "overall_score": round(overall_score, 2),
            "overall_level": self._get_overall_level(overall_score),
            "element_scores": element_scores,
            "average_element_score": round(avg_element_score, 2),
            "average_interface_score": round(avg_interface_score, 2),
            "analysis_completeness": f"{element_count}/6要素分析済み",
            "interface_completeness": f"{len(analysis.interface_analyses)}件のインターフェース分析済み",
            "summary": self._generate_evaluation_summary(analysis, overall_score)
        }

    def _get_overall_level(self, score: float) -> str:
        """総合評価レベルの判定"""
        if score >= 8:
            return "優秀"
        elif score >= 6:
            return "良好" 
        elif score >= 4:
            return "普通"
        elif score >= 2:
            return "要改善"
        else:
            return "危険"

    def _generate_evaluation_summary(self, analysis: MShellAnalysis, score: float) -> str:
        """評価サマリーの生成"""
        level = self._get_overall_level(score)
        critical_count = len(analysis.get_critical_issues())
        problem_interfaces = len(analysis.get_interface_problems())

        summary = f"システム全体の評価は「{level}」レベルです。"
        
        if critical_count > 0:
            summary += f" {critical_count}件の致命的問題が特定されました。"
        
        if problem_interfaces > 0:
            summary += f" {problem_interfaces}件のインターフェースに改善の余地があります。"
            
        if score >= 6:
            summary += " 基本的なシステム品質は確保されています。"
        else:
            summary += " システム改善の優先的な取り組みが必要です。"

        return summary

    def _generate_system_recommendations(self, analysis: MShellAnalysis) -> List[str]:
        """システム推奨事項の生成"""
        recommendations = []
        
        critical_issues = analysis.get_critical_issues()
        if critical_issues:
            recommendations.append(f"🚨 {len(critical_issues)}件の致命的問題への即座の対応が最優先")
            
        problem_interfaces = analysis.get_interface_problems()
        if problem_interfaces:
            recommendations.append(f"🔗 {len(problem_interfaces)}件のインターフェース改善が必要")

        # 要素別の分析状況確認
        analyzed_elements = set(analysis.element_analyses.keys())
        all_elements = set(elem.value for elem in MShellElement)
        missing_elements = all_elements - analyzed_elements
        
        if missing_elements:
            recommendations.append(f"📋 未分析要素（{', '.join(missing_elements)}）の分析を推奨")

        # 基本的な推奨事項
        recommendations.extend([
            "🔄 定期的なm-SHELL分析の実施",
            "📊 要素間の相互作用に注目した継続監視",
            "👥 関係者全員での結果共有と改善取り組み",
            "📝 分析結果に基づく改善計画の策定"
        ])

        return recommendations

    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """m-SHELL分析の取得"""
        if analysis_id not in self.analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }

        analysis = self.analyses[analysis_id]
        element_analyses = [elem.to_dict() for elem in analysis.element_analyses.values()]
        interface_analyses = [intf.to_dict() for intf in analysis.interface_analyses]

        return {
            "success": True,
            "message": f"🔍 m-SHELL分析 '{analysis.system_name}' の詳細",
            "data": {
                **analysis.to_dict(),
                "element_analyses": element_analyses,
                "interface_analyses": interface_analyses,
                "analysis_summary": self._generate_analysis_summary(analysis)
            }
        }

    def _generate_analysis_summary(self, analysis: MShellAnalysis) -> Dict[str, Any]:
        """分析サマリーの生成"""
        return {
            "completion_rate": f"{len(analysis.element_analyses)}/6要素",
            "total_findings": sum(len(ea.findings) for ea in analysis.element_analyses.values()),
            "total_recommendations": sum(len(ea.recommendations) for ea in analysis.element_analyses.values()),
            "severity_distribution": self._calculate_severity_distribution(analysis),
            "interface_quality_avg": self._calculate_interface_average(analysis)
        }

    def _calculate_severity_distribution(self, analysis: MShellAnalysis) -> Dict[str, int]:
        """重要度分布の計算"""
        distribution = {"軽微": 0, "中程度": 0, "重要": 0, "致命的": 0}
        for elem_analysis in analysis.element_analyses.values():
            label = elem_analysis._get_severity_label()
            distribution[label] += 1
        return distribution

    def _calculate_interface_average(self, analysis: MShellAnalysis) -> Optional[float]:
        """インターフェース品質の平均計算"""
        if not analysis.interface_analyses:
            return None
        scores = [ia.interaction_quality for ia in analysis.interface_analyses]
        return round(sum(scores) / len(scores), 2)

    def list_analyses(self) -> Dict[str, Any]:
        """すべてのm-SHELL分析の一覧取得"""
        if not self.analyses:
            return {
                "success": True,
                "message": "🔍 m-SHELL分析はまだ作成されていません",
                "data": {"analyses": []}
            }

        # 分析を作成日時でソート（新しい順）
        sorted_analyses = sorted(self.analyses.values(), key=lambda x: x.created_at, reverse=True)
        analyses_list = [analysis.to_dict() for analysis in sorted_analyses]

        return {
            "success": True,
            "message": f"🔍 {len(analyses_list)}件のm-SHELL分析",
            "data": {
                "analyses": analyses_list,
                "total_count": len(analyses_list)
            }
        }