# Raspberry Pi 4画面表示システム

このリポジトリは書籍で紹介しているサンプルコードです。

## ■ 概要
Raspberry Piを使用して、テレビ画面に複数の情報を同時表示するシステムです。

## ■ ファイル説明

### quad.html
画面を4分割して表示するHTMLです。

### start_quad.sh
Chromiumを全画面で起動するスクリプトです。

### schedule.html
スケジュールを表示する画面です。

### update_schedule_api.py
Googleカレンダーから予定を取得します。

## ■ 使い方

1. Raspberry Piにファイルをコピー
2. 以下を実行

```bash
bash start_quad.sh
