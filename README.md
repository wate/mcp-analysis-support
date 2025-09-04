分析支援MCPサーバー
=========================

> **注記**: このリポジトリのすべてのコードはClaude Codeによって生成されました。

専門的分析手法をサポートするMCPサーバーです。

- **5Why分析**: 問題の根本原因を特定するための5回の「なぜ」の繰り返し分析
- **MECE分析**: 相互排他・網羅的原則による論理的構造化支援（専用フレームワークツール付き）
- **SCAMPER法**: 7つの技法による創造的思考支援（代替、結合、応用、変更、転用、除去、逆転）
- **PMBOK RBS**: プロジェクトリスク分類構造とカテゴリ別リスク識別支援
- **m-SHELLモデル**: 6要素によるヒューマンファクター分析（航空業界由来）

インストール
-------------------------

```bash
uv sync
```

使用方法
-------------------------

### MCPサーバーとして起動

```bash
uv run analysis-support
```

### 利用可能なツール

#### 5Why分析（WhyAnalysis）

- `why_analysis_start`: 5Why分析を開始して根本原因を特定
- `why_analysis_add_answer`: 質問への回答と次のWhy生成
- `why_analysis_get`: 分析の現在状況を取得
- `why_analysis_list`: すべての5Why分析の一覧表示

#### MECE分析

- `mece_analyze_categories`: カテゴリのMECE分析実行（重複・漏れ検証）
- `mece_create_structure`: トピックに対するMECE構造提案
    - フレームワーク対応: 4P, 3C, SWOT, 時系列, 内外要因, auto（自動選択）

#### SCAMPER法

- `scamper_start_session`: SCAMPER創造的思考セッション開始
- `scamper_apply_technique`: 指定技法でのアイデア生成
    - 技法: substitute/代替, combine/結合, adapt/応用, modify/変更, put_to_other_use/転用, eliminate/除去, reverse/逆転
- `scamper_evaluate_ideas`: アイデアの実現可能性・インパクト評価
- `scamper_get_session`: セッション状況取得
- `scamper_list_sessions`: 全セッション一覧
- `scamper_generate_comprehensive`: 全技法適用による包括的アイデア生成

設定方法
-------------------------

### VSCode設定

VSCodeでMCPサーバーとして使用するには、`.vscode/mcp.json`ファイルを作成：

```json
{
  "servers": {
    "analysis-support": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "analysis-support"
      ],
      "cwd": "/path/to/mcp-analysis-support"
    }
  }
}
```

### Claude Desktop設定

Claude Desktopで使用するには、設定ファイルに以下を追加：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "analysis-support": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-analysis-support",
        "analysis-support"
      ]
    }
  }
}
```

**注意**: `cwd`のパスは実際のプロジェクトディレクトリに変更してください。

開発
-------------------------

```bash
# 依存関係のインストール
uv sync

# 全テストの実行（コミット前に必須）
uv run pytest -v

# 型チェック（エラー0必須）
uv run mypy src/

# 開発モードで実行
uv run python -m analysis_support.server
```
