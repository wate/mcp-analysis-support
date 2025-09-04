"""MCP Analysis Support Server."""

import asyncio
from typing import Any, Dict, List
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from mcp.server.models import InitializationOptions

from .tools.why_analysis import WhyAnalysis
from .tools.mece import MECE
from .tools.scamper import SCAMPER


# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# サーバー初期化  
server: Server = Server("analysis-support")

# 分析ツール初期化
why_analyzer = WhyAnalysis()
mece_analyzer = MECE()
scamper_analyzer = SCAMPER()

# MCPツール定義
TOOLS = [
    # 5Why分析ツール
    Tool(
        name="why_analysis_start",
        description="5Why分析を開始して根本原因を特定する",
        inputSchema={
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "分析したい問題や現象"
                },
                "context": {
                    "type": "string",
                    "description": "問題の背景情報（オプション）"
                }
            },
            "required": ["problem"]
        }
    ),
    Tool(
        name="why_analysis_add_answer",
        description="5Why分析の質問に回答し、次のWhyを生成する",
        inputSchema={
            "type": "object",
            "properties": {
                "analysis_id": {
                    "type": "string",
                    "description": "分析ID"
                },
                "level": {
                    "type": "integer",
                    "description": "回答するWhyのレベル（0から4）"
                },
                "answer": {
                    "type": "string",
                    "description": "質問への回答"
                }
            },
            "required": ["analysis_id", "level", "answer"]
        }
    ),
    Tool(
        name="why_analysis_get",
        description="5Why分析の現在の状況を取得する",
        inputSchema={
            "type": "object",
            "properties": {
                "analysis_id": {
                    "type": "string",
                    "description": "分析ID"
                }
            },
            "required": ["analysis_id"]
        }
    ),
    Tool(
        name="why_analysis_list",
        description="すべての5Why分析の一覧を取得する",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    
    # MECE分析ツール
    Tool(
        name="mece_analyze_categories",
        description="カテゴリのMECE分析を実行して重複や漏れを検証する",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "分析対象のトピック"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "分析するカテゴリのリスト"
                }
            },
            "required": ["topic", "categories"]
        }
    ),
    Tool(
        name="mece_create_structure",
        description="トピックに対するMECE構造を提案する",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "構造を作成したいトピック"
                },
                "framework": {
                    "type": "string",
                    "description": "使用するフレームワーク",
                    "enum": ["auto", "4P", "3C", "SWOT", "時系列", "内外"],
                    "default": "auto"
                }
            },
            "required": ["topic"]
        }
    ),
    
    # SCAMPER法ツール
    Tool(
        name="scamper_start_session",
        description="SCAMPER創造的思考セッションを開始する",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "創造的思考を適用したいトピックや課題"
                },
                "current_situation": {
                    "type": "string",
                    "description": "現在の状況や問題の詳細"
                },
                "context": {
                    "type": "string",
                    "description": "背景情報や制約条件（オプション）"
                }
            },
            "required": ["topic", "current_situation"]
        }
    ),
    Tool(
        name="scamper_apply_technique",
        description="指定されたSCAMPER技法でアイデアを生成する",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "SCAMPERセッションのID"
                },
                "technique": {
                    "type": "string",
                    "description": "適用するSCAMPER技法",
                    "enum": ["substitute", "combine", "adapt", "modify", "put_to_other_use", "eliminate", "reverse", "代替", "結合", "応用", "変更", "転用", "除去", "逆転"]
                },
                "ideas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "生成したアイデアのリスト"
                },
                "explanations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "各アイデアの説明（オプション）"
                }
            },
            "required": ["session_id", "technique", "ideas"]
        }
    ),
    Tool(
        name="scamper_evaluate_ideas",
        description="生成されたアイデアを実現可能性とインパクトで評価する",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "SCAMPERセッションのID"
                },
                "idea_evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "idea": {"type": "string"},
                            "feasibility": {"type": "integer", "minimum": 0, "maximum": 10},
                            "impact": {"type": "integer", "minimum": 0, "maximum": 10}
                        },
                        "required": ["idea", "feasibility", "impact"]
                    },
                    "description": "アイデア評価のリスト"
                }
            },
            "required": ["session_id", "idea_evaluations"]
        }
    ),
    Tool(
        name="scamper_get_session",
        description="SCAMPERセッションの現在の状況を取得する",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "SCAMPERセッションのID"
                }
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="scamper_list_sessions",
        description="すべてのSCAMPERセッションの一覧を取得する",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="scamper_generate_comprehensive",
        description="全てのSCAMPER技法を適用して包括的なアイデアを生成する",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "創造的思考を適用したいトピックや課題"
                },
                "current_situation": {
                    "type": "string",
                    "description": "現在の状況や問題の詳細"
                },
                "context": {
                    "type": "string",
                    "description": "背景情報や制約条件（オプション）"
                }
            },
            "required": ["topic", "current_situation"]
        }
    )
]


@server.list_tools()
async def list_tools() -> List[Tool]:
    """利用可能なツールのリストを返す."""
    logger.info(f"Listing {len(TOOLS)} available analysis tools")
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ツール呼び出しを処理する."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        # 5Why分析ツール
        if name == "why_analysis_start":
            result = why_analyzer.start_analysis(
                arguments["problem"],
                arguments.get("context")
            )
        elif name == "why_analysis_add_answer":
            result = why_analyzer.add_answer(
                arguments["analysis_id"],
                arguments["level"],
                arguments["answer"]
            )
        elif name == "why_analysis_get":
            result = why_analyzer.get_analysis(arguments["analysis_id"])
        elif name == "why_analysis_list":
            result = why_analyzer.list_analyses()
        
        # MECE分析ツール
        elif name == "mece_analyze_categories":
            result = mece_analyzer.analyze_categories(
                arguments["topic"],
                arguments["categories"]
            )
        elif name == "mece_create_structure":
            result = mece_analyzer.create_mece_structure(
                arguments["topic"],
                arguments.get("framework", "auto")
            )
        
        # SCAMPER法ツール
        elif name == "scamper_start_session":
            result = scamper_analyzer.start_session(
                arguments["topic"],
                arguments["current_situation"],
                arguments.get("context", "")
            )
        elif name == "scamper_apply_technique":
            result = scamper_analyzer.apply_technique(
                arguments["session_id"],
                arguments["technique"],
                arguments["ideas"],
                arguments.get("explanations")
            )
        elif name == "scamper_evaluate_ideas":
            result = scamper_analyzer.evaluate_ideas(
                arguments["session_id"],
                arguments["idea_evaluations"]
            )
        elif name == "scamper_get_session":
            result = scamper_analyzer.get_session(arguments["session_id"])
        elif name == "scamper_list_sessions":
            result = scamper_analyzer.list_sessions()
        elif name == "scamper_generate_comprehensive":
            result = scamper_analyzer.generate_comprehensive_ideas(
                arguments["topic"],
                arguments["current_situation"],
                arguments.get("context", "")
            )
        
        else:
            result = {
                "success": False,
                "message": f"❌ 未知のツール: {name}"
            }
        
        logger.info(f"Tool {name} executed successfully")
        return [{"type": "text", "text": str(result)}]
    
    except Exception as e:
        error_message = f"❌ ツール実行エラー: {str(e)}"
        logger.error(f"Tool execution error: {e}")
        return [{"type": "text", "text": error_message}]


async def main() -> None:
    """サーバーのメイン実行関数."""
    logger.info("Starting Analysis Support MCP Server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server started successfully")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())