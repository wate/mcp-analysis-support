"""5Why分析ツール実装."""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class WhyAnalysis:
    """5Why分析を管理するクラス."""
    
    def __init__(self) -> None:
        """5Why分析マネージャーを初期化."""
        self._analyses: Dict[str, Dict[str, Any]] = {}
    
    def start_analysis(self, problem: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        5Why分析を開始する.
        
        Args:
            problem: 分析したい問題や現象
            context: 問題の背景情報
            
        Returns:
            分析ID、問題、最初の質問を含む開始メッセージ
        """
        analysis_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().isoformat()
        
        analysis_data = {
            "id": analysis_id,
            "problem": problem,
            "context": context,
            "whys": [
                {
                    "level": 0,
                    "question": f"なぜ「{problem}」が起きているのですか？",
                    "answer": None,
                    "timestamp": created_at
                }
            ],
            "created_at": created_at,
            "status": "active"
        }
        
        self._analyses[analysis_id] = analysis_data
        
        return {
            "success": True,
            "message": f"📋 5Why分析を開始しました",
            "analysis_id": analysis_id,
            "problem": problem,
            "first_question": analysis_data["whys"][0].get("question", "") if isinstance(analysis_data["whys"], list) and len(analysis_data["whys"]) > 0 else "",
            "instructions": "最初の「なぜ」の質問に回答してください。回答後、次の「なぜ」が自動生成されます。"
        }
    
    def add_answer(self, analysis_id: str, level: int, answer: str) -> Dict[str, Any]:
        """
        5Why分析の質問に回答し、次のWhyを生成する.
        
        Args:
            analysis_id: 分析ID
            level: 回答するWhyのレベル（0から4）
            answer: 質問への回答
            
        Returns:
            記録された回答と次の質問（または完了サマリー）
        """
        if analysis_id not in self._analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }
        
        analysis = self._analyses[analysis_id]
        
        if level < 0 or level > 4:
            return {
                "success": False,
                "message": f"❌ レベル {level} は無効です。0から4の範囲で指定してください"
            }
        
        if level >= len(analysis["whys"]):
            return {
                "success": False,
                "message": f"❌ レベル {level} の質問が存在しません"
            }
        
        whys = analysis["whys"]
        if isinstance(whys, list) and level < len(whys) and isinstance(whys[level], dict):
            if whys[level].get("answer") is not None:
                return {
                    "success": False,
                    "message": f"❌ レベル {level} の質問には既に回答済みです"
                }
        
        # 回答を記録
        timestamp = datetime.now().isoformat()
        if isinstance(whys, list) and level < len(whys) and isinstance(whys[level], dict):
            whys[level]["answer"] = answer
            whys[level]["timestamp"] = timestamp
        
        # 次の質問を生成
        if level < 4:
            next_level = level + 1
            next_question = f"なぜ「{answer}」なのですか？"
            
            if isinstance(whys, list):
                whys.append({
                    "level": next_level,
                    "question": next_question,
                    "answer": None,
                    "timestamp": timestamp
                })
            
            return {
                "success": True,
                "message": f"✅ レベル {level} の回答を記録しました",
                "recorded_answer": answer,
                "next_question": next_question,
                "next_level": next_level,
                "progress": f"{level + 1}/5"
            }
        else:
            # 5Why分析完了
            analysis["status"] = "completed"
            summary = self._generate_summary(analysis)
            
            return {
                "success": True,
                "message": "🎯 5Why分析が完了しました！",
                "recorded_answer": answer,
                "summary": summary,
                "status": "completed"
            }
    
    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        5Why分析の現在の状況を取得する.
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            分析の詳細状況（進行状況、質問・回答一覧）
        """
        if analysis_id not in self._analyses:
            return {
                "success": False,
                "message": f"❌ 分析ID '{analysis_id}' が見つかりません"
            }
        
        analysis = self._analyses[analysis_id]
        
        # 進行状況を計算
        whys_data = analysis["whys"]
        if isinstance(whys_data, list):
            answered_count = sum(1 for why in whys_data if isinstance(why, dict) and why.get("answer") is not None)
        else:
            answered_count = 0
        progress = f"{answered_count}/5"
        
        # 現在の質問を特定
        current_question = None
        current_level = None
        whys = analysis["whys"]
        if isinstance(whys, list):
            for why in whys:
                if isinstance(why, dict) and why.get("answer") is None:
                    current_question = why.get("question")
                    current_level = why.get("level")
                    break
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "problem": analysis["problem"],
            "context": analysis["context"],
            "status": analysis["status"],
            "progress": progress,
            "current_question": current_question,
            "current_level": current_level,
            "whys": analysis["whys"],
            "created_at": analysis["created_at"]
        }
    
    def list_analyses(self) -> Dict[str, Any]:
        """
        すべての5Why分析の一覧を取得する.
        
        Returns:
            分析一覧（ID、問題概要、進捗、作成日）
        """
        analyses_list = []
        
        for analysis_id, analysis in self._analyses.items():
            whys_data = analysis["whys"]
            if isinstance(whys_data, list):
                answered_count = sum(1 for why in whys_data if isinstance(why, dict) and why.get("answer") is not None)
            else:
                answered_count = 0
            progress = f"{answered_count}/5"
            
            # 問題文を30文字で切り詰め
            problem_summary = analysis["problem"]
            if len(problem_summary) > 30:
                problem_summary = problem_summary[:27] + "..."
            
            analyses_list.append({
                "id": analysis_id,
                "problem": problem_summary,
                "status": analysis["status"],
                "progress": progress,
                "created_at": datetime.fromisoformat(analysis["created_at"]).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 作成日時の降順でソート
        analyses_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "message": f"📋 5Why分析一覧（{len(analyses_list)}件）",
            "analyses": analyses_list
        }
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        5Why分析の要約を生成する.
        
        Args:
            analysis: 分析データ
            
        Returns:
            分析要約
        """
        problem = analysis["problem"]
        whys_list = analysis["whys"]
        root_cause = "未特定"
        if (isinstance(whys_list, list) and len(whys_list) > 4 and 
            isinstance(whys_list[4], dict) and whys_list[4].get("answer")):
            root_cause = whys_list[4]["answer"]
        
        why_chain = []
        if isinstance(whys_list, list):
            for i, why in enumerate(whys_list[:5]):
                if isinstance(why, dict) and why.get("answer"):
                    why_chain.append({
                        "level": i,
                        "question": why.get("question", ""),
                        "answer": why["answer"]
                    })
        
        return {
            "original_problem": problem,
            "root_cause": root_cause,
            "why_chain": why_chain,
            "total_levels": len(why_chain),
            "analysis_depth": "完全" if len(why_chain) == 5 else f"部分的（{len(why_chain)}/5）"
        }