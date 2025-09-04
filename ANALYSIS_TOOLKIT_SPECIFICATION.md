分析系MCP実装仕様書
========================

本ドキュメントは、`mcp-analysis-support`として独立実装する分析系MCPの詳細仕様を記録しています。
PMBOKのRBS、m-SHELLモデル等の追加分析手法と合わせて実装する際の参考資料として使用してください。

## プロジェクト背景・分離の経緯

### 分離前の状況
- `mcp-thinking-support`は8つの思考方法（動的思考、段階的思考、クリティカル・シンキング、ロジカル・シンキング、5Why分析、MECE分析、弁証法、SCAMPER法）を統合したMCPサーバーでした
- 26個のMCPツール、74個のテストケースを有する大規模なシステムでした

### 分離の理由
1. **機能肥大化の懸念**: PMBOKのRBS、m-SHELLモデル等の専門分析手法を追加すると、本来の主目的（汎用的思考プロセス支援）から逸脱してしまう
2. **役割の明確化**: 汎用的思考プロセス vs 専門的分析手法という性質の違い
3. **保守性の向上**: 小さなコードベースによる管理のしやすさ
4. **用途別選択**: ユーザーが目的に応じて必要なMCPのみを選択可能

### 分離後の構成
- **`mcp-thinking-support`**: 5つの汎用的思考プロセス（sequential, stepwise, critical, logical, dialectical）
- **`mcp-analysis-support`**: 専門的分析手法（5Why, MECE, SCAMPER + 将来のRBS, m-SHELL等）

### 命名の統一性
両MCPは`mcp-[機能]-support`の命名規則で統一され、「支援」という共通コンセプトを持ちます。

実装対象ツール
-------------

### 1. 5Why分析（WhyAnalysis）

#### 概要

問題の根本原因を特定するための5回の「なぜ」の繰り返しによる分析手法

#### MCPツール仕様

##### 1.1 why_analysis_start

**説明**: 5Why分析を開始して根本原因を特定する
**入力パラメータ**:

- `problem` (string, 必須): 分析したい問題や現象
- `context` (string, オプション): 問題の背景情報

**出力**: 分析ID、問題、最初の質問を含む開始メッセージ

##### 1.2 why_analysis_add_answer

**説明**: 5Why分析の質問に回答し、次のWhyを生成する
**入力パラメータ**:

- `analysis_id` (string, 必須): 分析ID
- `level` (integer, 必須): 回答するWhyのレベル（0から4）
- `answer` (string, 必須): 質問への回答

**出力**: 記録された回答と次の質問（または完了サマリー）

##### 1.3 why_analysis_get

**説明**: 5Why分析の現在の状況を取得する
**入力パラメータ**:

- `analysis_id` (string, 必須): 分析ID

**出力**: 分析の詳細状況（進行状況、質問・回答一覧）

##### 1.4 why_analysis_list

**説明**: すべての5Why分析の一覧を取得する
**入力パラメータ**: なし
**出力**: 分析一覧（ID、問題概要、進捗、作成日）

#### 実装仕様

**主要クラス**: `WhyAnalysis`
**依存関係**: uuid, datetime, typing

**データ構造**:

```python
{
    "id": str,  # 8文字のUUID
    "problem": str,
    "context": str | None,
    "whys": [
        {
            "level": int,  # 0-4
            "question": str,
            "answer": str | None,
            "timestamp": str  # ISO format
        }
    ],
    "created_at": str,  # ISO format
    "status": "active" | "completed"
}
```

**主要メソッド**:

- `start_analysis(problem, context)`: 分析開始
- `add_answer(analysis_id, level, answer)`: 回答追加
- `get_analysis(analysis_id)`: 状況取得
- `list_analyses()`: 一覧取得
- `_generate_summary(analysis)`: 要約生成

#### テスト仕様

**テストファイル**: `test_why_analysis.py`
**テストカバレッジ**: 74テストケース中10テストケース

**主要テストケース**:

1. 分析開始テスト（コンテキスト有無）
2. 回答追加の連続テスト
3. 完全な5Why分析テスト
4. 分析状況取得テスト
5. 分析一覧テスト
6. エラーハンドリング（無効ID、重複回答）
7. 要約生成テスト
8. 進捗追跡テスト

