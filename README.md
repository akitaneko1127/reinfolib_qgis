# ReinfoLib for QGIS

不動産情報ライブラリAPIをQGISから直接利用するためのプラグインです。

## 機能

- 不動産取引価格・地価公示・地価調査データの取得
- 用途地域・都市計画区域などの都市計画情報
- 学校・医療機関・福祉施設などの周辺施設情報
- 洪水・土砂災害・津波などの防災情報
- GeoPackage、GeoJSON、Shapefile、CSV形式での出力

## 必要条件

- QGIS 3.28 以降
- インターネット接続
- 不動産情報ライブラリAPIキー（無料）

## インストール

### QGIS公式リポジトリから（推奨）

1. QGISを開く
2. プラグイン → プラグインの管理とインストール
3. 「ReinfoLib」を検索
4. インストールをクリック

### ZIPファイルから

1. [Releases](https://github.com/linkfield/reinfolib-qgis/releases)から最新版をダウンロード
2. プラグイン → プラグインの管理とインストール → ZIPからインストール
3. ダウンロードしたZIPファイルを選択

## APIキーの取得

1. [不動産情報ライブラリAPI](https://www.reinfolib.mlit.go.jp/help/apiManual/)にアクセス
2. 利用規約に同意
3. 必要事項を入力して申請
4. メールでAPIキーを受け取る

## 使い方

1. Webメニュー → ReinfoLib → 設定 を開く
2. APIキーを入力して保存
3. Webメニュー → ReinfoLib → データ取得 を開く
4. 取得したいデータを選択
5. 範囲を指定
6. 「データ取得」をクリック

## 対応API

### 価格情報
- 不動産価格情報（XIT001）
- 不動産価格ポイント（XPT001）
- 地価公示・地価調査ポイント（XPT002）
- 鑑定評価書情報（XCT001）

### 都市計画
- 都市計画区域/区域区分（XKT001）
- 用途地域（XKT002）
- 立地適正化計画（XKT003）
- 防火・準防火地域（XKT014）

### 周辺施設
- 小学校区（XKT004）
- 中学校区（XKT005）
- 学校（XKT006）
- 保育園・幼稚園等（XKT007）
- 医療機関（XKT010）
- 福祉施設（XKT011）
- 駅別乗降客数（XKT015）

### 防災情報
- 洪水浸水想定区域（XKT026）
- 高潮浸水想定区域（XKT027）
- 土砂災害警戒区域（XKT029）
- 指定緊急避難場所（XGT001）

## ライセンス

GPL-3.0 License

## 開発者

Link Field  
Email: info@linkfield.co.jp

## サポート

- [GitHub Issues](https://github.com/linkfield/reinfolib-qgis/issues)
- Email: info@linkfield.co.jp
