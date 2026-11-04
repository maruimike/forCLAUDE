# ANA / JAL マイルの実質購買力（RPP）分析

航空マイルの「1マイル＝○円」という換算が、正規運賃（普通運賃・正規ビジネス運賃）を分子に置いた
**見せかけの換算価値**になっている問題を排除し、合理的な消費者が現金で同じ役務を調達する場合の
**実質購買力（Real Purchasing Power Parity）** を定量的に算出・検証するリポジトリです。

```
RPP [円/マイル] = ( V_real − E[C_cash] ) / M_effective
```

| 記号 | 意味 |
|---|---|
| `V_real` | 同区間・同等シートを現金で調達する場合の **現実的な代替最安価格**（早割・LCC・新幹線・ZIPAIR・外資系セール運賃）。往復・税込 |
| `C_cash` | 特典航空券の発券時に **別途現金で徴収される費用**（燃油サーチャージ・空港施設使用料・諸税）。特典枠が取れた経路でのみ発生 |
| `M_effective` | **実効必要マイル数**。「特典枠が取れる確率 p」で基本マイル、「1−p」でフォールバック経路（JAL 特典航空券PLUS、または ANA SKY コイン／e JALポイントで現金運賃を買う）のマイル数を加重した期待値 |

## リポジトリ構成

```
data/params/            モデルの入力パラメータ（CSV、出典IDつき）
data/observations/      JAL 特典航空券PLUS 倍率などの観測データ
data/sources.csv        出典一覧
src/rpp_model/          モデル本体（識別式・モンテカルロ・感応度・作図）
src/run_analysis.py     一括実行スクリプト
output/tables/          計算結果（CSV）
output/figures/         図（PNG）
output/model_digest.md  計算結果の自動ダイジェスト
reports/                最終レポート（日本語）
research_notes/         リサーチノート（出典つき一次情報の整理）
```

## 実行方法

```bash
pip install -r requirements.txt
python3 src/run_analysis.py            # data/params を読み、output/ に表と図を出力
python3 src/run_analysis.py --n 50000  # モンテカルロの試行回数を変更
```

## 需要帯（demand band）

| ID | 需要帯 | 定義 |
|---|---|---|
| D1 | 閑散平日昼 | 火曜・水曜の 10〜16 時発、閑散期 |
| D2 | 通常 | 通常期の平日、朝夕ピーク以外 |
| D3 | 高需要時間帯 | 金曜 18〜20 時発、月曜 7〜8 時発、日曜夕方発 |
| D4 | 繁忙期 | 3 連休・年末年始・GW・お盆 |

ANA のシーズン制（L/R/H）、JAL の特典航空券PLUS 倍率、特典枠の空席確率、現金運賃はすべてこの需要帯ごとに
パラメータ化されています。
