"""MCP Analysis Support Server の統合テスト."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from analysis_support.server import server, call_tool, list_tools


class TestAnalysisSupportServer:
    """Analysis Support Server の統合テストクラス."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """利用可能なツール一覧取得のテスト."""
        tools = await list_tools()
        
        assert len(tools) == 28  # 全MCPツール数
        
        # 各ツールカテゴリが含まれていることを確認
        tool_names = [tool.name for tool in tools]
        
        # 5Why分析ツール
        assert "why_analysis_start" in tool_names
        assert "why_analysis_add_answer" in tool_names
        assert "why_analysis_get" in tool_names
        assert "why_analysis_list" in tool_names
        
        # MECE分析ツール
        assert "mece_analyze_categories" in tool_names
        assert "mece_create_structure" in tool_names
        
        # 専用フレームワーク分析ツール
        assert "swot_analysis" in tool_names
        assert "4p_analysis" in tool_names
        assert "3c_analysis" in tool_names
        assert "timeline_analysis" in tool_names
        assert "internal_external_analysis" in tool_names
        
        # SCAMPER法ツール
        assert "scamper_start_session" in tool_names
        assert "scamper_apply_technique" in tool_names
        assert "scamper_evaluate_ideas" in tool_names
        assert "scamper_get_session" in tool_names
        assert "scamper_list_sessions" in tool_names
        assert "scamper_generate_comprehensive" in tool_names
        
        # PMBOK RBSツール
        assert "rbs_create_structure" in tool_names
        assert "rbs_identify_risks" in tool_names
        assert "rbs_evaluate_risks" in tool_names
        assert "rbs_get_analysis" in tool_names
        assert "rbs_list_analyses" in tool_names
        
        # m-SHELLモデルツール
        assert "mshell_create_analysis" in tool_names
        assert "mshell_analyze_element" in tool_names
        assert "mshell_analyze_interface" in tool_names
        assert "mshell_evaluate_system" in tool_names
        assert "mshell_get_analysis" in tool_names
        assert "mshell_list_analyses" in tool_names
    
    @pytest.mark.asyncio
    async def test_why_analysis_start_tool(self) -> None:
        """5Why分析開始ツールのテスト."""
        arguments = {
            "problem": "サーバーが頻繁にダウンする",
            "context": "ピーク時間帯に発生"
        }
        
        result = await call_tool("why_analysis_start", arguments)
        
        assert len(result) == 1
        assert result[0]["type"] == "text"
        
        # 結果を評価形式で解析
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        assert "analysis_id" in response_text
    
    @pytest.mark.asyncio
    async def test_why_analysis_workflow(self) -> None:
        """5Why分析の完全ワークフローテスト."""
        # 1. 分析開始
        start_args = {"problem": "製品の品質が低い"}
        start_result = await call_tool("why_analysis_start", start_args)
        
        # analysis_idを抽出（簡易実装）
        response_dict = eval(start_result[0]["text"])
        analysis_id = response_dict["analysis_id"]
        
        # 2. 回答追加
        answer_args = {
            "analysis_id": analysis_id,
            "level": 0,
            "answer": "テストプロセスが不十分だから"
        }
        answer_result = await call_tool("why_analysis_add_answer", answer_args)
        
        assert len(answer_result) == 1
        response_text = answer_result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        
        # 3. 分析状況取得
        get_args = {"analysis_id": analysis_id}
        get_result = await call_tool("why_analysis_get", get_args)
        
        assert len(get_result) == 1
        response_text = get_result[0]["text"]
        assert "progress" in response_text
        assert "1/5" in response_text
        
        # 4. 分析一覧取得
        list_result = await call_tool("why_analysis_list", {})
        
        assert len(list_result) == 1
        response_text = list_result[0]["text"]
        assert "analyses" in response_text
    
    @pytest.mark.asyncio
    async def test_mece_analyze_categories_tool(self) -> None:
        """MECEカテゴリ分析ツールのテスト."""
        arguments = {
            "topic": "マーケティング戦略",
            "categories": ["デジタル広告", "SNS", "インフルエンサー", "PR"]
        }
        
        result = await call_tool("mece_analyze_categories", arguments)
        
        assert len(result) == 1
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        assert "mece_evaluation" in response_text
    
    @pytest.mark.asyncio
    async def test_mece_create_structure_tool(self) -> None:
        """MECE構造提案ツールのテスト."""
        arguments = {
            "topic": "事業戦略",
            "framework": "SWOT"
        }
        
        result = await call_tool("mece_create_structure", arguments)
        
        assert len(result) == 1
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        assert "structure" in response_text
        assert "SWOT" in response_text
    
    @pytest.mark.asyncio
    async def test_scamper_workflow(self) -> None:
        """SCAMPERの完全ワークフローテスト."""
        # 1. セッション開始
        start_args = {
            "topic": "会議の効率化",
            "current_situation": "長時間の会議で生産性が低い",
            "context": "リモートワーク環境"
        }
        start_result = await call_tool("scamper_start_session", start_args)
        
        # session_idを抽出
        response_dict = eval(start_result[0]["text"])
        session_id = response_dict["session_id"]
        
        # 2. 技法適用
        apply_args = {
            "session_id": session_id,
            "technique": "substitute",
            "ideas": ["長時間会議を短時間複数回に分割", "全員参加を必要者のみ参加に変更"],
            "explanations": ["集中力向上のため", "関係者の時間節約のため"]
        }
        apply_result = await call_tool("scamper_apply_technique", apply_args)
        
        assert len(apply_result) == 1
        response_text = apply_result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        
        # 3. アイデア評価
        eval_args = {
            "session_id": session_id,
            "idea_evaluations": [
                {"idea": "長時間会議を短時間複数回に分割", "feasibility": 8, "impact": 7},
                {"idea": "全員参加を必要者のみ参加に変更", "feasibility": 9, "impact": 6}
            ]
        }
        eval_result = await call_tool("scamper_evaluate_ideas", eval_args)
        
        assert len(eval_result) == 1
        response_text = eval_result[0]["text"]
        assert "success" in response_text
        assert "evaluation_results" in response_text
        
        # 4. セッション状況取得
        get_args = {"session_id": session_id}
        get_result = await call_tool("scamper_get_session", get_args)
        
        assert len(get_result) == 1
        response_text = get_result[0]["text"]
        assert "total_ideas" in response_text
        
        # 5. セッション一覧取得
        list_result = await call_tool("scamper_list_sessions", {})
        
        assert len(list_result) == 1
        response_text = list_result[0]["text"]
        assert "sessions" in response_text
    
    @pytest.mark.asyncio
    async def test_scamper_comprehensive_generation(self) -> None:
        """SCAMPER包括的生成ツールのテスト."""
        arguments = {
            "topic": "商品パッケージの改良",
            "current_situation": "現在のパッケージは環境に優しくない",
            "context": "コスト制約あり"
        }
        
        result = await call_tool("scamper_generate_comprehensive", arguments)
        
        assert len(result) == 1
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
        assert "technique_prompts" in response_text
        assert "comprehensive_approach" in response_text
    
    @pytest.mark.asyncio
    async def test_invalid_tool_name(self) -> None:
        """無効なツール名のテスト."""
        result = await call_tool("invalid_tool_name", {})
        
        assert len(result) == 1
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "False" in response_text
        assert "未知のツール" in response_text
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self) -> None:
        """ツールエラーハンドリングのテスト."""
        # 無効なパラメータでツール実行
        invalid_args = {"invalid_param": "invalid_value"}
        result = await call_tool("why_analysis_start", invalid_args)
        
        assert len(result) == 1
        response_text = result[0]["text"]
        # エラーが適切に処理されていることを確認
        assert "エラー" in response_text or "error" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_japanese_technique_names(self) -> None:
        """日本語技法名対応のテスト."""
        # セッション開始
        start_args = {
            "topic": "日本語技法テスト",
            "current_situation": "テスト状況"
        }
        start_result = await call_tool("scamper_start_session", start_args)
        response_dict = eval(start_result[0]["text"])
        session_id = response_dict["session_id"]
        
        # 日本語技法名で適用
        apply_args = {
            "session_id": session_id,
            "technique": "代替",  # 日本語
            "ideas": ["テストアイデア"]
        }
        result = await call_tool("scamper_apply_technique", apply_args)
        
        assert len(result) == 1
        response_text = result[0]["text"]
        assert "success" in response_text
        assert "True" in response_text
    
    @pytest.mark.asyncio
    async def test_mece_auto_framework_selection(self) -> None:
        """MECE自動フレームワーク選択のテスト."""
        test_cases = [
            ("マーケティング戦略", "4P"),
            ("競合分析", "3C"),
            ("組織の強み", "SWOT"),
            ("変化の推移", "時系列"),
            ("一般的な課題", "内外")
        ]
        
        for topic, expected_framework in test_cases:
            arguments = {"topic": topic, "framework": "auto"}
            result = await call_tool("mece_create_structure", arguments)
            
            response_text = result[0]["text"]
            # フレームワークが適切に選択されていることを確認
            assert expected_framework in response_text
    
    @pytest.mark.asyncio
    async def test_cross_tool_integration(self) -> None:
        """複数ツール間の統合テスト."""
        # 1. 5Why分析で根本原因を特定
        why_start = await call_tool("why_analysis_start", {
            "problem": "顧客満足度が低下している"
        })
        why_response = eval(why_start[0]["text"])
        analysis_id = why_response["analysis_id"]
        
        # 回答を追加して根本原因まで進む
        answers = [
            "サービス品質が低下している",
            "スタッフの対応が悪い", 
            "研修が不十分",
            "研修予算が削減された",
            "業績悪化により予算圧縮"
        ]
        
        for level, answer in enumerate(answers):
            await call_tool("why_analysis_add_answer", {
                "analysis_id": analysis_id,
                "level": level,
                "answer": answer
            })
        
        # 2. MECE分析で解決策の分類
        mece_result = await call_tool("mece_create_structure", {
            "topic": "顧客満足度改善策",
            "framework": "4P"
        })
        
        # 3. SCAMPER法で創造的解決策を生成
        scamper_start = await call_tool("scamper_start_session", {
            "topic": "顧客満足度向上",
            "current_situation": "根本原因は予算不足による研修不足"
        })
        scamper_response = eval(scamper_start[0]["text"])
        session_id = scamper_response["session_id"]
        
        # 全ての分析ツールが正常に動作することを確認
        assert why_response["success"] is True
        mece_response = eval(mece_result[0]["text"])
        assert mece_response["success"] is True
        assert scamper_response["success"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self) -> None:
        """並行セッション処理のテスト."""
        # 複数の分析を同時実行
        why_session1 = await call_tool("why_analysis_start", {"problem": "問題1"})
        why_session2 = await call_tool("why_analysis_start", {"problem": "問題2"})
        
        scamper_session1 = await call_tool("scamper_start_session", {
            "topic": "課題1", "current_situation": "状況1"
        })
        scamper_session2 = await call_tool("scamper_start_session", {
            "topic": "課題2", "current_situation": "状況2"
        })
        
        # 各セッションが独立して動作することを確認
        why1_response = eval(why_session1[0]["text"])
        why2_response = eval(why_session2[0]["text"])
        scamper1_response = eval(scamper_session1[0]["text"])
        scamper2_response = eval(scamper_session2[0]["text"])
        
        # 全セッションのIDがユニークであることを確認
        ids = [
            why1_response["analysis_id"],
            why2_response["analysis_id"],
            scamper1_response["session_id"],
            scamper2_response["session_id"]
        ]
        assert len(ids) == len(set(ids))  # 重複なし
    
    def test_tool_schema_validation(self) -> None:
        """ツールスキーマ検証のテスト."""
        import asyncio
        tools = asyncio.run(list_tools())
        
        for tool in tools:
            # 各ツールに必要な属性があることを確認
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            
            # スキーマの基本構造確認
            schema = tool.inputSchema
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema
            
            # 必須パラメータがある場合の確認
            if "required" in schema:
                assert isinstance(schema["required"], list)