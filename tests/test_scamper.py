"""SCAMPER法ツールのテスト."""

import pytest
from datetime import datetime

from analysis_support.tools.scamper import SCAMPER, SCAMPERTechnique


class TestSCAMPER:
    """SCAMPER法のテストクラス."""
    
    def setup_method(self) -> None:
        """各テストメソッドの前に実行される初期化."""
        self.analyzer = SCAMPER()
    
    def test_start_session_basic(self) -> None:
        """基本的なセッション開始のテスト."""
        topic = "オンライン会議の効率化"
        current_situation = "現在のオンライン会議は時間が長く、参加者の集中力が続かない"
        
        result = self.analyzer.start_session(topic, current_situation)
        
        assert result["success"] is True
        assert "session_id" in result
        assert len(result["session_id"]) == 36  # フルUUID
        assert result["topic"] == topic
        assert "techniques_overview" in result
        assert len(result["techniques_overview"]) == 7  # 7つの技法
        assert "usage_guide" in result
    
    def test_start_session_with_context(self) -> None:
        """コンテキスト付きセッション開始のテスト."""
        topic = "商品パッケージの改善"
        current_situation = "現在のパッケージは環境に優しくない"
        context = "予算制約あり、6ヶ月以内に実装必要"
        
        result = self.analyzer.start_session(topic, current_situation, context)
        
        assert result["success"] is True
        # セッションデータにcontextが保存されていることを確認
        session_id = result["session_id"]
        session = self.analyzer._sessions[session_id]
        assert session.context == context
    
    def test_apply_technique_substitute(self) -> None:
        """Substitute技法適用のテスト."""
        # セッション開始
        start_result = self.analyzer.start_session("テスト課題", "現在の状況")
        session_id = start_result["session_id"]
        
        # Substitute技法適用
        ideas = ["プラスチックを紙素材に置き換える", "対面会議をオンライン会議に置き換える"]
        explanations = ["環境負荷を削減", "移動時間とコストを削減"]
        
        result = self.analyzer.apply_technique(session_id, "substitute", ideas, explanations)
        
        assert result["success"] is True
        assert result["technique"] == "Substitute"
        assert len(result["added_ideas"]) == 2
        assert "technique_guide" in result
        assert "session_stats" in result
    
    def test_apply_technique_japanese_name(self) -> None:
        """日本語技法名での適用テスト."""
        start_result = self.analyzer.start_session("テスト課題", "現在の状況")
        session_id = start_result["session_id"]
        
        # 日本語での技法指定
        ideas = ["要素Aと要素Bを組み合わせる"]
        result = self.analyzer.apply_technique(session_id, "結合", ideas)
        
        assert result["success"] is True
        assert result["technique"] == "Combine"  # 英語名で返される
    
    def test_apply_technique_invalid_session(self) -> None:
        """無効なセッションIDでの技法適用テスト."""
        result = self.analyzer.apply_technique("invalid_id", "substitute", ["アイデア"])
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_apply_technique_invalid_technique(self) -> None:
        """無効な技法での適用テスト."""
        start_result = self.analyzer.start_session("テスト課題", "現在の状況")
        session_id = start_result["session_id"]
        
        result = self.analyzer.apply_technique(session_id, "invalid_technique", ["アイデア"])
        
        assert result["success"] is False
        assert "無効です" in result["message"]
    
    def test_apply_all_techniques(self) -> None:
        """全技法適用のテスト."""
        start_result = self.analyzer.start_session("プロダクト改善", "現在の製品に課題がある")
        session_id = start_result["session_id"]
        
        techniques = ["substitute", "combine", "adapt", "modify", "put_to_other_use", "eliminate", "reverse"]
        
        for technique in techniques:
            ideas = [f"{technique}のアイデア1", f"{technique}のアイデア2"]
            result = self.analyzer.apply_technique(session_id, technique, ideas)
            assert result["success"] is True
        
        # セッション統計を確認
        session_result = self.analyzer.get_session(session_id)
        assert session_result["total_ideas"] == 14  # 7技法 × 2アイデア
        # technique_statisticsは各技法の統計を含む辞書
        technique_stats = session_result["technique_statistics"]
        used_techniques = sum(1 for stats in technique_stats.values() if stats["total_ideas"] > 0)
        assert used_techniques == 7
    
    def test_evaluate_ideas_basic(self) -> None:
        """基本的なアイデア評価のテスト."""
        # セッション作成とアイデア追加
        start_result = self.analyzer.start_session("効率化", "作業効率を上げたい")
        session_id = start_result["session_id"]
        
        ideas = ["自動化ツール導入", "作業手順の見直し"]
        self.analyzer.apply_technique(session_id, "substitute", ideas)
        
        # アイデア評価
        evaluations = [
            {"idea": "自動化ツール導入", "feasibility": 7, "impact": 9},
            {"idea": "作業手順の見直し", "feasibility": 9, "impact": 6}
        ]
        
        result = self.analyzer.evaluate_ideas(session_id, evaluations)
        
        assert result["success"] is True
        assert len(result["evaluation_results"]) == 2
        assert "top_ideas" in result
        assert "technique_statistics" in result
        assert "evaluation_summary" in result
        
        # スコア順にソートされているか確認
        top_idea = result["top_ideas"][0]
        assert top_idea["total_score"] == 16  # 7 + 9
    
    def test_evaluate_ideas_invalid_session(self) -> None:
        """無効なセッションでの評価テスト."""
        evaluations = [{"idea": "テスト", "feasibility": 5, "impact": 5}]
        result = self.analyzer.evaluate_ideas("invalid_id", evaluations)
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_get_session_valid(self) -> None:
        """有効なセッション取得のテスト."""
        start_result = self.analyzer.start_session("セッション取得テスト", "テスト状況", "テストコンテキスト")
        session_id = start_result["session_id"]
        
        # いくつかのアイデアを追加
        self.analyzer.apply_technique(session_id, "substitute", ["アイデア1", "アイデア2"])
        
        result = self.analyzer.get_session(session_id)
        
        assert result["success"] is True
        assert result["session_id"] == session_id
        assert result["topic"] == "セッション取得テスト"
        assert result["current_situation"] == "テスト状況"
        assert result["context"] == "テストコンテキスト"
        assert result["total_ideas"] == 2
        assert "technique_statistics" in result
        assert "recent_ideas" in result
        assert "session_notes" in result
    
    def test_get_session_invalid_id(self) -> None:
        """無効なIDでのセッション取得テスト."""
        result = self.analyzer.get_session("invalid_id")
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_list_sessions_empty(self) -> None:
        """空のセッション一覧テスト."""
        result = self.analyzer.list_sessions()
        
        assert result["success"] is True
        assert result["sessions"] == []
    
    def test_list_sessions_multiple(self) -> None:
        """複数セッション一覧のテスト."""
        # 2つのセッションを作成
        self.analyzer.start_session("セッション1", "状況1")
        self.analyzer.start_session("セッション2", "状況2")
        
        result = self.analyzer.list_sessions()
        
        assert result["success"] is True
        assert len(result["sessions"]) == 2
        
        # 各セッションに必要な情報が含まれているか確認
        session_info = result["sessions"][0]
        assert "id" in session_info
        assert "topic" in session_info
        assert "total_ideas" in session_info
        assert "techniques_used" in session_info
        assert "created_at" in session_info
        assert "updated_at" in session_info
    
    def test_generate_comprehensive_ideas(self) -> None:
        """包括的アイデア生成のテスト."""
        topic = "リモートワーク環境改善"
        current_situation = "現在のリモートワーク環境では集中できない"
        context = "自宅での作業環境"
        
        result = self.analyzer.generate_comprehensive_ideas(topic, current_situation, context)
        
        assert result["success"] is True
        assert "session_id" in result
        assert result["topic"] == topic
        assert result["current_situation"] == current_situation
        assert "technique_prompts" in result
        assert len(result["technique_prompts"]) == 7
        assert "comprehensive_approach" in result
        assert "next_steps" in result
    
    def test_technique_normalization(self) -> None:
        """技法名正規化のテスト."""
        # 英語名（大文字小文字）
        assert self.analyzer._normalize_technique("substitute") == SCAMPERTechnique.SUBSTITUTE
        assert self.analyzer._normalize_technique("Substitute") == SCAMPERTechnique.SUBSTITUTE
        
        # 日本語名
        assert self.analyzer._normalize_technique("代替") == SCAMPERTechnique.SUBSTITUTE
        assert self.analyzer._normalize_technique("結合") == SCAMPERTechnique.COMBINE
        
        # 無効な技法名
        assert self.analyzer._normalize_technique("invalid") is None
    
    def test_session_stats_calculation(self) -> None:
        """セッション統計計算のテスト."""
        start_result = self.analyzer.start_session("統計テスト", "テスト状況")
        session_id = start_result["session_id"]
        session = self.analyzer._sessions[session_id]
        
        # 複数の技法でアイデア追加
        self.analyzer.apply_technique(session_id, "substitute", ["アイデア1", "アイデア2"])
        self.analyzer.apply_technique(session_id, "combine", ["アイデア3"])
        
        stats = self.analyzer._get_session_stats(session)
        
        assert stats["total_ideas"] == 3
        assert stats["techniques_used"] == 2
        assert "technique_distribution" in stats
        assert stats["technique_distribution"]["Substitute"] == 2
        assert stats["technique_distribution"]["Combine"] == 1
    
    def test_technique_statistics_calculation(self) -> None:
        """技法別統計計算のテスト."""
        start_result = self.analyzer.start_session("統計テスト", "テスト状況")
        session_id = start_result["session_id"]
        
        # アイデア追加と評価
        self.analyzer.apply_technique(session_id, "substitute", ["アイデア1", "アイデア2"])
        evaluations = [
            {"idea": "アイデア1", "feasibility": 8, "impact": 7},
            {"idea": "アイデア2", "feasibility": 6, "impact": 9}
        ]
        self.analyzer.evaluate_ideas(session_id, evaluations)
        
        session = self.analyzer._sessions[session_id]
        stats = self.analyzer._calculate_technique_stats(session)
        
        substitute_stats = stats["Substitute"]
        assert substitute_stats["total_ideas"] == 2
        assert substitute_stats["evaluated_ideas"] == 2
        assert substitute_stats["avg_feasibility"] == 7.0  # (8 + 6) / 2
        assert substitute_stats["avg_impact"] == 8.0  # (7 + 9) / 2
        assert substitute_stats["avg_total_score"] == 15.0  # 7.0 + 8.0
    
    def test_long_topic_truncation(self) -> None:
        """長いトピックの切り詰めテスト."""
        long_topic = "これは非常に長いトピック名です。" * 10
        self.analyzer.start_session(long_topic, "テスト状況")
        
        result = self.analyzer.list_sessions()
        session_info = result["sessions"][0]
        
        # 30文字で切り詰められることを確認
        assert len(session_info["topic"]) <= 30
        if len(long_topic) > 30:
            assert session_info["topic"].endswith("...")
    
    def test_technique_guides_initialization(self) -> None:
        """技法ガイド初期化のテスト."""
        guides = self.analyzer._technique_guides
        
        assert len(guides) == 7  # 7つの技法
        
        for technique in SCAMPERTechnique:
            guide = guides[technique]
            assert "name_jp" in guide
            assert "description" in guide
            assert "guide_questions" in guide
            assert len(guide["guide_questions"]) == 3  # 各技法に3つの質問
    
    def test_session_notes_tracking(self) -> None:
        """セッションメモ追跡のテスト."""
        start_result = self.analyzer.start_session("メモテスト", "テスト状況")
        session_id = start_result["session_id"]
        
        # アイデア追加
        self.analyzer.apply_technique(session_id, "substitute", ["アイデア1"])
        
        # 評価
        evaluations = [{"idea": "アイデア1", "feasibility": 5, "impact": 5}]
        self.analyzer.evaluate_ideas(session_id, evaluations)
        
        # セッション取得してメモ確認
        result = self.analyzer.get_session(session_id)
        notes = result["session_notes"]
        
        assert len(notes) >= 2  # アイデア追加と評価のメモ
        assert any("アイデアを生成" in note for note in notes)
        assert any("評価" in note for note in notes)
    
    def test_comprehensive_scamper_workflow(self) -> None:
        """包括的なSCAMPERワークフローのテスト."""
        # 1. セッション開始
        start_result = self.analyzer.start_session("ワークフロー改善", "現在の業務プロセスが非効率")
        session_id = start_result["session_id"]
        
        # 2. 複数の技法でアイデア生成
        techniques_and_ideas = [
            ("substitute", ["手動処理を自動化", "Excel を専用システムに変更"]),
            ("eliminate", ["不要な承認プロセス削除", "重複作業の除去"]),
            ("combine", ["複数のツールを統合", "会議とレビューを同時実行"])
        ]
        
        for technique, ideas in techniques_and_ideas:
            result = self.analyzer.apply_technique(session_id, technique, ideas)
            assert result["success"] is True
        
        # 3. アイデア評価
        all_evaluations = [
            {"idea": "手動処理を自動化", "feasibility": 7, "impact": 9},
            {"idea": "Excel を専用システムに変更", "feasibility": 5, "impact": 8},
            {"idea": "不要な承認プロセス削除", "feasibility": 8, "impact": 7},
            {"idea": "重複作業の除去", "feasibility": 9, "impact": 6},
            {"idea": "複数のツールを統合", "feasibility": 6, "impact": 8},
            {"idea": "会議とレビューを同時実行", "feasibility": 8, "impact": 5}
        ]
        
        eval_result = self.analyzer.evaluate_ideas(session_id, all_evaluations)
        assert eval_result["success"] is True
        
        # 4. 最終セッション状況確認
        final_result = self.analyzer.get_session(session_id)
        assert final_result["total_ideas"] == 6
        technique_stats = final_result["technique_statistics"]
        used_techniques = sum(1 for stats in technique_stats.values() if stats["total_ideas"] > 0)
        assert used_techniques == 3
        
        # 5. トップアイデアが正しくランキングされているか確認
        top_idea = eval_result["top_ideas"][0]
        assert top_idea["total_score"] == 16  # feasibility(7) + impact(9)