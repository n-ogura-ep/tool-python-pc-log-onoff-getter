# tool-python-pc-log-onoff-getter

## 概要

Windows 端末のイベントログから、指定した開始日〜現在までの「PCログオン・ログオフ」の記録を
日毎に抽出し、CSVファイルとして出力するツールです。GUI（Tkinter）を使って開始日を入力するだけで、
簡単にログを取得できます。

出力される `logon_off.csv` には、日付ごとに以下の情報がまとめられます。

- `date`: 日付
- `logon`: その日最初のログオン時刻
- `logoff`: その日最後のログオフ時刻
- `operating_time`: 稼働時間（ログオン〜ログオフの差分から、昼休み1時間を差し引いた時間）

## 動作の仕組み

1. Windows の `wevtutil` コマンドでシステムイベントログ（EventID 7001: ログオン, 7002: ログオフ）を取得
2. 取得したログをテキスト整形し、一時CSVへ変換
3. 「カスタマー エクスペリエンス向上プログラムのユーザー ログオン/ログオフ通知」の行のみ抽出
4. 指定した開始日〜現在日時の範囲でフィルタリング
5. 日付ごとに最も早いログオン時刻・最も遅いログオフ時刻・稼働時間を算出し、CSVへ保存
6. 一時ファイル（`log.txt`, `log.csv`）を削除

## 必要環境

- OS: Windows（`wevtutil` コマンドに依存するため Windows 専用）
- Python >= 3.13
- パッケージ管理: [uv](https://docs.astral.sh/uv/)

## セットアップ

```powershell
# 依存パッケージのインストール
uv sync
```

## 使い方

### GUIで実行する場合

```powershell
uv run python app.py
```

起動したウィンドウに開始日を `2022 11 1` のようにスペース区切りで入力し、
「ログ取得開始」ボタンを押すと、`log_output/logon_off.csv` に結果が保存されます。

### CLIで実行する場合

```powershell
uv run python pc_log_on_off.py
```

プロンプトが表示されるので、開始日をスペース区切り（例: `2022 11 1`）で入力してください。

## 出力先

実行時のカレントディレクトリ配下に `log_output/` フォルダが作成され、
その中に `logon_off.csv` が出力されます。

## 開発者向け情報（メンテナンス）

- Host OS: Windows
- Python: >= 3.13
- パッケージ管理は **uv** を使用すること
- Lint / Format は **ruff** を使用すること

```powershell
# Lint
uv run ruff check .

# Format
uv run ruff format .
```

### プロジェクト構成

| ファイル | 役割 |
| --- | --- |
| `app.py` | Tkinter による GUI エントリーポイント |
| `pc_log_on_off.py` | ログオン・ログオフ抽出のコアロジック（CLI実行も可能） |
| `pyproject.toml` | プロジェクト定義・依存パッケージ管理（uv） |

### 注意事項

- `wevtutil` に依存しているため、Windows以外の環境では動作しません。
- イベントログの文字コードは `cp932` を前提としています。
- 稼働時間の算出時に昼休み（1時間）を一律で差し引く仕様のため、必要に応じてロジックの見直しを検討してください。
