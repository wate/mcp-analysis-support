"""Tests for m-SHELL Model implementation."""

import pytest
from src.analysis_support.tools.mshell import MShell, MShellElement, AnalysisSeverity, ElementAnalysis, InterfaceAnalysis, MShellAnalysis


class TestMShell:
    """m-SHELLモデルのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.mshell = MShell()

    def test_create_analysis_basic(self):
        """基本的なm-SHELL分析作成のテスト"""
        result = self.mshell.create_analysis("航空機運航システム", "安全性向上のための分析")
        
        assert result["success"] is True
        assert "🔍" in result["message"]
        assert "data" in result
        assert "analysis_id" in result["data"]
        assert result["data"]["system_name"] == "航空機運航システム"
        assert result["data"]["analysis_purpose"] == "安全性向上のための分析"
        assert len(result["data"]["available_elements"]) == 6
        assert "element_descriptions" in result["data"]

    def test_create_analysis_with_context(self):
        """コンテキスト付きm-SHELL分析作成のテスト"""
        result = self.mshell.create_analysis(
            "医療機器システム", 
            "ヒューマンエラー防止",
            "手術室での機器操作における安全性確保"
        )
        
        assert result["success"] is True
        analysis_id = result["data"]["analysis_id"]
        assert analysis_id in self.mshell.analyses
        
        analysis = self.mshell.analyses[analysis_id]
        assert analysis.context == "手術室での機器操作における安全性確保"

    def test_analyze_element_basic(self):
        """基本的な要素分析のテスト"""
        # 分析作成
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        # Machine要素の分析
        findings = [
            "機械の応答速度が遅い",
            "異常時の警告表示が不明確",
            "保守性に問題がある"
        ]
        recommendations = [
            "処理速度の改善",
            "警告システムの見直し"
        ]
        
        result = self.mshell.analyze_element(
            analysis_id, 
            "Machine", 
            findings, 
            severity=3,
            recommendations=recommendations
        )
        
        assert result["success"] is True
        assert "✅" in result["message"]
        assert "機械・設備" in result["message"]
        assert "element_analysis" in result["data"]
        assert result["data"]["element_analysis"]["element"] == "Machine"
        assert result["data"]["element_analysis"]["severity"]["value"] == 3
        assert len(result["data"]["element_analysis"]["findings"]) == 3
        assert len(result["data"]["element_analysis"]["recommendations"]) == 2

    def test_analyze_element_invalid_analysis_id(self):
        """無効な分析IDでの要素分析テスト"""
        result = self.mshell.analyze_element("invalid_id", "Machine", ["テスト"])
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_analyze_element_invalid_element(self):
        """無効な要素での分析テスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        result = self.mshell.analyze_element(analysis_id, "InvalidElement", ["テスト"])
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "無効な要素" in result["message"]

    def test_analyze_element_invalid_severity(self):
        """無効な重要度での要素分析テスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        result = self.mshell.analyze_element(analysis_id, "Machine", ["テスト"], severity=5)
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "無効な重要度" in result["message"]

    def test_analyze_all_elements(self):
        """全要素の分析テスト"""
        create_result = self.mshell.create_analysis("統合システム", "全体評価")
        analysis_id = create_result["data"]["analysis_id"]
        
        elements_data = [
            ("Machine", ["機械的問題1", "機械的問題2"], 2),
            ("Software", ["ソフトウェア問題1"], 3),
            ("Hardware", ["ハードウェア問題1", "ハードウェア問題2"], 1),
            ("Environment", ["環境問題1"], 2),
            ("Liveware-Central", ["中心人物の問題1"], 4),
            ("Liveware-Other", ["他者との連携問題1"], 2)
        ]
        
        for element, findings, severity in elements_data:
            result = self.mshell.analyze_element(analysis_id, element, findings, severity)
            assert result["success"] is True
        
        # 分析取得で確認
        get_result = self.mshell.get_analysis(analysis_id)
        assert len(get_result["data"]["element_analyses"]) == 6

    def test_analyze_interface_basic(self):
        """基本的なインターフェース分析のテスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        issues = [
            "機械とソフトウェアの連携に遅延",
            "データ転送エラーが頻発",
            "同期処理の問題"
        ]
        
        result = self.mshell.analyze_interface(
            analysis_id,
            "Machine",
            "Software", 
            issues,
            quality_score=3
        )
        
        assert result["success"] is True
        assert "✅" in result["message"]
        assert "機械 ↔ SW" in result["message"]
        assert "interface_analysis" in result["data"]
        assert result["data"]["interface_analysis"]["quality_score"] == 3
        assert result["data"]["interface_analysis"]["quality_level"] == "問題あり"
        assert len(result["data"]["interface_analysis"]["issues"]) == 3

    def test_analyze_interface_invalid_analysis_id(self):
        """無効な分析IDでのインターフェース分析テスト"""
        result = self.mshell.analyze_interface("invalid_id", "Machine", "Software", ["テスト"])
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_analyze_interface_invalid_elements(self):
        """無効な要素でのインターフェース分析テスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        result = self.mshell.analyze_interface(analysis_id, "InvalidElement", "Software", ["テスト"])
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "無効な要素" in result["message"]

    def test_analyze_interface_same_elements(self):
        """同じ要素同士のインターフェース分析テスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        result = self.mshell.analyze_interface(analysis_id, "Machine", "Machine", ["テスト"])
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "同じ要素同士" in result["message"]

    def test_evaluate_system_basic(self):
        """基本的なシステム評価のテスト"""
        create_result = self.mshell.create_analysis("評価対象システム", "総合評価")
        analysis_id = create_result["data"]["analysis_id"]
        
        # 要素分析を追加
        self.mshell.analyze_element(analysis_id, "Machine", ["問題1"], 2)
        self.mshell.analyze_element(analysis_id, "Software", ["問題2"], 3)
        self.mshell.analyze_element(analysis_id, "Hardware", ["問題3"], 1)
        
        # インターフェース分析を追加
        self.mshell.analyze_interface(analysis_id, "Machine", "Software", ["連携問題"], 6)
        self.mshell.analyze_interface(analysis_id, "Software", "Hardware", ["互換性問題"], 4)
        
        # システム評価
        result = self.mshell.evaluate_system(analysis_id)
        
        assert result["success"] is True
        assert "📊" in result["message"]
        assert "evaluation" in result["data"]
        assert "overall_score" in result["data"]["evaluation"]
        assert "overall_level" in result["data"]["evaluation"]
        assert "recommendations" in result["data"]
        
        evaluation = result["data"]["evaluation"]
        assert 0 <= evaluation["overall_score"] <= 10
        assert "element_scores" in evaluation
        assert "average_interface_score" in evaluation

    def test_evaluate_system_no_data(self):
        """データなしでのシステム評価テスト"""
        create_result = self.mshell.create_analysis("テストシステム", "テスト目的")
        analysis_id = create_result["data"]["analysis_id"]
        
        result = self.mshell.evaluate_system(analysis_id)
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "評価対象の分析データがありません" in result["message"]

    def test_evaluate_system_invalid_analysis_id(self):
        """無効な分析IDでのシステム評価テスト"""
        result = self.mshell.evaluate_system("invalid_id")
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_system_evaluation_scores(self):
        """システム評価スコア計算のテスト"""
        create_result = self.mshell.create_analysis("スコア計算テスト", "評価検証")
        analysis_id = create_result["data"]["analysis_id"]
        
        # 異なる重要度の要素分析
        self.mshell.analyze_element(analysis_id, "Machine", ["軽微な問題"], 1)      # score: 4
        self.mshell.analyze_element(analysis_id, "Software", ["重要な問題"], 3)      # score: 2
        self.mshell.analyze_element(analysis_id, "Hardware", ["致命的問題"], 4)      # score: 1
        
        # 異なる品質のインターフェース分析
        self.mshell.analyze_interface(analysis_id, "Machine", "Software", ["問題"], 8)    # 良好
        self.mshell.analyze_interface(analysis_id, "Software", "Hardware", ["問題"], 3)  # 問題あり
        
        result = self.mshell.evaluate_system(analysis_id)
        evaluation = result["data"]["evaluation"]
        
        # 要素スコア平均: (4+2+1)/3 ≈ 2.33
        # インターフェーススコア平均: (8+3)/2 = 5.5
        # 総合スコア: 2.33*0.6 + 5.5*0.4 = 1.4 + 2.2 = 3.6
        
        assert evaluation["average_element_score"] == 2.33
        assert evaluation["average_interface_score"] == 5.5
        assert evaluation["overall_score"] == 3.6
        assert evaluation["overall_level"] == "要改善"

    def test_get_analysis_valid(self):
        """有効な分析取得のテスト"""
        create_result = self.mshell.create_analysis("取得テスト", "データ確認")
        analysis_id = create_result["data"]["analysis_id"]
        
        # データを追加
        self.mshell.analyze_element(analysis_id, "Machine", ["テスト問題"], 2, ["改善案"])
        self.mshell.analyze_interface(analysis_id, "Machine", "Software", ["連携問題"], 7)
        
        result = self.mshell.get_analysis(analysis_id)
        
        assert result["success"] is True
        assert "🔍" in result["message"]
        assert result["data"]["id"] == analysis_id
        assert result["data"]["system_name"] == "取得テスト"
        assert len(result["data"]["element_analyses"]) == 1
        assert len(result["data"]["interface_analyses"]) == 1
        assert "analysis_summary" in result["data"]

    def test_get_analysis_invalid_id(self):
        """無効なID指定での分析取得テスト"""
        result = self.mshell.get_analysis("invalid_id")
        
        assert result["success"] is False
        assert "❌" in result["message"]
        assert "が見つかりません" in result["message"]

    def test_list_analyses_empty(self):
        """空の分析リスト取得テスト"""
        result = self.mshell.list_analyses()
        
        assert result["success"] is True
        assert "🔍" in result["message"]
        assert "まだ作成されていません" in result["message"]
        assert result["data"]["analyses"] == []

    def test_list_analyses_multiple(self):
        """複数分析のリスト取得テスト"""
        # 複数の分析を作成
        self.mshell.create_analysis("システム1", "目的1")
        self.mshell.create_analysis("システム2", "目的2")
        self.mshell.create_analysis("システム3", "目的3")
        
        result = self.mshell.list_analyses()
        
        assert result["success"] is True
        assert "🔍" in result["message"]
        assert "3件のm-SHELL分析" in result["message"]
        assert len(result["data"]["analyses"]) == 3
        assert result["data"]["total_count"] == 3
        
        # 作成日時でソートされていることを確認（新しい順）
        analyses = result["data"]["analyses"]
        assert analyses[0]["system_name"] == "システム3"  # 最後に作成
        assert analyses[2]["system_name"] == "システム1"  # 最初に作成

    def test_element_analysis_creation_and_properties(self):
        """ElementAnalysisクラスの作成とプロパティテスト"""
        findings = ["問題1", "問題2", "問題3"]
        recommendations = ["改善案1", "改善案2"]
        
        element = ElementAnalysis(
            MShellElement.LIVEWARE_CENTRAL,
            findings,
            AnalysisSeverity.HIGH,
            recommendations
        )
        
        assert element.element == MShellElement.LIVEWARE_CENTRAL
        assert element.findings == findings
        assert element.severity == AnalysisSeverity.HIGH
        assert element.recommendations == recommendations
        assert len(element.id) == 8  # 短縮UUID
        
        element_dict = element.to_dict()
        assert element_dict["element"] == "Liveware-Central"
        assert element_dict["element_jp"] == "中心人物・主要オペレーター"
        assert element_dict["severity"]["value"] == 3
        assert element_dict["severity"]["label"] == "重要"
        assert len(element_dict["findings"]) == 3
        assert len(element_dict["recommendations"]) == 2

    def test_interface_analysis_creation_and_properties(self):
        """InterfaceAnalysisクラスの作成とプロパティテスト"""
        issues = ["インターフェース問題1", "問題2"]
        
        interface = InterfaceAnalysis(
            MShellElement.MACHINE,
            MShellElement.ENVIRONMENT,
            issues,
            interaction_quality=7
        )
        
        assert interface.element1 == MShellElement.MACHINE
        assert interface.element2 == MShellElement.ENVIRONMENT
        assert interface.interface_issues == issues
        assert interface.interaction_quality == 7
        
        interface_dict = interface.to_dict()
        assert interface_dict["interface"] == "Machine ↔ Environment"
        assert interface_dict["interface_jp"] == "機械 ↔ 環境"
        assert interface_dict["quality_score"] == 7
        assert interface_dict["quality_level"] == "普通"
        assert len(interface_dict["issues"]) == 2

    def test_mshell_analysis_management(self):
        """MShellAnalysisクラスの管理機能テスト"""
        analysis = MShellAnalysis("管理テスト", "機能確認", "詳細コンテキスト")
        
        # 要素分析追加
        element1 = ElementAnalysis(MShellElement.MACHINE, ["問題1"], AnalysisSeverity.HIGH)
        element2 = ElementAnalysis(MShellElement.SOFTWARE, ["問題2"], AnalysisSeverity.CRITICAL)
        element3 = ElementAnalysis(MShellElement.HARDWARE, ["問題3"], AnalysisSeverity.LOW)
        
        analysis.add_element_analysis(element1)
        analysis.add_element_analysis(element2)  
        analysis.add_element_analysis(element3)
        
        assert len(analysis.element_analyses) == 3
        
        # インターフェース分析追加
        interface1 = InterfaceAnalysis(MShellElement.MACHINE, MShellElement.SOFTWARE, ["問題"], 8)
        interface2 = InterfaceAnalysis(MShellElement.SOFTWARE, MShellElement.HARDWARE, ["問題"], 3)
        
        analysis.add_interface_analysis(interface1)
        analysis.add_interface_analysis(interface2)
        
        assert len(analysis.interface_analyses) == 2
        
        # 致命的問題の取得
        critical_issues = analysis.get_critical_issues()
        assert len(critical_issues) == 1
        assert critical_issues[0].severity == AnalysisSeverity.CRITICAL
        
        # インターフェース問題の取得
        interface_problems = analysis.get_interface_problems()
        assert len(interface_problems) == 1
        assert interface_problems[0].interaction_quality == 3

    def test_analysis_templates_initialization(self):
        """分析テンプレート初期化のテスト"""
        templates = self.mshell.analysis_templates
        
        # 全要素のテンプレートが存在することを確認
        for element in MShellElement:
            assert element in templates
            
        # Machine要素のテンプレート確認
        machine_templates = templates[MShellElement.MACHINE]
        assert "設計・機能" in machine_templates
        assert "信頼性・保守性" in machine_templates
        assert "操作性" in machine_templates
        
        # 各カテゴリにチェックポイントが存在することを確認
        for category, checkpoints in machine_templates.items():
            assert len(checkpoints) > 0
            for checkpoint in checkpoints:
                assert isinstance(checkpoint, str)
                assert len(checkpoint) > 0

    def test_interface_matrix_initialization(self):
        """インターフェースマトリックス初期化のテスト"""
        matrix = self.mshell.interface_matrix
        
        # 要素間の全組み合わせが存在することを確認（重複なし）
        elements = list(MShellElement)
        expected_combinations = len(elements) * (len(elements) - 1) // 2
        assert len(matrix) == expected_combinations
        
        # Machine-Software間のチェックポイント確認
        key = (MShellElement.MACHINE, MShellElement.SOFTWARE)
        if key in matrix:
            checkpoints = matrix[key]
        else:
            key = (MShellElement.SOFTWARE, MShellElement.MACHINE)
            checkpoints = matrix[key]
        
        assert len(checkpoints) > 0
        assert any("制御" in cp or "フィードバック" in cp for cp in checkpoints)

    def test_comprehensive_mshell_workflow(self):
        """包括的なm-SHELLワークフローのテスト"""
        # 1. 分析作成
        create_result = self.mshell.create_analysis(
            "病院手術システム", 
            "医療安全向上",
            "手術室での機器操作とチーム連携の改善"
        )
        assert create_result["success"] is True
        analysis_id = create_result["data"]["analysis_id"]
        
        # 2. 複数要素の分析
        elements_to_analyze = [
            ("Machine", ["手術機器の応答遅延", "警告音が聞こえにくい"], 3, ["機器更新", "音響改善"]),
            ("Liveware-Central", ["外科医の疲労", "判断ミス"], 4, ["休憩時間確保", "支援システム"]),
            ("Environment", ["手術室照明不足", "騒音レベル高"], 2, ["照明改善", "騒音対策"])
        ]
        
        for element, findings, severity, recommendations in elements_to_analyze:
            result = self.mshell.analyze_element(analysis_id, element, findings, severity, recommendations)
            assert result["success"] is True
        
        # 3. インターフェース分析
        interfaces = [
            ("Machine", "Liveware-Central", ["操作性の問題", "フィードバック不足"], 4),
            ("Liveware-Central", "Environment", ["環境ストレス", "集中力低下"], 6)
        ]
        
        for elem1, elem2, issues, quality in interfaces:
            result = self.mshell.analyze_interface(analysis_id, elem1, elem2, issues, quality)
            assert result["success"] is True
        
        # 4. システム評価
        eval_result = self.mshell.evaluate_system(analysis_id)
        assert eval_result["success"] is True
        assert len(eval_result["data"]["critical_issues"]) == 1  # Liveware-Central
        
        # 5. 分析取得
        get_result = self.mshell.get_analysis(analysis_id)
        assert get_result["success"] is True
        assert len(get_result["data"]["element_analyses"]) == 3
        assert len(get_result["data"]["interface_analyses"]) == 2
        
        # 6. 推奨事項確認
        recommendations = eval_result["data"]["recommendations"]
        assert any("致命的問題" in rec for rec in recommendations)
        assert any("インターフェース改善" in rec for rec in recommendations)

    def test_severity_and_quality_level_mapping(self):
        """重要度と品質レベルマッピングのテスト"""
        # 重要度レベルのテスト
        severities = [
            (AnalysisSeverity.LOW, "軽微"),
            (AnalysisSeverity.MEDIUM, "中程度"),
            (AnalysisSeverity.HIGH, "重要"),
            (AnalysisSeverity.CRITICAL, "致命的")
        ]
        
        for severity_enum, expected_label in severities:
            element = ElementAnalysis(MShellElement.MACHINE, ["テスト"], severity_enum)
            assert element._get_severity_label() == expected_label
        
        # 品質レベルのテスト
        quality_levels = [
            (9, "良好"),
            (6, "普通"),
            (4, "要改善"),
            (2, "問題あり")
        ]
        
        for quality_score, expected_level in quality_levels:
            interface = InterfaceAnalysis(
                MShellElement.MACHINE, MShellElement.SOFTWARE, ["テスト"], quality_score
            )
            assert interface._get_quality_level() == expected_level

    def test_system_evaluation_edge_cases(self):
        """システム評価のエッジケーステスト"""
        create_result = self.mshell.create_analysis("エッジケーステスト", "境界値確認")
        analysis_id = create_result["data"]["analysis_id"]
        
        # 要素のみ（インターフェースなし）の評価
        self.mshell.analyze_element(analysis_id, "Machine", ["問題"], 2)
        result = self.mshell.evaluate_system(analysis_id)
        
        evaluation = result["data"]["evaluation"]
        assert evaluation["average_interface_score"] == 0
        assert evaluation["overall_score"] == evaluation["average_element_score"]  # インターフェーススコアが0の場合
        
        # 全要素が致命的な場合
        analysis2 = self.mshell.create_analysis("致命的テスト", "最悪ケース")["data"]["analysis_id"]
        for element in ["Machine", "Software", "Hardware"]:
            self.mshell.analyze_element(analysis2, element, ["致命的問題"], 4)
        
        result2 = self.mshell.evaluate_system(analysis2)
        evaluation2 = result2["data"]["evaluation"]
        assert evaluation2["average_element_score"] == 1.0  # 5-4 = 1
        assert evaluation2["overall_level"] == "危険"

    def test_long_system_name_handling(self):
        """長いシステム名の処理テスト"""
        long_name = "非常に長いシステム名" * 20
        result = self.mshell.create_analysis(long_name, "長い名前のテスト")
        
        assert result["success"] is True
        assert result["data"]["system_name"] == long_name
        
        # 分析取得でも長い名前が保持されることを確認
        analysis_id = result["data"]["analysis_id"]
        get_result = self.mshell.get_analysis(analysis_id)
        assert get_result["data"]["system_name"] == long_name