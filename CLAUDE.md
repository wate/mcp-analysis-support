プロジェクト概要
========================

このプロジェクトは、専門的分析手法をサポートするMCPサーバーです。`mcp-thinking-support`から分離され、5Why分析、MECE分析、SCAMPER法などの分析手法に特化しています。

必須事項
-------------------------

受け答えはすべて日本語で行います。

実装内容
-------------------------

### 5Why分析（WhyAnalysis）

- 問題の根本原因を特定するための5回の「なぜ」の繰り返しによる分析手法
- 4つのMCPツール: `why_analysis_start`, `why_analysis_add_answer`, `why_analysis_get`, `why_analysis_list`
- 8文字のUUIDを使用して分析セッションを管理

### MECE分析

- 相互排他（Mutually Exclusive）と網羅的（Collectively Exhaustive）の原則に基づく論理的構造化支援
- 2つのMCPツール: `mece_analyze_categories`, `mece_create_structure`
- フレームワーク: 4P, 3C, SWOT, 時系列, 内外要因, auto（自動選択）

### SCAMPER法

- 7つの技法による創造的思考支援（Substitute/代替、Combine/結合、Adapt/応用、Modify/変更、Put to other use/転用、Eliminate/除去、Reverse/逆転）
- 6つのMCPツール: セッション管理、技法適用、アイデア評価、包括的生成など
- フルUUIDを使用してセッションを管理、英語・日本語の技法名に対応

技術仕様
-------------------------

- 言語: Python 3.10+（型ヒント必須、mypy対応）
- フレームワーク: MCP SDK（Model Context Protocol）
- パッケージ管理: uv
- テスト: pytest + pytest-asyncio
- 型チェック: mypy
- Markdown: markdownlint設定済み

MCPツール一覧
-------------------------

1. `why_analysis_start` - 5Why分析の開始
2. `why_analysis_add_answer` - 質問への回答と次のWhy生成
3. `why_analysis_get` - 分析状況の取得
4. `why_analysis_list` - 全分析の一覧表示
5. `mece_analyze_categories` - カテゴリのMECE分析実行
6. `mece_create_structure` - MECE構造の提案
7. `scamper_start_session` - SCAMPER創造的思考セッション開始
8. `scamper_apply_technique` - 指定技法でのアイデア生成
9. `scamper_evaluate_ideas` - アイデアの実現可能性・インパクト評価
10. `scamper_get_session` - セッション状況取得
11. `scamper_list_sessions` - 全セッション一覧
12. `scamper_generate_comprehensive` - 全技法適用による包括的アイデア生成

開発・テスト
-------------------------

### コマンド

- `uv sync` - 依存関係インストール
- `uv run pytest -v` - テスト実行（全テストの成功が必須）
- `uv run mypy src/` - 型チェック（エラー0が必須）
- `uv run analysis-support` - MCPサーバー起動
- `uv run python -m analysis_support.server` - 開発モード実行

### テスト構成

- 5Why分析: 10テストケース（分析開始、回答追加、完全分析、エラーハンドリング等）
- MECE分析: 9テストケース（重複検出、漏れ検出、フレームワーク構造提案等）
- SCAMPER法: 22テストケース（セッション管理、技法適用、アイデア評価、日本語対応等）
- サーバー統合テスト
- エラーハンドリングテスト

全テストケース数: 74+（包括的なテスト網羅が必要）

実装基準
-------------------------

### 言語・ローカライゼーション

- すべてのユーザー向けメッセージは日本語
- 絵文字アイコンの活用（📋, ✅, 🎯, 💡等）
- SCAMPER技法の英語・日本語対応

### データ管理

- インメモリ辞書によるセッション永続化
- 8文字UUID（`str(uuid.uuid4())[:8]`）: 5Why・MECE分析
- フルUUID（`str(uuid.uuid4())`）: SCAMPERセッション
- ISO形式タイムスタンプ（`datetime.now().isoformat()`）

### エラーハンドリングパターン

- 無効ID: `"❌ [リソース]ID '[id]' が見つかりません"`
- パラメータ不正: 適切な日本語バリデーションメッセージ
- 状態不整合: 現在の状態に基づく適切なエラーメッセージ

### プロジェクト構造

```
src/analysis_support/
├── server.py              # MCPサーバーメイン
└── tools/
    ├── why_analysis.py    # 5Why分析実装
    ├── mece.py           # MECE分析実装
    └── scamper.py        # SCAMPER法実装
```

将来の拡張予定
-------------------------

- PMBOK RBS（Risk Breakdown Structure）: リスクの階層的分類構造
- m-SHELLモデル: 6要素分析（Machine, Software, Hardware, Environment, Liveware×2）
- フィッシュボーン図（特性要因図）
- パレート分析
- FMEA（Failure Mode and Effects Analysis）
- KJ法（親和図法）

開発方針
-------------------------

- セキュリティ重視: 防御的セキュリティタスクのみ対応
- 型安全性: Optional型を適切に使用、mypy互換性必須
- テスト駆動: 包括的なテスト網羅
- 日本語対応: UIと分析結果を日本語で提供
- 拡張性: 新しいフレームワーク・技法の追加容易性

コード品質管理
-------------------------

### Markdownlint設定

`.markdownlint.yml`で以下のルールを設定：

- 見出しスタイル: H1-H2はsetext記法、H3以降はatx記法
- 行長制限: 120文字まで
- 見出し周辺: 上下に空白行を1行ずつ配置
- リストインデント: ネスト時は4スペース
- 重複見出し: 同一レベル内での重複を禁止
- コードブロック: 言語指定を推奨（必須ではない）

重要な開発指針
-------------------------

- 要求されたことのみを実行し、それ以上でもそれ以下でもない
- 目標達成に絶対必要でない限り、新しいファイルは作成しない
- 新規作成よりも既存ファイルの編集を優先する
- 機能の追加や更新があった場合は、必ずテストを追加し、全体のテストを実行する
- 実装済みの機能がCLAUDE.mdおよびREADME.mdに正確に反映されていることを確認する
