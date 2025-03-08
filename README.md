# Sepsis X Bot

自動的に敗血症データの更新をX（Twitter）に投稿するAWS CDKプロジェクトです。毎日日本時間の午前10時に、その日の敗血症データへのリンクを含むメッセージが投稿されます。

## 概要

このプロジェクトは以下のAWSサービスを使用しています：

- **AWS Lambda**: X（Twitter）への投稿を実行
- **AWS EventBridge**: 毎日定時に実行するためのスケジューリング
- **AWS Secrets Manager**: X API認証情報の安全な保管
- **AWS CDK**: インフラストラクチャをコードとして定義

## 前提条件

- AWS CLI がインストールされ、適切に設定されていること
- Python 3.9 以上
- AWS CDK v2
- X（Twitter）デベロッパーアカウントとAPI認証情報

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone [repository-url]
cd sepsis_x_project
```

### 2. 環境変数の設定

`.env` ファイルを作成し、以下の内容を設定します：

```
# AWS Configuration
AWS_ACCOUNT_ID=あなたのAWSアカウントID
AWS_REGION=ap-northeast-1
```

### 3. X API認証情報の設定

AWS Secrets Managerに以下の形式でシークレットを作成します：

1. AWS Management Consoleにログイン
2. Secrets Managerに移動
3. 「新しいシークレットを保存」を選択
4. 「その他のタイプのシークレット」を選択
5. 以下のキーと値のペアを追加：
   - `api_key`: あなたのX API Key
   - `api_key_secret`: あなたのX API Key Secret
   - `access_token`: あなたのX Access Token
   - `access_token_secret`: あなたのX Access Token Secret
   - `bearer_token`: あなたのX Bearer Token
6. シークレット名を `twitter-api-keys` として保存

### 4. 依存関係のインストール

```bash
# CDK依存関係のインストール
pip install -r requirements.txt

# Lambda Layer用の依存関係準備
chmod +x build_layer.sh
./build_layer.sh
```

### 5. デプロイ

```bash
cdk bootstrap
cdk deploy
```

## プロジェクト構造

```
sepsis_x_project/
├── .env                          # 環境変数
├── app.py                        # CDKアプリケーションエントリーポイント
├── requirements.txt              # CDKプロジェクト用依存関係
├── requirements-lambda.txt       # Lambda Layer用依存関係
├── build_layer.sh                # Lambdaレイヤーを構築するスクリプト
├── lambda/                       # Lambda関数コード
│   └── twitter_bot.py            # メインLambda関数
├── lambda_layer/                 # build_layer.shによって作成される
└── sepsis_x/                     # CDK Stackディレクトリ
    ├── __init__.py
    └── sepsis_x_stack.py         # CDK Stack定義
```

## 投稿フォーマット

毎日投稿されるメッセージのフォーマットは以下の通りです：

```
本日の敗血症
https://www.sepsis-search.com/articles?date=YYYY-MM-DD
```

日付は日本時間の現在の日付（YYYY-MM-DD形式）で自動的に設定されます。

## カスタマイズ

- 投稿の内容を変更する場合は、`lambda/twitter_bot.py` ファイルの `post_to_twitter` 関数内の `message` 変数を編集します。
- 投稿時間を変更する場合は、`sepsis_x/sepsis_x_stack.py` ファイル内の `daily_schedule` 定義のcron式を修正します。

## トラブルシューティング

- Lambda関数の実行ログはCloudWatchで確認できます。
- 認証エラーが発生する場合は、Secrets Managerの認証情報が正しく設定されているか確認してください。
- スケジュールの問題がある場合は、EventBridgeのルールを確認してください。

## ライセンス

[ライセンス情報]
