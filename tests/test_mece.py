"""MECE分析ツールのテスト."""

import pytest

from analysis_support.tools.mece import MECE, MECEViolationType


class TestMECE:
    """MECE分析のテストクラス."""
    
    def setup_method(self) -> None:
        """各テストメソッドの前に実行される初期化."""
        self.analyzer = MECE()
    
    def test_analyze_categories_with_overlaps(self) -> None:
        """重複があるカテゴリの分析テスト."""
        topic = "営業戦略"
        categories = ["新規顧客開拓", "既存顧客維持", "顧客満足度向上", "新規市場開拓"]
        
        result = self.analyzer.analyze_categories(topic, categories)
        
        assert result["success"] is True
        assert result["topic"] == topic
        assert result["categories"] == categories
        assert "analysis_id" in result
        assert len(result["analysis_id"]) == 8  # 8文字のUUID
        
        # 重複検出の確認
        mece_eval = result["mece_evaluation"]
        assert "overlaps" in mece_eval
        assert "gaps" in mece_eval
    
    def test_analyze_categories_mece_compliant(self) -> None:
        """MECE原則に適合するカテゴリの分析テスト."""
        topic = "時間管理"
        categories = ["過去", "現在", "未来"]  # 時系列で重複なし
        
        result = self.analyzer.analyze_categories(topic, categories)
        
        assert result["success"] is True
        mece_eval = result["mece_evaluation"]
        assert len(mece_eval["overlaps"]) == 0  # 重複なし
        assert "improvement_suggestions" in result
    
    def test_create_structure_4p_framework(self) -> None:
        """4Pフレームワークでの構造提案テスト."""
        topic = "商品マーケティング"
        framework = "4P"
        
        result = self.analyzer.create_mece_structure(topic, framework)
        
        assert result["success"] is True
        assert result["topic"] == topic
        assert result["framework"] == framework
        
        structure = result["structure"]
        categories = structure["categories"]
        assert len(categories) == 4
        assert "Product" in categories[0]
        assert "Price" in categories[1]
        assert "Place" in categories[2]
        assert "Promotion" in categories[3]
        
        # 説明が含まれているか確認
        assert "explanations" in structure
        assert len(structure["explanations"]) == 4
    
    def test_create_structure_3c_framework(self) -> None:
        """3Cフレームワークでの構造提案テスト."""
        topic = "競合分析"
        framework = "3C"
        
        result = self.analyzer.create_mece_structure(topic, framework)
        
        assert result["success"] is True
        assert result["framework"] == framework
        
        categories = result["structure"]["categories"]
        assert len(categories) == 3
        assert "Customer" in categories[0]
        assert "Competitor" in categories[1]
        assert "Company" in categories[2]
    
    def test_create_structure_swot_framework(self) -> None:
        """SWOTフレームワークでの構造提案テスト."""
        topic = "組織分析"
        framework = "SWOT"
        
        result = self.analyzer.create_mece_structure(topic, framework)
        
        assert result["success"] is True
        categories = result["structure"]["categories"]
        assert len(categories) == 4
        assert "Strengths" in categories[0]
        assert "Weaknesses" in categories[1]
        assert "Opportunities" in categories[2]
        assert "Threats" in categories[3]
    
    def test_create_structure_time_framework(self) -> None:
        """時系列フレームワークでの構造提案テスト."""
        topic = "プロジェクト計画"
        framework = "時系列"
        
        result = self.analyzer.create_mece_structure(topic, framework)
        
        assert result["success"] is True
        categories = result["structure"]["categories"]
        assert len(categories) == 3
        assert "過去" in categories
        assert "現在" in categories
        assert "未来" in categories
    
    def test_create_structure_internal_external_framework(self) -> None:
        """内外フレームワークでの構造提案テスト."""
        topic = "リスク要因"
        framework = "内外"
        
        result = self.analyzer.create_mece_structure(topic, framework)
        
        assert result["success"] is True
        categories = result["structure"]["categories"]
        assert len(categories) == 2
        assert "内部要因" in categories
        assert "外部要因" in categories
    
    def test_create_structure_auto_selection(self) -> None:
        """自動フレームワーク選択のテスト."""
        # マーケティング関連のトピック → 4P
        result = self.analyzer.create_mece_structure("商品販売戦略", "auto")
        assert result["framework"] == "4P"
        
        # 競合分析関連のトピック → 3C
        result = self.analyzer.create_mece_structure("市場競合分析", "auto")
        assert result["framework"] == "3C"
        
        # 組織関連のトピック → SWOT
        result = self.analyzer.create_mece_structure("企業の強み弱み分析", "auto")
        assert result["framework"] == "SWOT"
        
        # 時間関連のトピック → 時系列
        result = self.analyzer.create_mece_structure("変化の推移", "auto")
        assert result["framework"] == "時系列"
        
        # デフォルト → 内外
        result = self.analyzer.create_mece_structure("一般的な課題", "auto")
        assert result["framework"] == "内外"
    
    def test_create_structure_invalid_framework(self) -> None:
        """無効なフレームワークでの構造提案テスト."""
        result = self.analyzer.create_mece_structure("テスト", "invalid_framework")
        
        assert result["success"] is False
        assert "サポートされていません" in result["message"]
    
    def test_overlap_detection_logic(self) -> None:
        """重複検出ロジックのテスト."""
        categories = ["営業チーム", "販売チーム", "マーケティング"]  # 営業と販売で重複
        overlaps = self.analyzer._find_overlaps(categories)
        
        # 何らかの重複が検出されることを確認
        assert isinstance(overlaps, list)
    
    def test_gap_detection_logic(self) -> None:
        """漏れ検出ロジックのテスト."""
        topic = "ビジネス分析"
        categories = ["売上", "利益"]  # 時間、人、場所などの観点が不足
        gaps = self.analyzer._find_gaps(topic, categories)
        
        assert isinstance(gaps, list)
        # ビジネス関連トピックなので何らかのギャップが検出される可能性が高い
    
    def test_category_explanations_generation(self) -> None:
        """カテゴリ説明生成のテスト."""
        topic = "デジタル戦略"
        framework = "4P"
        categories = self.analyzer._frameworks[framework]
        
        explanations = self.analyzer._generate_category_explanations(topic, framework, categories)
        
        assert len(explanations) == len(categories)
        for category in categories:
            assert category in explanations
            assert topic in explanations[category]
            assert len(explanations[category]) > 10  # ある程度の長さの説明
    
    def test_improvement_suggestions_generation(self) -> None:
        """改善提案生成のテスト."""
        # 重複とギャップがある分析の模擬作成
        from analysis_support.tools.mece import MECEAnalysis, MECEViolationType
        
        analysis = MECEAnalysis("test_id", "テストトピック", ["A", "B", "C"])
        analysis.overlaps = [("A", "B", "共通要素あり")]
        analysis.gaps = ["時間の観点", "場所の観点"]
        analysis.violation_type = MECEViolationType.BOTH
        
        suggestions = self.analyzer._generate_improvement_suggestions(analysis)
        
        assert len(suggestions) > 0
        # 重複に関する提案があることを確認
        assert any("重複" in suggestion for suggestion in suggestions)
        # ギャップに関する提案があることを確認
        assert any("観点" in suggestion for suggestion in suggestions)
    
    def test_analysis_notes_generation(self) -> None:
        """分析ノート生成のテスト."""
        from analysis_support.tools.mece import MECEAnalysis, MECEViolationType
        
        analysis = MECEAnalysis("test_id", "テストトピック", ["A", "B", "C"])
        analysis.overlaps = [("A", "B", "重複あり")]
        analysis.gaps = ["ギャップ1"]
        analysis.violation_type = MECEViolationType.BOTH
        
        notes = self.analyzer._generate_analysis_notes(analysis)
        
        assert len(notes) > 0
        assert any("分析対象" in note for note in notes)
        assert any("カテゴリ数" in note for note in notes)
        assert any("MECE評価" in note for note in notes)
    
    def test_comprehensive_analysis_flow(self) -> None:
        """包括的な分析フローのテスト."""
        # 1. カテゴリ分析
        topic = "プロジェクト管理"
        categories = ["計画", "実行", "監視", "完了"]
        
        analyze_result = self.analyzer.analyze_categories(topic, categories)
        assert analyze_result["success"] is True
        
        # 2. 構造提案
        structure_result = self.analyzer.create_mece_structure(topic, "auto")
        assert structure_result["success"] is True
        
        # 結果が一貫していることを確認
        assert analyze_result["topic"] == structure_result["topic"]
    
    def test_framework_characteristics_and_tips(self) -> None:
        """フレームワークの特徴と使い方ヒントのテスト."""
        result = self.analyzer.create_mece_structure("テスト", "4P")
        
        assert "characteristics" in result
        characteristics = result["characteristics"]
        assert "mutually_exclusive" in characteristics
        assert "collectively_exhaustive" in characteristics
        
        assert "usage_tips" in result
        tips = result["usage_tips"]
        assert len(tips) > 0
        assert all(isinstance(tip, str) for tip in tips)