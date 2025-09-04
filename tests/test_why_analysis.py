"""5Why分析ツールのテスト."""

import pytest
from datetime import datetime

from analysis_support.tools.why_analysis import WhyAnalysis


class TestWhyAnalysis:
    """5Why分析のテストクラス."""
    
    def setup_method(self) -> None:
        """各テストメソッドの前に実行される初期化."""
        self.analyzer = WhyAnalysis()
    
    def test_start_analysis_basic(self) -> None:
        """基本的な分析開始のテスト."""
        problem = "システムが頻繁に停止する"
        result = self.analyzer.start_analysis(problem)
        
        assert result["success"] is True
        assert "analysis_id" in result
        assert len(result["analysis_id"]) == 8  # 8文字のUUID
        assert result["problem"] == problem
        assert "なぜ" in result["first_question"]
    
    def test_start_analysis_with_context(self) -> None:
        """コンテキスト付きの分析開始のテスト."""
        problem = "売上が減少している"
        context = "過去3ヶ月で売上が20%減少"
        result = self.analyzer.start_analysis(problem, context)
        
        assert result["success"] is True
        assert result["problem"] == problem
        # 内部データにcontextが保存されていることを確認
        analysis_id = result["analysis_id"]
        analysis_data = self.analyzer._analyses[analysis_id]
        assert analysis_data["context"] == context
    
    def test_add_answer_valid(self) -> None:
        """有効な回答追加のテスト."""
        # 分析開始
        problem = "プロジェクトが遅延している"
        start_result = self.analyzer.start_analysis(problem)
        analysis_id = start_result["analysis_id"]
        
        # 最初の回答
        answer = "リソースが不足しているから"
        result = self.analyzer.add_answer(analysis_id, 0, answer)
        
        assert result["success"] is True
        assert result["recorded_answer"] == answer
        assert "next_question" in result
        assert result["next_level"] == 1
        assert result["progress"] == "1/5"
    
    def test_add_answer_invalid_id(self) -> None:
        """無効な分析IDでの回答追加テスト."""
        result = self.analyzer.add_answer("invalid_id", 0, "テスト回答")
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_add_answer_invalid_level(self) -> None:
        """無効なレベルでの回答追加テスト."""
        # 分析開始
        start_result = self.analyzer.start_analysis("テスト問題")
        analysis_id = start_result["analysis_id"]
        
        # 無効なレベル
        result = self.analyzer.add_answer(analysis_id, 5, "テスト回答")
        assert result["success"] is False
        assert "無効です" in result["message"]
        
        result = self.analyzer.add_answer(analysis_id, -1, "テスト回答")
        assert result["success"] is False
        assert "無効です" in result["message"]
    
    def test_add_answer_duplicate(self) -> None:
        """重複回答のテスト."""
        # 分析開始と最初の回答
        start_result = self.analyzer.start_analysis("テスト問題")
        analysis_id = start_result["analysis_id"]
        
        answer = "テスト回答"
        self.analyzer.add_answer(analysis_id, 0, answer)
        
        # 同じレベルに再度回答
        result = self.analyzer.add_answer(analysis_id, 0, "別の回答")
        assert result["success"] is False
        assert "既に回答済み" in result["message"]
    
    def test_complete_5why_analysis(self) -> None:
        """完全な5Why分析のテスト."""
        # 分析開始
        start_result = self.analyzer.start_analysis("売上減少")
        analysis_id = start_result["analysis_id"]
        
        # 5つの回答を順次追加
        answers = [
            "競合他社の参入により市場シェアが減少した",
            "価格競争で優位性を失った",
            "製品の差別化が不十分だった",
            "市場調査が不適切だった",
            "顧客ニーズの変化を把握していなかった"
        ]
        
        for i, answer in enumerate(answers):
            result = self.analyzer.add_answer(analysis_id, i, answer)
            assert result["success"] is True
            
            if i < 4:
                # まだ完了していない
                assert "next_question" in result
                assert result["next_level"] == i + 1
            else:
                # 完了
                assert result["status"] == "completed"
                assert "summary" in result
    
    def test_get_analysis_valid(self) -> None:
        """有効な分析取得のテスト."""
        # 分析開始と1つの回答
        start_result = self.analyzer.start_analysis("テスト問題")
        analysis_id = start_result["analysis_id"]
        self.analyzer.add_answer(analysis_id, 0, "テスト回答")
        
        # 分析取得
        result = self.analyzer.get_analysis(analysis_id)
        
        assert result["success"] is True
        assert result["analysis_id"] == analysis_id
        assert result["problem"] == "テスト問題"
        assert result["status"] == "active"
        assert result["progress"] == "1/5"
        assert result["current_level"] == 1
    
    def test_get_analysis_invalid_id(self) -> None:
        """無効なIDでの分析取得テスト."""
        result = self.analyzer.get_analysis("invalid_id")
        
        assert result["success"] is False
        assert "見つかりません" in result["message"]
    
    def test_list_analyses_empty(self) -> None:
        """空の分析一覧テスト."""
        result = self.analyzer.list_analyses()
        
        assert result["success"] is True
        assert result["analyses"] == []
    
    def test_list_analyses_multiple(self) -> None:
        """複数の分析一覧テスト."""
        # 2つの分析を開始
        self.analyzer.start_analysis("問題1")
        self.analyzer.start_analysis("問題2")
        
        result = self.analyzer.list_analyses()
        
        assert result["success"] is True
        assert len(result["analyses"]) == 2
        # 分析が存在することを確認（順序は実装依存のため柔軟にチェック）
        problems = [analysis["problem"] for analysis in result["analyses"]]
        assert "問題1" in problems
        assert "問題2" in problems
    
    def test_summary_generation(self) -> None:
        """要約生成のテスト."""
        # 完全な5Why分析を実行
        start_result = self.analyzer.start_analysis("コードの品質が低い")
        analysis_id = start_result["analysis_id"]
        
        answers = [
            "レビュー体制が整っていない",
            "時間に余裕がない",
            "プロジェクト計画が甘い",
            "要件定義が不完全",
            "顧客との合意形成ができていない"
        ]
        
        # 5つの回答を追加
        for i, answer in enumerate(answers):
            result = self.analyzer.add_answer(analysis_id, i, answer)
        
        # 最後の結果に要約が含まれていることを確認
        assert "summary" in result
        summary = result["summary"]
        assert summary["original_problem"] == "コードの品質が低い"
        assert summary["root_cause"] == answers[-1]
        assert len(summary["why_chain"]) == 5
        assert summary["analysis_depth"] == "完全"
    
    def test_long_problem_truncation(self) -> None:
        """長い問題文の切り詰めテスト."""
        long_problem = "これは非常に長い問題文です。" * 10  # 30文字超
        self.analyzer.start_analysis(long_problem)
        
        result = self.analyzer.list_analyses()
        analysis = result["analyses"][0]
        
        # 30文字で切り詰められ、"..."が追加されることを確認
        assert len(analysis["problem"]) <= 30
        if len(long_problem) > 30:
            assert analysis["problem"].endswith("...")
    
    def test_analysis_timestamps(self) -> None:
        """タイムスタンプのテスト."""
        start_result = self.analyzer.start_analysis("タイムスタンプテスト")
        analysis_id = start_result["analysis_id"]
        
        # 分析データの作成時刻が正しく設定されているか確認
        analysis_data = self.analyzer._analyses[analysis_id]
        created_at = datetime.fromisoformat(analysis_data["created_at"])
        assert isinstance(created_at, datetime)
        
        # 回答追加時のタイムスタンプ
        self.analyzer.add_answer(analysis_id, 0, "テスト回答")
        why_data = analysis_data["whys"][0]
        timestamp = datetime.fromisoformat(why_data["timestamp"])
        assert isinstance(timestamp, datetime)