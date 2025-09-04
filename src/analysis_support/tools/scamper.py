"""SCAMPER法ツール実装."""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from enum import Enum


class SCAMPERTechnique(Enum):
    """SCAMPER技法の種類."""
    SUBSTITUTE = "Substitute"
    COMBINE = "Combine"
    ADAPT = "Adapt"
    MODIFY = "Modify"
    PUT_TO_OTHER_USE = "Put to other use"
    ELIMINATE = "Eliminate"
    REVERSE = "Reverse"


class SCAMPERIdea:
    """SCAMPERアイデアクラス."""
    
    def __init__(
        self, 
        idea_id: str, 
        technique: SCAMPERTechnique, 
        idea: str, 
        explanation: str = ""
    ):
        self.id = idea_id
        self.technique = technique
        self.idea = idea
        self.explanation = explanation
        self.feasibility_score: Optional[int] = None
        self.impact_score: Optional[int] = None
        self.created_at = datetime.now()


class SCAMPERSession:
    """SCAMPERセッションクラス."""
    
    def __init__(self, session_id: str, topic: str, current_situation: str, context: str = ""):
        self.id = session_id
        self.topic = topic
        self.current_situation = current_situation
        self.context = context
        self.ideas: List[SCAMPERIdea] = []
        self.active_technique: Optional[SCAMPERTechnique] = None
        self.session_notes: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class SCAMPER:
    """SCAMPER法を管理するクラス."""
    
    def __init__(self) -> None:
        """SCAMPER法マネージャーを初期化."""
        self._sessions: Dict[str, SCAMPERSession] = {}
        self._technique_guides = self._initialize_technique_guides()
        self._technique_mapping = self._initialize_technique_mapping()
    
    def start_session(
        self, 
        topic: str, 
        current_situation: str, 
        context: str = ""
    ) -> Dict[str, Any]:
        """
        SCAMPER創造的思考セッションを開始する.
        
        Args:
            topic: 創造的思考を適用したいトピックや課題
            current_situation: 現在の状況や問題の詳細
            context: 背景情報や制約条件
            
        Returns:
            セッションID、技法概要、使い方ガイド
        """
        session_id = str(uuid.uuid4())
        session = SCAMPERSession(session_id, topic, current_situation, context)
        self._sessions[session_id] = session
        
        return {
            "success": True,
            "message": "💡 SCAMPER創造的思考セッションを開始しました",
            "session_id": session_id,
            "topic": topic,
            "techniques_overview": {
                "Substitute (代替)": "何かを別のものに置き換えて改善できないか考える",
                "Combine (結合)": "異なる要素を組み合わせて新しい価値を創造できないか考える", 
                "Adapt (応用)": "他の分野のアイデアを適用できないか考える",
                "Modify (変更)": "形、大きさ、強度などを変更して改善できないか考える",
                "Put to other use (転用)": "他の用途や目的に転用できないか考える",
                "Eliminate (除去)": "不要な部分を取り除いて簡素化できないか考える",
                "Reverse (逆転)": "順序や役割を逆にして新しい視点を得られないか考える"
            },
            "usage_guide": [
                "1つの技法を選んで、その視点からアイデアを生成してください",
                "各技法には3つのガイド質問があります",
                "アイデアが浮かんだら apply_technique でセッションに記録してください",
                "最終的に evaluate_ideas でアイデアを評価できます"
            ]
        }
    
    def apply_technique(
        self, 
        session_id: str, 
        technique: str, 
        ideas: List[str], 
        explanations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        指定されたSCAMPER技法でアイデアを生成する.
        
        Args:
            session_id: SCAMPERセッションのID
            technique: 適用するSCAMPER技法
            ideas: 生成したアイデアのリスト
            explanations: 各アイデアの説明
            
        Returns:
            適用結果、技法ガイド、セッション統計
        """
        if session_id not in self._sessions:
            return {
                "success": False,
                "message": f"❌ セッションID '{session_id}' が見つかりません"
            }
        
        # 技法名を正規化
        normalized_technique = self._normalize_technique(technique)
        if not normalized_technique:
            valid_techniques = list(self._technique_mapping.keys())
            return {
                "success": False,
                "message": f"❌ 技法 '{technique}' は無効です。有効な技法: {', '.join(valid_techniques)}"
            }
        
        session = self._sessions[session_id]
        session.active_technique = normalized_technique
        session.updated_at = datetime.now()
        
        # アイデアを記録
        if explanations is None:
            explanations = [""] * len(ideas)
        
        added_ideas = []
        for i, idea in enumerate(ideas):
            idea_id = str(uuid.uuid4())
            explanation = explanations[i] if i < len(explanations) else ""
            scamper_idea = SCAMPERIdea(idea_id, normalized_technique, idea, explanation)
            session.ideas.append(scamper_idea)
            added_ideas.append({
                "id": idea_id,
                "idea": idea,
                "explanation": explanation
            })
        
        # セッションノート更新
        note = f"{normalized_technique.value}技法で{len(ideas)}個のアイデアを生成"
        session.session_notes.append(note)
        
        return {
            "success": True,
            "message": f"✅ {normalized_technique.value}技法で{len(ideas)}個のアイデアを記録しました",
            "technique": normalized_technique.value,
            "added_ideas": added_ideas,
            "technique_guide": self._technique_guides[normalized_technique],
            "session_stats": self._get_session_stats(session)
        }
    
    def evaluate_ideas(
        self, 
        session_id: str, 
        idea_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成されたアイデアを実現可能性とインパクトで評価する.
        
        Args:
            session_id: SCAMPERセッションのID
            idea_evaluations: アイデア評価のリスト
            
        Returns:
            評価結果、ランキング、技法別統計
        """
        if session_id not in self._sessions:
            return {
                "success": False,
                "message": f"❌ セッションID '{session_id}' が見つかりません"
            }
        
        session = self._sessions[session_id]
        
        # アイデアに評価を適用
        evaluated_ideas = []
        for evaluation in idea_evaluations:
            idea_text = evaluation["idea"]
            feasibility = evaluation["feasibility"]
            impact = evaluation["impact"]
            
            # 該当するアイデアを検索
            for idea in session.ideas:
                if idea.idea == idea_text:
                    idea.feasibility_score = feasibility
                    idea.impact_score = impact
                    evaluated_ideas.append({
                        "idea": idea.idea,
                        "technique": idea.technique.value,
                        "feasibility": feasibility,
                        "impact": impact,
                        "total_score": feasibility + impact
                    })
                    break
        
        # ランキング作成（合計スコア順）
        evaluated_ideas.sort(key=lambda x: x["total_score"], reverse=True)
        
        # 技法別統計
        technique_stats = self._calculate_technique_stats(session)
        
        session.updated_at = datetime.now()
        session.session_notes.append(f"{len(evaluated_ideas)}個のアイデアを評価")
        
        return {
            "success": True,
            "message": f"📊 {len(evaluated_ideas)}個のアイデアを評価しました",
            "evaluation_results": evaluated_ideas,
            "top_ideas": evaluated_ideas[:5],
            "technique_statistics": technique_stats,
            "evaluation_summary": {
                "total_evaluated": len(evaluated_ideas),
                "avg_feasibility": sum(idea["feasibility"] for idea in evaluated_ideas) / len(evaluated_ideas) if evaluated_ideas else 0,
                "avg_impact": sum(idea["impact"] for idea in evaluated_ideas) / len(evaluated_ideas) if evaluated_ideas else 0
            }
        }
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        SCAMPERセッションの現在の状況を取得する.
        
        Args:
            session_id: SCAMPERセッションのID
            
        Returns:
            セッション概要、技法別統計、最新アイデア
        """
        if session_id not in self._sessions:
            return {
                "success": False,
                "message": f"❌ セッションID '{session_id}' が見つかりません"
            }
        
        session = self._sessions[session_id]
        
        # 最新アイデア（最新5件）
        recent_ideas = sorted(session.ideas, key=lambda x: x.created_at, reverse=True)[:5]
        recent_ideas_data = [
            {
                "idea": idea.idea,
                "technique": idea.technique.value,
                "explanation": idea.explanation,
                "evaluated": idea.feasibility_score is not None and idea.impact_score is not None
            }
            for idea in recent_ideas
        ]
        
        return {
            "success": True,
            "session_id": session_id,
            "topic": session.topic,
            "current_situation": session.current_situation,
            "context": session.context,
            "total_ideas": len(session.ideas),
            "technique_statistics": self._calculate_technique_stats(session),
            "recent_ideas": recent_ideas_data,
            "session_notes": session.session_notes,
            "created_at": session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": session.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def list_sessions(self) -> Dict[str, Any]:
        """
        すべてのSCAMPERセッションの一覧を取得する.
        
        Returns:
            セッション一覧（ID、トピック、アイデア数、日時）
        """
        sessions_list = []
        
        for session_id, session in self._sessions.items():
            # トピックを30文字で切り詰め
            topic_summary = session.topic
            if len(topic_summary) > 30:
                topic_summary = topic_summary[:27] + "..."
            
            sessions_list.append({
                "id": session_id,
                "topic": topic_summary,
                "total_ideas": len(session.ideas),
                "techniques_used": len(set(idea.technique for idea in session.ideas)),
                "created_at": session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": session.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 更新日時の降順でソート
        sessions_list.sort(key=lambda x: str(x["updated_at"]), reverse=True)
        
        return {
            "success": True,
            "message": f"💡 SCAMPERセッション一覧（{len(sessions_list)}件）",
            "sessions": sessions_list
        }
    
    def generate_comprehensive_ideas(
        self, 
        topic: str, 
        current_situation: str, 
        context: str = ""
    ) -> Dict[str, Any]:
        """
        全てのSCAMPER技法を適用して包括的なアイデアを生成する.
        
        Args:
            topic: 創造的思考を適用したいトピックや課題
            current_situation: 現在の状況や問題の詳細
            context: 背景情報や制約条件
            
        Returns:
            全技法適用結果、統計情報、次のステップ
        """
        session_id = str(uuid.uuid4())
        session = SCAMPERSession(session_id, topic, current_situation, context)
        self._sessions[session_id] = session
        
        # 各技法のガイド質問を提供
        technique_prompts = {}
        for technique in SCAMPERTechnique:
            technique_prompts[technique.value] = self._technique_guides[technique]
        
        return {
            "success": True,
            "message": "🎯 包括的SCAMPER分析セッションを開始しました",
            "session_id": session_id,
            "topic": topic,
            "current_situation": current_situation,
            "technique_prompts": technique_prompts,
            "comprehensive_approach": [
                "各技法（S-C-A-M-P-E-R）について順番に考えてください",
                "それぞれの技法で2-3個のアイデアを出すことを目標にしてください",
                "各アイデアにはなぜそのアイデアが有効かの説明を加えてください",
                "全ての技法を試した後、evaluate_ideas でベストアイデアを選択してください"
            ],
            "next_steps": "apply_technique を使って、各技法ごとにアイデアを記録してください"
        }
    
    def _initialize_technique_guides(self) -> Dict[SCAMPERTechnique, Dict[str, Any]]:
        """技法ガイドを初期化する."""
        return {
            SCAMPERTechnique.SUBSTITUTE: {
                "name_jp": "代替",
                "description": "何かを別のものに置き換える",
                "guide_questions": [
                    "何を他のものと置き換えられますか？",
                    "どの材料や要素を代替できますか？",
                    "他の場所や時間に置き換えられますか？"
                ]
            },
            SCAMPERTechnique.COMBINE: {
                "name_jp": "結合",
                "description": "異なる要素を組み合わせる",
                "guide_questions": [
                    "どの要素を組み合わせられますか？",
                    "どのプロセスを統合できますか？",
                    "どの機能を一つにまとめられますか？"
                ]
            },
            SCAMPERTechnique.ADAPT: {
                "name_jp": "応用",
                "description": "他のアイデアを適用する",
                "guide_questions": [
                    "他の分野で似たような問題はどう解決されていますか？",
                    "自然界から学べることはありますか？",
                    "過去の成功例を参考にできますか？"
                ]
            },
            SCAMPERTechnique.MODIFY: {
                "name_jp": "変更",
                "description": "形や属性を変更する",
                "guide_questions": [
                    "何を拡大または縮小できますか？",
                    "何を強調または弱化できますか？",
                    "形や色を変えられますか？"
                ]
            },
            SCAMPERTechnique.PUT_TO_OTHER_USE: {
                "name_jp": "転用",
                "description": "他の用途に転用する",
                "guide_questions": [
                    "他にどんな用途がありますか？",
                    "副産物を活用できますか？",
                    "別の市場で使えますか？"
                ]
            },
            SCAMPERTechnique.ELIMINATE: {
                "name_jp": "除去",
                "description": "不要な部分を除去する",
                "guide_questions": [
                    "何を削除または除去できますか？",
                    "どの機能を簡素化できますか？",
                    "どの手順を省略できますか？"
                ]
            },
            SCAMPERTechnique.REVERSE: {
                "name_jp": "逆転",
                "description": "順序や役割を逆転する",
                "guide_questions": [
                    "順序を逆にできますか？",
                    "役割を交換できますか？",
                    "逆の視点から考えるとどうですか？"
                ]
            }
        }
    
    def _initialize_technique_mapping(self) -> Dict[str, SCAMPERTechnique]:
        """技法名のマッピングを初期化する."""
        mapping = {}
        for technique in SCAMPERTechnique:
            # 英語名（完全一致とlower case）
            mapping[technique.value.lower()] = technique
            mapping[technique.value] = technique
            
            # アンダースコア区切りのバリエーション
            underscore_version = technique.value.lower().replace(" ", "_")
            mapping[underscore_version] = technique
            
            # 日本語名
            guide = self._technique_guides[technique]
            mapping[guide["name_jp"]] = technique
        
        return mapping
    
    def _normalize_technique(self, technique: str) -> Optional[SCAMPERTechnique]:
        """技法名を正規化する."""
        technique_lower = technique.lower()
        return self._technique_mapping.get(technique_lower) or self._technique_mapping.get(technique)
    
    def _get_session_stats(self, session: SCAMPERSession) -> Dict[str, Any]:
        """セッション統計を取得する."""
        technique_counts: Dict[str, int] = {}
        for idea in session.ideas:
            technique_name = idea.technique.value
            technique_counts[technique_name] = technique_counts.get(technique_name, 0) + 1
        
        return {
            "total_ideas": len(session.ideas),
            "techniques_used": len(technique_counts),
            "technique_distribution": technique_counts
        }
    
    def _calculate_technique_stats(self, session: SCAMPERSession) -> Dict[str, Any]:
        """技法別統計を計算する."""
        technique_stats: Dict[str, Dict[str, Any]] = {}
        
        for technique in SCAMPERTechnique:
            ideas = [idea for idea in session.ideas if idea.technique == technique]
            
            evaluated_ideas = [idea for idea in ideas if idea.feasibility_score is not None]
            
            stats: Dict[str, Any] = {
                "total_ideas": len(ideas),
                "evaluated_ideas": len(evaluated_ideas)
            }
            
            if evaluated_ideas:
                feasibility_scores = [idea.feasibility_score for idea in evaluated_ideas if idea.feasibility_score is not None]
                impact_scores = [idea.impact_score for idea in evaluated_ideas if idea.impact_score is not None]
                stats["avg_feasibility"] = sum(feasibility_scores) / len(feasibility_scores) if feasibility_scores else 0
                stats["avg_impact"] = sum(impact_scores) / len(impact_scores) if impact_scores else 0
                stats["avg_total_score"] = stats["avg_feasibility"] + stats["avg_impact"]
            else:
                stats["avg_feasibility"] = 0
                stats["avg_impact"] = 0
                stats["avg_total_score"] = 0
            
            technique_stats[technique.value] = stats
        
        return technique_stats