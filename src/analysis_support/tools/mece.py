"""MECE分析ツール実装."""

from typing import Dict, List, Optional, Any, Tuple
import uuid
from datetime import datetime
from enum import Enum


class MECEViolationType(Enum):
    """MECE違反の種類."""
    OVERLAP = "重複（相互排他性違反）"
    GAP = "漏れ（網羅性違反）"
    BOTH = "重複と漏れの両方"
    NONE = "MECE原則に適合"


class MECECategory:
    """MECEカテゴリクラス."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class MECEAnalysis:
    """MECE分析結果クラス."""
    
    def __init__(
        self, 
        analysis_id: str, 
        topic: str, 
        original_categories: List[str]
    ):
        self.id = analysis_id
        self.topic = topic
        self.original_categories = original_categories
        self.mece_categories: List[MECECategory] = []
        self.violation_type = MECEViolationType.NONE
        self.overlaps: List[Tuple[str, str, str]] = []
        self.gaps: List[str] = []
        self.improvement_suggestions: List[str] = []
        self.analysis_notes: List[str] = []
        self.created_at = datetime.now()


class MECE:
    """MECE分析を管理するクラス."""
    
    def __init__(self) -> None:
        """MECE分析マネージャーを初期化."""
        self._frameworks = {
            "4P": ["Product (製品)", "Price (価格)", "Place (流通)", "Promotion (販促)"],
            "3C": ["Customer (顧客)", "Competitor (競合)", "Company (自社)"],
            "SWOT": ["Strengths (強み)", "Weaknesses (弱み)", "Opportunities (機会)", "Threats (脅威)"],
            "時系列": ["過去", "現在", "未来"],
            "内外": ["内部要因", "外部要因"]
        }
    
    def analyze_categories(self, topic: str, categories: List[str]) -> Dict[str, Any]:
        """
        カテゴリのMECE分析を実行して重複や漏れを検証する.
        
        Args:
            topic: 分析対象のトピック
            categories: 分析するカテゴリのリスト
            
        Returns:
            MECE評価、重複・漏れの検出、改善提案
        """
        analysis_id = str(uuid.uuid4())[:8]
        analysis = MECEAnalysis(analysis_id, topic, categories)
        
        # MECEカテゴリを作成
        for category in categories:
            analysis.mece_categories.append(MECECategory(category))
        
        # MECE違反をチェック
        self._check_mece_violations(analysis)
        
        # 分析結果を構築
        result = {
            "success": True,
            "message": f"📊 MECE分析を実行しました",
            "analysis_id": analysis_id,
            "topic": topic,
            "categories": categories,
            "mece_evaluation": {
                "violation_type": analysis.violation_type.value,
                "is_mece_compliant": analysis.violation_type == MECEViolationType.NONE,
                "overlaps": analysis.overlaps,
                "gaps": analysis.gaps
            },
            "improvement_suggestions": analysis.improvement_suggestions,
            "analysis_notes": analysis.analysis_notes
        }
        
        return result
    
    def create_mece_structure(self, topic: str, framework: str = "auto") -> Dict[str, Any]:
        """
        トピックに対するMECE構造を提案する.
        
        Args:
            topic: 構造を作成したいトピック
            framework: 使用するフレームワーク（auto, 4P, 3C, SWOT, 時系列, 内外）
            
        Returns:
            提案されるMECE構造、各カテゴリの説明
        """
        if framework == "auto":
            framework = self._auto_select_framework(topic)
        
        if framework not in self._frameworks:
            return {
                "success": False,
                "message": f"❌ フレームワーク '{framework}' はサポートされていません。対応フレームワーク: {', '.join(self._frameworks.keys())}"
            }
        
        structure_categories = self._frameworks[framework]
        category_explanations = self._generate_category_explanations(topic, framework, structure_categories)
        
        return {
            "success": True,
            "message": f"🎯 {framework}フレームワークによるMECE構造を提案しました",
            "topic": topic,
            "framework": framework,
            "structure": {
                "categories": structure_categories,
                "explanations": category_explanations
            },
            "characteristics": {
                "mutually_exclusive": f"各カテゴリは重複しない独立した領域です",
                "collectively_exhaustive": f"すべてのカテゴリで{topic}を網羅的にカバーします"
            },
            "usage_tips": [
                f"各カテゴリの視点から{topic}について分析してください",
                "カテゴリ間での重複がないか確認しながら整理しましょう",
                "すべてのカテゴリを検討することで漏れを防げます"
            ]
        }
    
    def _check_mece_violations(self, analysis: MECEAnalysis) -> None:
        """MECE違反をチェックする."""
        # 重複検出
        overlaps = self._find_overlaps(analysis.original_categories)
        analysis.overlaps = overlaps
        
        # 漏れ検出
        gaps = self._find_gaps(analysis.topic, analysis.original_categories)
        analysis.gaps = gaps
        
        # 違反タイプを決定
        has_overlaps = len(overlaps) > 0
        has_gaps = len(gaps) > 0
        
        if has_overlaps and has_gaps:
            analysis.violation_type = MECEViolationType.BOTH
        elif has_overlaps:
            analysis.violation_type = MECEViolationType.OVERLAP
        elif has_gaps:
            analysis.violation_type = MECEViolationType.GAP
        else:
            analysis.violation_type = MECEViolationType.NONE
        
        # 改善提案を生成
        analysis.improvement_suggestions = self._generate_improvement_suggestions(analysis)
        
        # 分析ノートを生成
        analysis.analysis_notes = self._generate_analysis_notes(analysis)
    
    def _find_overlaps(self, categories: List[str]) -> List[Tuple[str, str, str]]:
        """重複を検出する."""
        overlaps = []
        
        # 簡単な重複検出（キーワードベース）
        keywords_map: Dict[str, List[str]] = {}
        for category in categories:
            words = category.lower().split()
            for word in words:
                if len(word) > 2:  # 2文字以下は除外
                    if word not in keywords_map:
                        keywords_map[word] = []
                    keywords_map[word].append(category)
        
        # 共通キーワードを持つカテゴリペアを検出
        for word, cats in keywords_map.items():
            if len(cats) > 1:
                for i in range(len(cats)):
                    for j in range(i + 1, len(cats)):
                        overlap_reason = f"共通キーワード「{word}」を含む"
                        overlaps.append((cats[i], cats[j], overlap_reason))
        
        return overlaps
    
    def _find_gaps(self, topic: str, categories: List[str]) -> List[str]:
        """漏れを検出する."""
        gaps = []
        
        # トピックに基づく一般的な漏れを検出
        topic_lower = topic.lower()
        category_text = " ".join(categories).lower()
        
        # 一般的な分析軸の漏れをチェック
        common_aspects = {
            "時間": ["時間", "期間", "タイミング", "スケジュール"],
            "場所": ["場所", "地域", "エリア", "位置"],
            "人": ["人", "担当者", "責任者", "ユーザー", "顧客"],
            "方法": ["方法", "手順", "プロセス", "やり方"],
            "理由": ["理由", "原因", "目的", "動機"],
            "コスト": ["費用", "コスト", "予算", "価格"]
        }
        
        for aspect, keywords in common_aspects.items():
            if not any(keyword in category_text for keyword in keywords):
                if "ビジネス" in topic_lower or "業務" in topic_lower or "プロジェクト" in topic_lower:
                    gaps.append(f"{aspect}の観点")
        
        return gaps
    
    def _generate_improvement_suggestions(self, analysis: MECEAnalysis) -> List[str]:
        """改善提案を生成する."""
        suggestions = []
        
        if analysis.overlaps:
            suggestions.append("🔄 重複しているカテゴリを統合または明確に分離してください")
            for overlap in analysis.overlaps[:2]:  # 最初の2つだけ表示
                suggestions.append(f"   - 「{overlap[0]}」と「{overlap[1]}」: {overlap[2]}")
        
        if analysis.gaps:
            suggestions.append("📝 以下の観点が不足している可能性があります")
            for gap in analysis.gaps[:3]:  # 最初の3つだけ表示
                suggestions.append(f"   - {gap}")
        
        if analysis.violation_type == MECEViolationType.NONE:
            suggestions.append("✅ MECE原則に適合しています。良い分類です！")
        
        return suggestions
    
    def _generate_analysis_notes(self, analysis: MECEAnalysis) -> List[str]:
        """分析ノートを生成する."""
        notes = []
        
        notes.append(f"分析対象: {analysis.topic}")
        notes.append(f"カテゴリ数: {len(analysis.original_categories)}個")
        notes.append(f"MECE評価: {analysis.violation_type.value}")
        
        if analysis.overlaps:
            notes.append(f"重複検出: {len(analysis.overlaps)}件")
        
        if analysis.gaps:
            notes.append(f"漏れ検出: {len(analysis.gaps)}件")
        
        return notes
    
    def _auto_select_framework(self, topic: str) -> str:
        """トピックに基づいてフレームワークを自動選択する."""
        topic_lower = topic.lower()
        
        # マーケティング関連
        if any(keyword in topic_lower for keyword in ["マーケティング", "販売", "商品", "製品"]):
            return "4P"
        
        # 組織・企業分析関連（SWOTを優先）
        if any(keyword in topic_lower for keyword in ["組織", "企業", "会社", "強み", "弱み"]):
            return "SWOT"
            
        # 戦略分析関連
        if any(keyword in topic_lower for keyword in ["戦略", "競合", "分析", "市場"]):
            return "3C"
        
        # 時間関連
        if any(keyword in topic_lower for keyword in ["変化", "推移", "履歴", "将来"]):
            return "時系列"
        
        # デフォルト
        return "内外"
    
    def _generate_category_explanations(self, topic: str, framework: str, categories: List[str]) -> Dict[str, str]:
        """カテゴリごとの説明を生成する."""
        explanations = {}
        
        if framework == "4P":
            explanations = {
                "Product (製品)": f"{topic}における製品・サービスの特徴、品質、機能について",
                "Price (価格)": f"{topic}の価格戦略、コスト構造、価値提案について",
                "Place (流通)": f"{topic}の販売チャネル、流通経路、アクセス方法について",
                "Promotion (販促)": f"{topic}の広告、宣伝、コミュニケーション戦略について"
            }
        elif framework == "3C":
            explanations = {
                "Customer (顧客)": f"{topic}における顧客ニーズ、顧客行動、市場環境について",
                "Competitor (競合)": f"{topic}の競合他社の動向、競合優位性、市場シェアについて",
                "Company (自社)": f"{topic}における自社の強み、リソース、能力について"
            }
        elif framework == "SWOT":
            explanations = {
                "Strengths (強み)": f"{topic}における内部の強み、優位性、競争力について",
                "Weaknesses (弱み)": f"{topic}における内部の弱み、課題、改善点について",
                "Opportunities (機会)": f"{topic}における外部の機会、チャンス、可能性について",
                "Threats (脅威)": f"{topic}における外部の脅威、リスク、阻害要因について"
            }
        elif framework == "時系列":
            explanations = {
                "過去": f"{topic}の過去の状況、経緯、学習できる点について",
                "現在": f"{topic}の現在の状況、現状の課題と機会について",
                "未来": f"{topic}の将来の展望、予測、計画について"
            }
        elif framework == "内外":
            explanations = {
                "内部要因": f"{topic}における内部でコントロール可能な要素について",
                "外部要因": f"{topic}における外部の環境や制約条件について"
            }
        
        return explanations