---

### 2. MECE分析（MECE）

#### 概要

Mutually Exclusive（相互排他性）とCollectively Exhaustive（網羅性）の原則に基づく論理的構造化支援

#### MCPツール仕様

##### 2.1 mece_analyze_categories

**説明**: カテゴリのMECE分析を実行して重複や漏れを検証する
**入力パラメータ**:

- `topic` (string, 必須): 分析対象のトピック
- `categories` (array[string], 必須): 分析するカテゴリのリスト

**出力**: MECE評価、重複・漏れの検出、改善提案

##### 2.2 mece_create_structure

**説明**: トピックに対するMECE構造を提案する
**入力パラメータ**:

- `topic` (string, 必須): 構造を作成したいトピック
- `framework` (string, デフォルト: "auto"): 使用するフレームワーク
    - 選択肢: auto, 4P, 3C, SWOT, 時系列, 内外

**出力**: 提案されるMECE構造、各カテゴリの説明

#### 実装仕様

**主要クラス**: `MECE`, `MECEAnalysis`, `MECECategory`, `MECEViolationType`
**依存関係**: uuid, datetime, typing, enum

**データ構造**:

```python
class MECEViolationType(Enum):
    OVERLAP = "重複（相互排他性違反）"
    GAP = "漏れ（網羅性違反）"
    BOTH = "重複と漏れの両方"
    NONE = "MECE原則に適合"

class MECEAnalysis:
    id: str
    topic: str
    original_categories: List[str]
    mece_categories: List[MECECategory]
    violation_type: MECEViolationType
    overlaps: List[tuple]
    gaps: List[str]
    improvement_suggestions: List[str]
    analysis_notes: List[str]
    created_at: datetime
```

**フレームワーク対応**:

- 4P: Product, Price, Place, Promotion
- 3C: Customer, Competitor, Company
- SWOT: Strengths, Weaknesses, Opportunities, Threats
- 時系列: 過去, 現在, 未来
- 内外: 内部要因, 外部要因
- auto: トピックに応じた自動選択

**主要メソッド**:

- `analyze_categories(topic, categories)`: カテゴリ分析
- `create_mece_structure(topic, framework)`: 構造提案
- `_check_mece_violations(analysis)`: 違反チェック
- `_find_overlaps(categories)`: 重複検出
- `_find_gaps(topic, categories)`: 漏れ検出

#### テスト仕様

**テストファイル**: `test_mece.py`
**テストケース**:

1. 重複があるカテゴリの分析テスト
2. 漏れがあるカテゴリの分析テスト
3. MECE原則に適合するカテゴリの分析テスト
4. 各フレームワーク（4P, 3C, SWOT, 時系列, 内外）での構造提案テスト
5. 重複検出ロジックのテスト
6. 漏れ検出ロジックのテスト
7. 自動フレームワーク選択のテスト
8. 改善提案生成のテスト
9. カテゴリ説明生成のテスト

---

### 3. SCAMPER法（SCAMPER）

#### 概要

Substitute（代替）、Combine（結合）、Adapt（応用）、Modify（変更）、Put to other use（転用）、Eliminate（除去）、Reverse（逆転）の7つの技法による創造的思考支援

#### MCPツール仕様

##### 3.1 scamper_start_session

**説明**: SCAMPER創造的思考セッションを開始する
**入力パラメータ**:

- `topic` (string, 必須): 創造的思考を適用したいトピックや課題
- `current_situation` (string, 必須): 現在の状況や問題の詳細
- `context` (string, オプション): 背景情報や制約条件

**出力**: セッションID、技法概要、使い方ガイド

##### 3.2 scamper_apply_technique

**説明**: 指定されたSCAMPER技法でアイデアを生成する
**入力パラメータ**:

- `session_id` (string, 必須): SCAMPERセッションのID
- `technique` (string, 必須): 適用するSCAMPER技法
    - 選択肢: substitute/combine/adapt/modify/put_to_other_use/eliminate/reverse
    - 日本語対応: 代替/結合/応用/変更/転用/除去/逆転
- `ideas` (array[string], 必須): 生成したアイデアのリスト
- `explanations` (array[string], オプション): 各アイデアの説明

**出力**: 適用結果、技法ガイド、セッション統計

