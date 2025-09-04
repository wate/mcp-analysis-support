"""Tests for PMBOK RBS (Risk Breakdown Structure)."""

import pytest
from src.analysis_support.tools.rbs import RBS, RiskCategory, RiskProbability, RiskImpact, RiskItem, RBSAnalysis


class TestRBS:
    """RBSツールのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.rbs = RBS()

    def test_create_structure_basic(self):
        """基本的なRBS構造作成のテスト"""
        result = self.rbs.create_structure("Webサイトリニューアル", "IT・システム開発")
        
        assert result["success"] is True
        assert "📋" in result["message"]
        assert "data" in result
        assert "analysis_id" in result["data"]
        assert result["data"]["project_name"] == "Webサイトリニューアル"
        assert result["data"]["project_type"] == "IT・システム開発"
        assert "rbs_structure" in result["data"]
        assert "recommended_focus" in result["data"]

    def test_create_structure_with_context(self):
        """コンテキスト付きRBS構造作成のテスト"""
        result = self.rbs.create_structure(
            "新店舗建設", 
            "インフラ・建設", 
            "都市部の商業地域に3階建ての店舗を建設"
        )
        
        assert result["success"] is True
        analysis_id = result["data"]["analysis_id"]
        assert analysis_id in self.rbs.analyses
        
        analysis = self.rbs.analyses[analysis_id]
        assert analysis.context == "都市部の商業地域に3階建ての店舗を建設"

    def test_rbs_structure_contains_all_categories(self):
        """RBS構造に全カテゴリが含まれることのテスト"""
        result = self.rbs.create_structure("テストプロジェクト", "新商品開発")
        
        structure = result["data"]["rbs_structure"]
        expected_categories = ["技術的リスク", "外部リスク", "組織リスク", "プロジェクト管理リスク"]
        
        for category in expected_categories:
            assert category in structure
            assert "subcategories" in structure[category]
            assert "total_examples" in structure[category]

    def test_project_type_recommendations(self):
        """プロジェクトタイプ別推奨事項のテスト"""
        # IT・システム開発
        result = self.rbs.create_structure("システム開発", "IT・システム開発")
        focus = result["data"]["recommended_focus"]
        assert len(focus) > 0
        assert any("技術的リスク" in item for item in focus)
        
        # インフラ・建設
        result = self.rbs.create_structure("建設プロジェクト", "インフラ・建設")
        focus = result["data"]["recommended_focus"]
        assert any("外部環境" in item or "安全管理" in item for item in focus)
        
        # 組織変革
        result = self.rbs.create_structure("組織改革", "組織変革")
        focus = result["data"]["recommended_focus"]
        assert any("組織リスク" in item or "抵抗" in item for item in focus)

    def test_identify_risks_basic(self):
        """基本的なリスク識別のテスト"""
        # まずRBS構造を作成
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        # リスクを識別
        risks = [
            {
                "name": "データベース性能問題",
                "description": "大量データアクセス時の性能劣化",
                "probability": 3,
                "impact": 4
            },
            {
                "name": "APIの仕様変更",
                "description": "外部APIの仕様が予告なく変更される",
                "probability": 2,
                "impact": 3
            }
        ]
        
        result = self.rbs.identify_risks(analysis_id, "技術的リスク", "システム統合", risks)
        
        assert result["success"] is True
        assert "✅" in result["message"]
        assert "2件のリスクを" in result["message"]
        assert result["data"]["analysis_id"] == analysis_id
        assert result["data"]["category"] == "技術的リスク"
        assert result["data"]["subcategory"] == "システム統合"
        assert len(result["data"]["added_risks"]) == 2

    def test_identify_risks_invalid_analysis_id(self):
        """無効な分析IDでのリスク識別テスト"""
        risks = [{"name": "テストリスク", "description": "テスト用のリスク"}]
        result = self.rbs.identify_risks("invalid_id", "技術的リスク", "テスト", risks)
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_identify_risks_invalid_category(self):
        """無効なカテゴリでのリスク識別テスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        risks = [{"name": "テストリスク", "description": "テスト用のリスク"}]
        result = self.rbs.identify_risks(analysis_id, "無効なカテゴリ", "テスト", risks)
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "無効なリスクカテゴリ" in result["message"]

    def test_evaluate_risks_basic(self):
        """基本的なリスク評価のテスト"""
        # RBS構造作成とリスク追加
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        risks = [
            {"name": "高リスク項目", "description": "影響度大", "probability": 4, "impact": 5},
            {"name": "中リスク項目", "description": "標準的", "probability": 3, "impact": 3},
            {"name": "低リスク項目", "description": "影響軽微", "probability": 2, "impact": 2}
        ]
        
        self.rbs.identify_risks(analysis_id, "技術的リスク", "システム統合", risks)
        
        # リスク評価
        result = self.rbs.evaluate_risks(analysis_id)
        
        assert result["success"] is True
        assert "📊" in result["message"]
        assert "3件のリスク" in result["message"]
        assert "data" in result
        assert "risk_matrix" in result["data"]
        assert "statistics" in result["data"]
        assert "priority_groups" in result["data"]
        assert "recommendations" in result["data"]

    def test_evaluate_risks_no_risks(self):
        """リスクが存在しない場合の評価テスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        result = self.rbs.evaluate_risks(analysis_id)
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "評価対象のリスクがありません" in result["message"]

    def test_evaluate_risks_invalid_analysis_id(self):
        """無効な分析IDでのリスク評価テスト"""
        result = self.rbs.evaluate_risks("invalid_id")
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_risk_matrix_creation(self):
        """リスクマトリックス作成のテスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        # 異なる確率・影響度のリスクを追加
        risks = [
            {"name": "高確率高影響", "description": "最も危険", "probability": 5, "impact": 5},
            {"name": "低確率高影響", "description": "影響大だが稀", "probability": 1, "impact": 5},
            {"name": "高確率低影響", "description": "頻繁だが軽微", "probability": 5, "impact": 1}
        ]
        
        self.rbs.identify_risks(analysis_id, "技術的リスク", "品質保証", risks)
        result = self.rbs.evaluate_risks(analysis_id)
        
        matrix = result["data"]["risk_matrix"]
        
        # マトリックス構造の確認
        assert "5" in matrix
        assert "1" in matrix["5"]
        assert "5" in matrix["5"]
        
        # 高確率高影響セル(5,5)にリスクが存在することを確認
        assert len(matrix["5"]["5"]) == 1
        assert matrix["5"]["5"][0]["name"] == "高確率高影響"

    def test_priority_grouping(self):
        """優先度別グループ化のテスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        risks = [
            {"name": "最高優先", "description": "スコア20", "probability": 5, "impact": 4},  # 20
            {"name": "高優先", "description": "スコア12", "probability": 3, "impact": 4},   # 12
            {"name": "中優先", "description": "スコア9", "probability": 3, "impact": 3},    # 9
            {"name": "低優先", "description": "スコア6", "probability": 2, "impact": 3},    # 6
            {"name": "最低優先", "description": "スコア2", "probability": 1, "impact": 2}   # 2
        ]
        
        self.rbs.identify_risks(analysis_id, "技術的リスク", "品質保証", risks)
        result = self.rbs.evaluate_risks(analysis_id)
        
        groups = result["data"]["priority_groups"]
        
        assert len(groups["最高優先"]) == 1
        assert len(groups["高優先"]) == 1
        assert len(groups["中優先"]) == 1
        assert len(groups["低優先"]) == 1
        assert len(groups["最低優先"]) == 1
        
        assert groups["最高優先"][0]["name"] == "最高優先"
        assert groups["高優先"][0]["name"] == "高優先"

    def test_risk_statistics_calculation(self):
        """リスク統計計算のテスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        risks = [
            {"name": "リスク1", "description": "技術", "probability": 4, "impact": 5},  # 20
            {"name": "リスク2", "description": "組織", "probability": 2, "impact": 3},  # 6
            {"name": "リスク3", "description": "外部", "probability": 3, "impact": 4}   # 12
        ]
        
        # 異なるカテゴリに追加
        self.rbs.identify_risks(analysis_id, "技術的リスク", "品質保証", [risks[0]])
        self.rbs.identify_risks(analysis_id, "組織リスク", "人的リソース", [risks[1]])
        self.rbs.identify_risks(analysis_id, "外部リスク", "市場・競合", [risks[2]])
        
        result = self.rbs.evaluate_risks(analysis_id)
        stats = result["data"]["statistics"]
        
        assert stats["total_risks"] == 3
        assert stats["average_score"] == 12.67  # (20+6+12)/3 ≈ 12.67
        assert stats["max_score"] == 20
        assert stats["min_score"] == 6
        assert stats["high_priority_count"] == 2  # スコア12以上は2件
        assert "技術的リスク" in stats["category_distribution"]
        assert "組織リスク" in stats["category_distribution"]
        assert "外部リスク" in stats["category_distribution"]

    def test_get_analysis_valid(self):
        """有効な分析取得のテスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        risks = [{"name": "テストリスク", "description": "テスト用", "probability": 3, "impact": 3}]
        self.rbs.identify_risks(analysis_id, "技術的リスク", "システム統合", risks)
        
        result = self.rbs.get_analysis(analysis_id)
        
        assert result["success"] is True
        assert "📋" in result["message"]
        assert result["data"]["id"] == analysis_id
        assert result["data"]["project_name"] == "テストプロジェクト"
        assert result["data"]["risk_count"] == 1
        assert len(result["data"]["risks"]) == 1
        assert "risk_summary" in result["data"]

    def test_get_analysis_invalid_id(self):
        """無効なID指定での分析取得テスト"""
        result = self.rbs.get_analysis("invalid_id")
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_list_analyses_empty(self):
        """空の分析リスト取得テスト"""
        result = self.rbs.list_analyses()
        
        assert result["success"] is True
        assert "📋" in result["message"]
        assert "まだ作成されていません" in result["message"]
        assert result["data"]["analyses"] == []

    def test_list_analyses_multiple(self):
        """複数分析のリスト取得テスト"""
        # 複数の分析を作成
        self.rbs.create_structure("プロジェクト1", "IT・システム開発")
        self.rbs.create_structure("プロジェクト2", "新商品開発")
        self.rbs.create_structure("プロジェクト3", "インフラ・建設")
        
        result = self.rbs.list_analyses()
        
        assert result["success"] is True
        assert "📋" in result["message"]
        assert "3件のRBS分析" in result["message"]
        assert len(result["data"]["analyses"]) == 3
        assert result["data"]["total_count"] == 3
        
        # 作成日時でソートされていることを確認（新しい順）
        analyses = result["data"]["analyses"]
        assert analyses[0]["project_name"] == "プロジェクト3"  # 最後に作成
        assert analyses[2]["project_name"] == "プロジェクト1"  # 最初に作成

    def test_risk_item_creation_and_properties(self):
        """RiskItemクラスの作成とプロパティテスト"""
        risk = RiskItem(
            name="データベース障害",
            description="メインデータベースサーバーの突然の停止",
            category=RiskCategory.TECHNICAL,
            subcategory="システム統合",
            probability=RiskProbability.LOW,
            impact=RiskImpact.VERY_HIGH
        )
        
        assert risk.name == "データベース障害"
        assert risk.category == RiskCategory.TECHNICAL
        assert risk.risk_score == 10  # 2 * 5 = 10
        assert len(risk.id) == 8  # 短縮UUID
        
        risk_dict = risk.to_dict()
        assert risk_dict["name"] == "データベース障害"
        assert risk_dict["category"] == "技術的リスク"
        assert risk_dict["risk_score"] == 10
        assert risk_dict["priority"] == "中優先"  # スコア10は中優先
        assert risk_dict["probability"]["label"] == "低い"
        assert risk_dict["impact"]["label"] == "非常に重大"

    def test_rbs_analysis_risk_management(self):
        """RBSAnalysisクラスのリスク管理テスト"""
        analysis = RBSAnalysis("テストプロジェクト", "IT・システム開発", "テストコンテキスト")
        
        # リスクの追加
        risk1 = RiskItem("リスク1", "説明1", RiskCategory.TECHNICAL, "サブカテゴリ1")
        risk2 = RiskItem("リスク2", "説明2", RiskCategory.ORGANIZATIONAL, "サブカテゴリ2")
        high_risk = RiskItem("高リスク", "高影響", RiskCategory.EXTERNAL, "サブ", 
                           RiskProbability.HIGH, RiskImpact.VERY_HIGH)
        
        analysis.add_risk(risk1)
        analysis.add_risk(risk2)
        analysis.add_risk(high_risk)
        
        assert len(analysis.risks) == 3
        
        # カテゴリ別取得
        tech_risks = analysis.get_risks_by_category(RiskCategory.TECHNICAL)
        assert len(tech_risks) == 1
        assert tech_risks[0].name == "リスク1"
        
        # 高優先度リスク取得
        high_priority = analysis.get_high_priority_risks()
        assert len(high_priority) == 1
        assert high_priority[0].name == "高リスク"
        assert high_priority[0].risk_score == 20  # 4 * 5 = 20

    def test_comprehensive_rbs_workflow(self):
        """包括的なRBSワークフローのテスト"""
        # 1. RBS構造作成
        structure_result = self.rbs.create_structure("ECサイトリニューアル", "IT・システム開発", 
                                                   "レガシーシステムからの移行を含む")
        assert structure_result["success"] is True
        analysis_id = structure_result["data"]["analysis_id"]
        
        # 2. 技術的リスクの識別
        tech_risks = [
            {"name": "レガシーDB移行", "description": "データ移行での整合性問題", "probability": 4, "impact": 4},
            {"name": "性能要件未達", "description": "想定トラフィックに対応できない", "probability": 3, "impact": 5}
        ]
        tech_result = self.rbs.identify_risks(analysis_id, "技術的リスク", "システム統合", tech_risks)
        assert tech_result["success"] is True
        
        # 3. 組織リスクの識別
        org_risks = [
            {"name": "キーパーソン離職", "description": "システム知識を持つ担当者の退職", "probability": 2, "impact": 4}
        ]
        org_result = self.rbs.identify_risks(analysis_id, "組織リスク", "人的リソース", org_risks)
        assert org_result["success"] is True
        
        # 4. リスク評価
        eval_result = self.rbs.evaluate_risks(analysis_id)
        assert eval_result["success"] is True
        assert eval_result["data"]["statistics"]["total_risks"] == 3
        
        # 5. 分析取得
        analysis_result = self.rbs.get_analysis(analysis_id)
        assert analysis_result["success"] is True
        assert len(analysis_result["data"]["risks"]) == 3
        
        # 6. リスト確認
        list_result = self.rbs.list_analyses()
        assert list_result["success"] is True
        assert len(list_result["data"]["analyses"]) == 1

    def test_risk_recommendations_generation(self):
        """リスク推奨事項生成のテスト"""
        structure_result = self.rbs.create_structure("テストプロジェクト", "IT・システム開発")
        analysis_id = structure_result["data"]["analysis_id"]
        
        # 多数の高優先度リスクを追加
        high_risks = [
            {"name": f"高リスク{i}", "description": f"説明{i}", "probability": 4, "impact": 4}
            for i in range(5)
        ]
        low_risks = [
            {"name": f"低リスク{i}", "description": f"説明{i}", "probability": 1, "impact": 2}
            for i in range(8)
        ]
        
        all_risks = high_risks + low_risks
        self.rbs.identify_risks(analysis_id, "技術的リスク", "品質保証", all_risks)
        
        result = self.rbs.evaluate_risks(analysis_id)
        recommendations = result["data"]["recommendations"]
        
        # 高優先度リスクに関する推奨事項
        assert any("5件の高優先度リスク" in rec for rec in recommendations)
        # 多数のリスクに関する推奨事項
        assert any("リスク数が多い" in rec for rec in recommendations)
        # 基本的な推奨事項
        assert any("定期的なリスク評価" in rec for rec in recommendations)

    def test_long_project_name_handling(self):
        """長いプロジェクト名の処理テスト"""
        long_name = "非常に長いプロジェクト名" * 10
        result = self.rbs.create_structure(long_name, "IT・システム開発")
        
        assert result["success"] is True
        assert result["data"]["project_name"] == long_name
        
        # 分析取得でも長い名前が保持されることを確認
        analysis_id = result["data"]["analysis_id"]
        get_result = self.rbs.get_analysis(analysis_id)
        assert get_result["data"]["project_name"] == long_name

    def test_risk_template_initialization(self):
        """リスクテンプレート初期化のテスト"""
        templates = self.rbs.risk_templates
        
        # 全カテゴリが存在することを確認
        for category in RiskCategory:
            assert category in templates
            
        # 技術的リスクのテンプレート確認
        tech_templates = templates[RiskCategory.TECHNICAL]
        assert "技術要件" in tech_templates
        assert "システム統合" in tech_templates
        assert "品質保証" in tech_templates
        
        # 各サブカテゴリにサンプルリスクが存在することを確認
        for subcategory, risks in tech_templates.items():
            assert len(risks) > 0
            for risk in risks:
                assert isinstance(risk, str)
                assert len(risk) > 0