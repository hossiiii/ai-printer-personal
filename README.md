# 🖨️ AI Printer - 音声からドキュメント生成システム

音声入力からAIを活用して高品質なドキュメントを自動生成し、PDFとして出力できるWebアプリケーションです。

## 📋 概要

AI Printerは、音声録音からAIによる文字起こしと文書生成を行い、美しいデザインのちらしや案内書をPDFで出力できるシステムです。OpenAIの最新技術を活用し、直感的なWebインターフェースで簡単に利用できます。

### 🎯 主な機能

- **🎤 音声録音・文字起こし**: Web Audio APIとOpenAI Whisperによる高精度な音声認識
- **🤖 AI文書生成**: ChatGPT-4o-latestを使用した自然で魅力的な文書作成
- **📝 リアルタイムプレビュー**: HTMLとCSSによる美しいドキュメントプレビュー
- **📄 PDF出力**: 日本語対応のReportLabによる高品質PDF生成
- **✏️ 文書修正**: 音声またはテキストによる文書の編集・改善
- **🌐 多言語対応**: 日本語・英語に対応したユーザーインターフェース
- **💾 ファイル履歴**: 生成した文書の管理と再ダウンロード機能

### 🛠️ 技術スタック

**バックエンド:**
- FastAPI (Python 3.11)
- OpenAI API (GPT-4o-latest, Whisper)
- ReportLab (PDF生成)
- BeautifulSoup4 (HTML解析)
- SQLAlchemy (データベース)
- Redis (キャッシュ)

**フロントエンド:**
- React 18 with TypeScript
- Vite (ビルドツール)
- Material-UI (コンポーネント)
- React i18next (国際化)
- Web Audio API (音声録音)

**インフラ:**
- Docker & Docker Compose
- PostgreSQL
- Redis

## 🚀 ローカル環境セットアップ

### 前提条件

以下のソフトウェアがインストールされている必要があります：

- **Docker** (20.10.0以上)
- **Docker Compose** (2.0.0以上)
- **Git**

### 1. リポジトリのクローン

```bash
git clone https://github.com/hossiiii/ai-printer-personal.git
cd ai-printer-personal
```

### 2. 環境変数の設定

`.env.development`ファイルを編集し、必要なAPI keyを設定します：

```bash
# OpenAI API キーを設定（必須）
OPENAI_API_KEY=your_openai_api_key_here

# モデル設定（推奨）
OPENAI_MODEL=chatgpt-4o-latest
WHISPER_MODEL=whisper-1

# Google Drive連携（オプション）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 3. Dockerコンテナの起動

```bash
# すべてのサービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 4. アプリケーションにアクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

### 5. 開発環境の確認

```bash
# サービス状態の確認
docker-compose ps

# バックエンドのヘルスチェック
curl http://localhost:8000/health

# フロントエンドのアクセス確認
curl http://localhost:3000
```

## 💻 使用方法

### 基本的な使い方

1. **音声録音**: 「録音開始」ボタンを押して音声を録音
2. **文字起こし**: 録音停止後、自動的にWhisperが文字起こしを実行
3. **文書生成**: 文字起こしテキストからAIが適切な文書を生成
4. **プレビュー確認**: 生成された文書をリアルタイムでプレビュー
5. **PDF出力**: 「PDF生成」ボタンでPDFファイルをダウンロード

### 文書の修正

- **テキスト修正**: 修正指示を入力して「修正」ボタンをクリック
- **音声修正**: 音声で修正指示を録音して適用

### 対応文書タイプ

- イベント案内・告知
- 会議資料・議事録
- 商品・サービス紹介
- お知らせ・通知文書

## 🔧 開発者向け情報

### プロジェクト構造

```
ai-printer-personal/
├── backend/                 # FastAPIバックエンド
│   ├── app/
│   │   ├── api/            # APIルート
│   │   ├── services/       # ビジネスロジック
│   │   ├── models/         # データモデル
│   │   └── config.py       # 設定
│   ├── tests/              # テストファイル
│   └── Dockerfile
├── frontend/               # React + Viteフロントエンド
│   ├── src/
│   │   ├── components/     # Reactコンポーネント
│   │   ├── services/       # API通信
│   │   ├── types/          # TypeScript型定義
│   │   └── i18n/          # 国際化
│   ├── public/
│   └── Dockerfile
├── docker-compose.yml      # Docker設定
└── README.md
```

### API エンドポイント

主要なAPIエンドポイント：

- `POST /api/transcribe` - 音声ファイルの文字起こし
- `POST /api/generate-document` - 文書生成
- `POST /api/revise-document` - 文書修正
- `POST /api/generate-pdf` - PDF生成
- `GET /api/download/{filename}` - ファイルダウンロード

### 開発コマンド

```bash
# 開発環境の起動
docker-compose up -d

# ログの確認
docker-compose logs -f backend
docker-compose logs -f frontend

# コンテナに入る
docker-compose exec backend bash
docker-compose exec frontend sh

# テストの実行
docker-compose exec backend python -m pytest

# 型チェック
docker-compose exec frontend npm run lint
```

### 環境設定詳細

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `OPENAI_API_KEY` | OpenAI APIキー | 必須 |
| `OPENAI_MODEL` | 使用するGPTモデル | `chatgpt-4o-latest` |
| `WHISPER_MODEL` | 音声認識モデル | `whisper-1` |
| `VITE_API_URL` | バックエンドAPI URL | `http://localhost:8000` |
| `REDIS_URL` | Redis接続URL | `redis://localhost:6380/0` |

## 🤝 貢献

プロジェクトへの貢献を歓迎します：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🆘 トラブルシューティング

### よくある問題

**Q: OpenAI API keyエラーが発生する**
A: `.env.development`ファイルで正しいAPI keyが設定されているか確認してください。

**Q: Dockerコンテナが起動しない**
A: ポートの競合を確認してください。特にポート3000, 8000, 6380が使用されていないか確認。

**Q: PDF生成に失敗する**
A: 日本語フォントが正しくインストールされているか確認してください。

**Q: 音声録音ができない**
A: ブラウザでマイクの許可が与えられているか確認してください。HTTPSまたはlocalhostでのみ動作します。

### ログの確認

```bash
# 全体のログ
docker-compose logs -f

# 特定のサービス
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis
docker-compose logs -f postgres
```

### サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。