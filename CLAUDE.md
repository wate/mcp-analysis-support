プロジェクト概要
========================

このプロジェクトは、専門的分析手法をサポートするMCPサーバーです。

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

### MECE分析専用フレームワーク

- 主要分析フレームワークへの直接アクセス機能
- 5つの専用MCPツール: `swot_analysis`, `4p_analysis`, `3c_analysis`, `timeline_analysis`, `internal_external_analysis`
- MECEツールのframeworkパラメータ指定が不要でユーザビリティ向上

### SCAMPER法

- 7つの技法による創造的思考支援（Substitute/代替、Combine/結合、Adapt/応用、Modify/変更、Put to other use/転用、Eliminate/除去、Reverse/逆転）
- 6つのMCPツール: セッション管理、技法適用、アイデア評価、包括的生成など
- フルUUIDを使用してセッションを管理、英語・日本語の技法名に対応

### PMBOK RBS（Risk Breakdown Structure）

- プロジェクトリスク分類構造とカテゴリ別リスク識別支援
- 5つのMCPツール: 構造作成、リスク識別、評価マトリックス、分析取得、一覧表示
- 4カテゴリ（技術的、外部、組織、プロジェクト管理）×5段階評価でリスク管理

### m-SHELLモデル（ヒューマンファクター分析）

- 6要素（Machine、Software、Hardware、Environment、Liveware-Central、Liveware-Other）による分析
- 6つのMCPツール: 分析作成、要素分析、インターフェース分析、システム評価、取得、一覧
- 航空業界由来の分析手法でシステム障害要因を特定

技術仕様
-------------------------

- 言語: Python 3.10+（型ヒント必須、mypy対応）
- フレームワーク: MCP SDK（Model Context Protocol）
- パッケージ管理: uv
- テスト: pytest + pytest-asyncio
- 型チェック: mypy
- Markdown: markdownlint設定済み

MCPツール一覧（全28ツール）
-------------------------

### 5Why分析（4ツール）

1. `why_analysis_start` - 5Why分析の開始
2. `why_analysis_add_answer` - 質問への回答と次のWhy生成
3. `why_analysis_get` - 分析状況の取得
4. `why_analysis_list` - 全分析の一覧表示

### MECE分析（2ツール）

5. `mece_analyze_categories` - カテゴリのMECE分析実行
6. `mece_create_structure` - MECE構造の提案

### MECE専用フレームワーク（5ツール）

7. `swot_analysis` - SWOT分析（強み・弱み・機会・脅威）
8. `4p_analysis` - 4P分析（Product・Price・Place・Promotion）
9. `3c_analysis` - 3C分析（Customer・Competitor・Company）
10. `timeline_analysis` - 時系列分析（過去・現在・未来）
11. `internal_external_analysis` - 内外分析（内部要因・外部要因）

### SCAMPER法（6ツール）

12. `scamper_start_session` - SCAMPER創造的思考セッション開始
13. `scamper_apply_technique` - 指定技法でのアイデア生成
14. `scamper_evaluate_ideas` - アイデアの実現可能性・インパクト評価
15. `scamper_get_session` - セッション状況取得
16. `scamper_list_sessions` - 全セッション一覧
17. `scamper_generate_comprehensive` - 全技法適用による包括的アイデア生成

### PMBOK RBS（5ツール）

18. `rbs_create_structure` - プロジェクトリスク分類構造作成
19. `rbs_identify_risks` - カテゴリ別リスク識別支援
20. `rbs_evaluate_risks` - リスク評価マトリックス生成
21. `rbs_get_analysis` - RBS分析状況取得
22. `rbs_list_analyses` - 全RBS分析一覧

### m-SHELLモデル（6ツール）

23. `mshell_create_analysis` - m-SHELL分析開始
24. `mshell_analyze_element` - 特定要素分析
25. `mshell_analyze_interface` - 要素間インターフェース分析
26. `mshell_evaluate_system` - システム全体評価
27. `mshell_get_analysis` - m-SHELL分析状況取得
28. `mshell_list_analyses` - 全m-SHELL分析一覧

開発・テスト
-------------------------

### コマンド

- `uv sync` - 依存関係インストール
- `uv run pytest -v` - テスト実行（全テストの成功が必須）
- `uv run mypy src/` - 型チェック
- `uv run analysis-support` - MCPサーバー起動
- `uv run python -m analysis_support.server` - 開発モード実行

### テスト構成

- 各思考ツールの単体テスト
- サーバー統合テスト  
- エラーハンドリングテスト
- 型安全性テスト

全テストが成功し、実用可能な品質を保証済み。

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

### ❌ 絶対にやってはいけないこと

**テストを通すことが目的ではなく、仕様通りに実装されていることが最優先**

- テストが通らないからといって仕様を捻じ曲げてはならない
- テストの期待値を強引に書き換えてテストの意味をなくしてはならない
- 実装が間違っている場合は実装を修正し、テストが間違っている場合はテストを修正する
- テストは仕様の正しさを検証するためのものであり、テストのための実装変更は本末転倒である

### ✅ 正しいアプローチ

1. **仕様理解**: まず仕様を正確に理解する
2. **仕様通り実装**: 仕様に忠実に実装する
3. **仕様通りテスト**: 仕様の期待動作をテストで検証する
4. **不整合の修正**: テスト失敗時は仕様と実装のどちらが正しいかを判断し、正しい方に合わせる