##### 3.3 scamper_evaluate_ideas

**説明**: 生成されたアイデアを実現可能性とインパクトで評価する
**入力パラメータ**:

- `session_id` (string, 必須): SCAMPERセッションのID
- `idea_evaluations` (array[object], 必須): アイデア評価のリスト
    - 各オブジェクト: `{idea: string, feasibility: integer(0-10), impact: integer(0-10)}`

**出力**: 評価結果、ランキング、技法別統計

##### 3.4 scamper_get_session

**説明**: SCAMPERセッションの現在の状況を取得する
**入力パラメータ**:

- `session_id` (string, 必須): SCAMPERセッションのID

**出力**: セッション概要、技法別統計、最新アイデア

##### 3.5 scamper_list_sessions

**説明**: すべてのSCAMPERセッションの一覧を取得する
**入力パラメータ**: なし
**出力**: セッション一覧（ID、トピック、アイデア数、日時）

##### 3.6 scamper_generate_comprehensive

**説明**: 全てのSCAMPER技法を適用して包括的なアイデアを生成する
**入力パラメータ**:

- `topic` (string, 必須): 創造的思考を適用したいトピックや課題
- `current_situation` (string, 必須): 現在の状況や問題の詳細
- `context` (string, オプション): 背景情報や制約条件

**出力**: 全技法適用結果、統計情報、次のステップ

#### 実装仕様

**主要クラス**: `SCAMPER`, `SCAMPERSession`, `SCAMPERIdea`, `SCAMPERTechnique`
**依存関係**: uuid, datetime, typing, enum

**データ構造**:

```python
class SCAMPERTechnique(Enum):
    SUBSTITUTE = "Substitute"
    COMBINE = "Combine"
    ADAPT = "Adapt"
    MODIFY = "Modify"
    PUT_TO_OTHER_USE = "Put to other use"
    ELIMINATE = "Eliminate"
    REVERSE = "Reverse"

class SCAMPERIdea:
    id: str
    technique: SCAMPERTechnique
    idea: str
    explanation: str
    feasibility_score: int  # 0-10
    impact_score: int      # 0-10
    created_at: datetime

class SCAMPERSession:
    id: str
    topic: str
    current_situation: str
    ideas: List[SCAMPERIdea]
    active_technique: Optional[SCAMPERTechnique]
    session_notes: List[str]
    created_at: datetime
    updated_at: datetime
```

**技法ガイダンス**:
各技法には3つの思考ガイド質問が定義されています：

- Substitute: 代替可能性、類似問題の解決方法
- Combine: 統合・組み合わせの可能性
- Adapt: 他分野のアイデア適用、自然界の模倣
- Modify: 拡大・縮小、強調・弱化
- Put to other use: 他用途への転用、副産物活用
- Eliminate: 削除・簡素化の可能性
- Reverse: 順序・役割の逆転

**主要メソッド**:

- `start_session(topic, current_situation, context)`: セッション開始
- `apply_technique(session_id, technique, ideas, explanations)`: 技法適用
- `evaluate_ideas(session_id, idea_evaluations)`: アイデア評価
- `get_session(session_id)`: セッション取得
- `list_sessions()`: セッション一覧
- `generate_comprehensive_ideas(topic, current_situation, context)`: 包括的生成

#### テスト仕様

**テストファイル**: `test_scamper.py`
**テストクラス**: `TestSCAMPER`
**テストケース数**: 22テストケース

**主要テストケース**:

1. セッション開始のテスト
2. 各技法（Substitute, Combine等）の適用テスト
3. 全技法の適用テスト
4. アイデア評価のテスト
5. セッション状況取得のテスト
6. セッション一覧取得のテスト
7. 包括的アイデア生成のテスト
8. エラーハンドリング（無効技法、無効セッションID）
9. 日本語技法名の対応テスト
10. セッションメモ追跡のテスト
11. 統計情報生成のテスト

---

## 共通実装パターン

### エラーハンドリング

- 無効なID: `"❌ [リソース]ID '[id]' が見つかりません"`
- パラメータ不正: 適切なバリデーションメッセージ
- 状態不整合: 現在の状態に基づく適切なエラーメッセージ

### UUID生成

- 短縮UUID: `str(uuid.uuid4())[:8]` （8文字）
- フルUUID: `str(uuid.uuid4())` （SCAMPER用）

### 日時処理

- ISO形式: `datetime.now().isoformat()`
- 表示形式: `datetime.strftime('%Y-%m-%d %H:%M:%S')`

### 日本語対応

- すべてのメッセージは日本語
- 絵文字アイコンの活用（📋, ✅, 🎯, 💡等）
- 技法の日英対応（SCAMPER）

### データ永続化

- インメモリ辞書による管理
- セッション間でのデータ保持
- 分析履歴の維持

## 技術要件

### 基盤技術スタック（mcp-thinking-supportと同一）

**言語・ランタイム:**
- Python 3.10+
- 型ヒント必須（mypy対応）
- async/await対応

**フレームワーク・ライブラリ:**
- MCP SDK（Model Context Protocol）
- パッケージ管理: uv
- テストフレームワーク: pytest + pytest-asyncio

**開発・品質管理ツール:**
- 型チェック: mypy
- Markdown: markdownlint設定済み
- コード品質: 防御的セキュリティタスクのみ対応

**プロジェクト構造:**
```
mcp-analysis-support/
├── src/analysis_support/
│   ├── server.py              # MCPサーバーメイン
│   └── tools/
│       ├── why_analysis.py    # 5Why分析
│       ├── mece.py           # MECE分析  
│       ├── scamper.py        # SCAMPER法
│       └── [新規分析手法]
├── tests/
│   ├── test_why_analysis.py
│   ├── test_mece.py
│   ├── test_scamper.py
│   └── test_server.py
├── pyproject.toml            # uv設定
├── CLAUDE.md                 # 開発指針
└── README.md                 # 利用ガイド
```

### 基本依存関係

```python
# 標準ライブラリ
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import logging
import asyncio

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server  
from mcp.types import Tool
```

### テスト環境

- pytest（単体テスト・統合テスト）
- pytest-asyncio（非同期テスト対応）
- フィクスチャベースのテスト設計
- テストカバレッジ: 各ツールの包括的テスト

## 実装時の注意点

1. **型安全性**: Optional型を適切に使用
2. **エラーハンドリング**: ユーザーフレンドリーなメッセージ
3. **パフォーマンス**: 大量データ処理時の考慮
4. **国際化**: 日本語メッセージの統一
5. **拡張性**: 新しいフレームワーク・技法の追加容易性

## 開発・運用コマンド（mcp-thinking-supportと同一）

```bash
# 依存関係インストール  
uv sync

# テスト実行（全テストの成功が必須）
uv run pytest -v

# 型チェック（エラー0が必須）
uv run mypy src/

# MCPサーバー起動
uv run analysis-support

# 開発モードで実行
uv run python -m analysis_support.server
```

## 品質基準（mcp-thinking-supportと同一）

### Markdownlint設定
`.markdownlint.yml`で以下のルールを適用:
- 見出しスタイル: H1-H2はsetext記法、H3以降はatx記法
- 行長制限: 120文字まで
- 見出し周辺: 上下に空白行を1行ずつ配置
- リストインデント: ネスト時は4スペース

### 開発方針
- 要求されたことのみを実行し、それ以上でもそれ以下でもない
- 目標達成に絶対必要でない限り、新しいファイルは作成しない
- 新規作成よりも既存ファイルの編集を優先する
- 機能の追加や更新があった場合は、必ずテストを追加し、全体のテストを実行する
- 実装済みの機能がCLAUDE.mdおよびREADME.mdに正確に反映されていることを確認する

このドキュメントを参考に、`mcp-analysis-support`として独立したMCPサーバーを実装してください。

## 追加実装予定の分析手法

### PMBOK RBS（Risk Breakdown Structure）

- リスクの階層的分類構造
- カテゴリ別リスク識別支援
- リスク評価マトリックス

### m-SHELLモデル

- Machine、Software、Hardware、Environment、Liveware、Livewareの6要素分析
- 航空業界由来のヒューマンファクター分析手法
- システム障害の要因分析支援

### その他の分析手法（将来実装候補）

- フィッシュボーン図（特性要因図）
- パレート分析
- FMEA（Failure Mode and Effects Analysis）
- KJ法（親和図法）
