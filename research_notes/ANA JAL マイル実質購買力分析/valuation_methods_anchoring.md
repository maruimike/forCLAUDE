# マイル価値の算定方法論と「見せかけの換算価値」の構造 — マイラーサイトのアンカリング、航空会社公式の換算レート、会計上のマイル負債単価、海外の評価手法（2026年11月4日時点）

> **調査方法上の制約（必読）**
> - 本セッションでは外部サイトへの直接アクセス（WebFetch / curl）がプロキシ側のポリシーで全ホスト拒否（HTTP 403 / DNS不解決）され、**記事本文・PDF本文を一次ソースのまま読むことができなかった**。取得できたのは検索エンジン（WebSearch 拡張モード）が返す要約と引用スニペットのみである。
> - そのため、下表の数値は「検索要約が当該URLに帰属させた引用」を転記したものであり、**計算式の完全な原文転記はできていない**。帰属が要約上あいまいなものは「出典未確定」と明記した。
> - 追加検索は、本ターンの検索上限（200回/ターン、全エージェント共有）に達したため途中で打ち切られた（JAL国内線運賃、国際線正規運賃表、ANA/JAL 有報のマイレージ注記、NerdWallet/Point.me、米系3社の breakage、DOT調査の2025年以降の状況、消費者庁・公取委の見解は**未検索または未取得**）。フォローアップのメッセージで続行可能。
> - 全行の「取得日」は 2026-11-04。「掲載日」は要約・URL・タイトルから判明した範囲で記載し、不明なものは「不明」とした。

## KQ1. マイラーブログ／比較サイト／YouTubeが提示する「1マイルの価値」の実例と、その計算式（分子・分母・燃油諸税・空席確率）

### Takeaway
日本語圏の「1マイル＝○円」は、ほぼ例外なく **「（現金で買った場合の運賃）÷（必要マイル数）」** の単純比で作られており、分子には国際線ファースト／ビジネスの往復運賃（正規運賃相当の高額例：欧州ファースト約295万円、NYファースト約257万〜280万円）、分母にはローシーズン最低必要マイル（例：165,000マイル、150,000マイル）が置かれるため、15〜20円という上限値が「マイルの価値」として流通する。燃油サーチャージ・諸税を控除するサイト、空席確率に言及するサイトは少数派で、2026年版の記事でも「国内線1.5〜4円／国際線ビジネス5〜10円超／ファースト10〜20円」というレンジ表示が定着している。

### Cited Findings

#### 1-A. サイト別一覧（提示値・計算式・前提）

列：No. | サイト（記事名） | 提示値（円/マイル） | 分子（運賃の種類） | 分母（必要マイル・シーズン） | 燃油・諸税控除 | 空席確率 | 片道/往復 | 掲載日 | 出典URL | 帰属の確度

| No. | サイト（記事名） | 提示値（円/マイル） | 分子（運賃の種類） | 分母（必要マイル・シーズン） | 燃油・諸税控除 | 空席確率 | 片道/往復 | 掲載日 | 出典URL | 帰属の確度 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | rikei-miler.com「マイルの価値は2円という理解で正しいのか」 | 約2.14円（国内線） | 羽田－沖縄往復「普通に購入する場合は約30,000円」（記事表現は「普通に購入」。金額水準から**普通運賃ではなく割引運賃と推定**＝推定） | 14,000マイル（往復。旧ANA国内線Lシーズン水準） | 国内線のため燃油なし。税込か不明 | 考慮なし（ただし「早期割引運賃と特典航空券では変更の可否など使い勝手が大きく違う」「割の悪い路線では2円を下回る」と留保） | 往復 | 不明 | https://rikei-miler.com/mile/post-32/ | 高（要約が記事本文を直接引用） |
| 2 | romulus-k-anaume.net「1マイル＝約2円の価値は本当か？マイル単価の真実」 | （数値未取得） | 「普通運賃と比べるか期間限定運賃と比べるかで単価が大きく違う」と指摘 | — | — | — | — | 2016-09-20（URLより） | https://www.romulus-k-anaume.net/entry/2016-09-20-060600 | 中 |
| 3 | dietmiler.com「マイルの価値を徹底解説。1ANAマイルは一体何円なのか？」 | ファースト 17.87円（約295万円÷165,000）、17.66円（2,915,000円÷165,000）、15.34円（2,915,000円÷190,000）；ビジネス 5〜9円（別記事では7〜8円） | 欧州（フランクフルト）往復ファーストクラス運賃（正規ファースト運賃相当と推定） | 165,000マイル（Lシーズン）／190,000マイル（ハイシーズン） | 控除の言及なし（＝未控除と推定） | 考慮なし | 往復 | 2018-03（URL「201803」より推定） | https://dietmiler.com/201803mile ／ https://dietmiler.com/201805mile3 | 高 |
| 4 | burio-kyonomanabi.com「1ANAマイルが『15円以上』⁈」 | 1.7円（SKYコイン最大）〜15円以上（特典航空券）；同ブログ別記事では「280万円÷15万マイル＝約18円/マイル」 | 成田⇆NY ファースト相当の推定運賃（280万円） | 150,000マイル（Lシーズン往復） | 「諸経費（燃料サーチャージや空港使用料等）が別途必要」と明記＝**控除せず** | 考慮なし | 往復 | 不明 | https://burio-kyonomanabi.com/anamile/ ／ https://burio-kyonomanabi.com/mile-skycoin/ | 高 |
| 5 | news.akirax.online「ANAマイルの価値はいくら？1マイル単価・特典航空券【2026年版】」 | 商品交換 約0.3〜0.8円／SKYコイン 約1.0〜1.7円／国内線特典 約1.5〜4円／国際線エコノミー 約2〜5円／国際線ビジネス 約5〜10円以上 | 「現金航空券価格÷必要マイル数」（運賃種別の指定なし） | 不明 | 不明 | 不明 | 不明 | 2026-05-04 | https://news.akirax.online/2026/05/04/ana-mile-value-best-use-flight/ | 高 |
| 6 | abtem.hateblo.jp「【2026年最新】JALマイルは何円の価値？」 | 普段は1.5〜2円で考える／特典航空券で3円以上／「特典航空券PLUS」で必要マイル増時は1円前後／e JALポイント1.5円が下支え／Amazonギフトは1万マイル→8,000円相当 | 現金運賃（種別不明） | 基本マイル／PLUS変動マイルの両方に言及 | 「燃油サーチャージや税金を差し引くと実質価値は下がる」と言及 | PLUS（空席連動）に言及 | 不明 | 2026年（記事名） | https://abtem.hateblo.jp/entry/jal-mile-value-yen-conversion-guide | 高 |
| 7 | 価格.comマガジン「1マイルが約10円相当に！これだからJALマイラーはやめられない」 | 約10円（JAL 約11万マイルでパリ往復ビジネス特典） | 同旅程の現金運賃（往復100万円前後。正規か割引か不明） | 約110,000マイル（往復） | 控除なし（要約の概算では「税金や燃油代を差し引くとさらに下がる」） | 考慮なし | 往復 | 2024年夏の旅程（約2年前） | https://kakakumag.com/money/?id=21323 | 高 |
| 8 | The Goal（matsunosuke.jp）「JALマイルの使い方 2026」 | 国内線普通席 1.5〜2円／国際線ビジネス 2.5〜6円／国際線ファースト 7〜16円／実際の発券例 13.95円 | 現金運賃（種別不明） | 不明 | 不明 | 不明 | 不明 | 2026年版 | https://matsunosuke.jp/jal-mile-way-to-use/ ／ ANA版 https://matsunosuke.jp/how-to-use-ana-mileage/ | 高 |
| 9 | haruwari.com「1マイルの価値はいくら？年100万円の得をする使い方」 | シンガポール ビジネス 9.12円／パリ ファースト 17.94円 | 「往復の運賃を必要マイル数で割って算出」 | 不明 | 不明 | 不明 | 往復 | 不明 | https://haruwari.com/kachi/ | 高 |
| 10 | jp.trip.com「1マイルはいくら？各航空会社別の価値」 | ANA：国内線 1.5〜3.0円、国際線上位クラス 7〜14円／JAL：国内線特典 1.5〜2.5円、国際線ビジネス以上 8〜15円／国際線エコノミー 1.2〜2.5円／e JAL・SKYコイン 1.0〜1.7円 | 不明 | 不明 | 不明 | 不明 | 不明 | 不明 | https://jp.trip.com/guide/info/cost-of-1-mile.html | 高 |
| 11 | genryo-miler.com「１マイルの価値は？JALマイル、ANAマイルで検証！」 | ショッピング等 1〜1.5円（「1円だとお得とは言えない」）／国際線ビジネス・ファースト 10円台 | 不明 | 不明 | 不明 | 不明 | 不明 | 不明 | https://genryo-miler.com/mile-value | 高 |
| 12 | mile-bible.com「1マイルの価値は何円？交換先別・クラス別に実額で検証【2026年4月時点】」 | （数値は要約上帰属未確定。候補：国際線ビジネス 5〜14円、ファースト 10〜20円） | 「実額」検証 | 不明 | 不明 | ファーストは1機あたり8〜14席で特典枠も限られると**空席制約に言及** | 不明 | 2026-04 | https://mile-bible.com/mile-value/ | 中 |
| 13 | trippointslab.com「10万マイルの価値は最大150万円分｜ANA・JAL別シミュレーション【2026年】」 | タイトルから最大15円/マイル（150万円÷10万マイル）＝推定 | 不明 | 不明 | 不明 | 不明 | 不明 | 2026年 | https://trippointslab.com/mile/10man-mile-value-calculation-2026/ | 中（タイトルのみ） |
| 14 | happy-mi-life.net「ANAマイルの価値ってどのくらい？【2020年版】」 | NYファースト 約11.5円（1,725,020円÷150,000マイル） | ファースト現金価格 1,725,020円 | 150,000マイル | 不明 | 考慮なし | 往復と推定 | 2020年版（初出2017-04-01） | https://www.happy-mi-life.net/entry/2017-04-01-144435 | 中（要約上の対応付け） |
| 15 | bousaid.com「ANAエコノミークラスの特典航空券でタイに行ったら、マイルの価値は3.1円だった」 | 3.1円（実体験、国際線エコノミー） | 不明 | 不明 | 不明 | 実体験 | 不明 | 不明 | https://www.bousaid.com/ana%E3%82%A8%E3%82%B3%E3%83%8E%E3%83%9F%E3%83%BC... | 中（タイトルのみ） |
| 16 | ameblo.jp yokohamasoulclub「JALマイルの価値は1マイルいくら？エコノミー・ビジネスクラスで徹底比較」 | ビジネス（2人分）約6.6円 | 不明 | 不明 | 不明 | 不明 | 不明 | 不明 | https://ameblo.jp/yokohamasoulclub/entry-12938921804.html | 中（要約上の対応付け） |
| 17 | note.com「すこ」『「1マイル＝10円」は本当？JAL・ANAマイルの“現実的な価値”を冷静に計算してみた』 | 控除式の例：（700,000−50,000）÷80,000 ≒ 約8円 | 現金価格70万円 | 8万マイル | **諸税・燃油5万円を控除** | 不明 | 不明 | 不明 | https://note.com/moneyskill_chat/n/n38a338fa7b9b | 低〜中（式は検索要約に出現したが当該記事への帰属は未確定） |
| 18 | lovemile.tipsnote.info「1ANAマイルはいくらの価値がある？」 | 交換ベース：10,000ポイント→7,000マイルなので「実質1.43円相当」 | （ポイント原価ベース） | — | — | — | — | 不明 | https://lovemile.tipsnote.info/1milevalue | 低〜中（要約上の対応付け） |
| 19 | hanshin-travel.co.jp「1マイルの価値を徹底検証【ANA/JAL】2024年」 | （要約上帰属未確定。候補：ANA 4〜5円、JAL 4〜6円） | 不明 | 不明 | 不明 | 不明 | 不明 | 2024年 | https://hanshin-travel.co.jp/mile-no-kachi/ | 低 |
| 20 | anasumai.jp（ANAグループ「ANAの住まい」）「ANA1マイルはいくらになる？獲得方法・利用方法別にマイルの価値を計算」 | （数値未取得） | — | — | — | — | — | 不明 | https://anasumai.jp/blog/useful-information/article/59/ | — |
| 21 | magazine.d-money.jp「1マイルの価値とは」／「1マイルはいくらになるの？公式レート」 | （数値未取得。検索要約の「SKYコイン1.0〜1.7円／国内線特典1.5〜4円／提携ポイント0.5〜1円」が本記事由来の可能性） | — | — | — | — | — | 不明 | https://magazine.d-money.jp/creditcard/miles-value-exchange/ ／ https://magazine.d-money.jp/point/one-mile-worth-in-yen/ | 低 |
| 22 | manekai.ameba.jp「1マイルはいくらの価値がある？ANAとJALのマイルの価値を検証」 | （数値未取得） | — | — | — | — | — | 不明 | https://manekai.ameba.jp/creditcard/mileage/value/ | — |
| 23 | tabi-otoku.com「JALマイルの交換先比較2026」 | （数値未取得） | — | — | — | — | — | 2026年 | https://www.tabi-otoku.com/jal-mile-koukansaki-hikaku-2026-otoku-tsukaikata-ejal-point-waon/ | — |
| 24 | travelers-lifehack.com「ANAマイルの価値はいくら？交換先別に比較」／「JALマイルの価値はいくら？」 | （数値未取得。検索要約の「国内線1.5〜2円、国際線ビジネス2.5〜5円」が本記事由来の可能性） | — | — | — | — | — | 不明 | https://www.travelers-lifehack.com/anamile-value/ ／ https://www.travelers-lifehack.com/jal-mile-value/ | 低 |
| 25 | puchi-tool.com「マイル・ポイント価値計算ツール（円/マイル換算）」 | （計算ツール：運賃÷マイルの電卓） | ユーザー入力 | ユーザー入力 | ユーザー入力 | — | — | 不明 | https://puchi-tool.com/mile-value-calculator/ | 中 |

その他、タイトルのみ取得できた関連記事（数値・式は未取得）：flugzeug.hatenablog.com（2022-09-02）https://flugzeug.hatenablog.com/entry/2022/09/02/180000 ／ shirokuma-amex.com https://shirokuma-amex.com/value-of-mile/ ／ global-insights-hub.com（2025-11）https://www.global-insights-hub.com/2025/11/1.html ／ pointtown.com https://www.pointtown.com/articles/1mile/ ／ hapitas.jp https://hapitas.jp/tabihapi/4827/ ／ pipinobu.com https://www.pipinobu.com/entry/milevalue-and-exchange ／ mairu-tubasa.com https://mairu-tubasa.com/ana-mileage-value ／ maru-2-muchu.com ／ miler-nabj.com https://www.miler-nabj.com/entry/mileage-attraction ／ mile-de-hawaii.com https://mile-de-hawaii.com/mile-value/ ／ note.com okitra https://note.com/okitra/n/n7172bfac1e9b ／ note.com Dr.マイル「マイル単価だけで判断してはいけない理由」https://note.com/shunji1000/n/n5d283079b745 ／ miles.kaiteki-travel.com https://miles.kaiteki-travel.com/miles_abroad.html ／ coraltrading.xsrv.jp https://coraltrading.xsrv.jp/2139.html ／ card.tagu-blog.com（2026）https://card.tagu-blog.com/ana-mile-complete-guide-2026/ ／ creditcard-rescue.com https://creditcard-rescue.com/column/1mile/ ／ abtem ANA版（2026）https://abtem.hateblo.jp/entry/ana-mile-value-yen-guide-2026

#### 1-B. 検索要約に出現したが出典URLを特定できなかった提示値（「出典未確定」。報告書では引用せず背景情報として扱うこと）
- 「1マイルの価値の平均は15.8円」（ファースト、サイト不明）— 検索要約 [dietmiler検索](https://dietmiler.com/201803mile) 周辺
- 「日本⇆NY ファースト運賃 2,567,050円 ÷ 165,000マイル ＝ 15.55円」（サイト不明）
- 「ファースト 16.3円〜17.92円」「ZONE7ヨーロッパ（ロンドン）ファースト 19.17円」（サイト不明）
- 「国内線特典 2〜5円／国際線ビジネス 5〜14円／国際線ファースト 18〜20円近く」（候補：mile-bible.com）
- 「国内線 2〜3.5円／国際線エコノミー 1.8〜2.5円／国際線ビジネス 5〜8円以上」（候補：abtem ANA版 2026）
- 「30,000円の航空券を15,000ANAマイルで発券すれば1マイル＝2円」（国内線の定番例、複数サイト）
- 「国内線 約3円／国際線エコノミー 約4円／ビジネス 約7円」（サイト不明）
- 「東京〜NY：現金1,500,000円、必要110,000マイル、諸税・燃油60,000円 → 約13円」（仮設例、サイト不明）
- 「2026年10月時点の表で北米ファーストは片道85,000マイル」（ブログの表、サイト不明。ANA公式の必要マイル表と要照合）
- 「他社ポイント・商品交換は0.8〜1円」「国内線の割引運賃を前提にすると2円前後が無難」（複数サイト）

#### 1-C. 計算式の型（検索要約で確認できたもの）
- 型A（単純比）：「マイル単価（円/マイル）＝ 航空券の購入価格（円）÷ 必要マイル数」— [価格.comマガジン検索要約](https://kakakumag.com/money/?id=21323)、[akirax 2026](https://news.akirax.online/2026/05/04/ana-mile-value-best-use-flight/)、[rikei-miler](https://rikei-miler.com/mile/post-32/)、[haruwari](https://haruwari.com/kachi/)、[dietmiler](https://dietmiler.com/201803mile)
- 型B（控除比）：「1マイルの価値 ＝（現金で買った場合の航空券価格 − 特典航空券の諸税・燃油・手数料）÷ 必要マイル数」— 検索要約（候補：[note すこ](https://note.com/moneyskill_chat/n/n38a338fa7b9b)）。「燃油サーチャージを引かずに出す単純計算は過大評価になる」という指摘も同要約内。
- 型C（交換レート逆算）：「10,000ポイント→7,000マイル ⇒ 1マイル＝1.43円相当」— [lovemile.tipsnote.info](https://lovemile.tipsnote.info/1milevalue)（帰属は中程度）
- 型D（レンジ表示）：交換先×クラス別の目安表（SKYコイン1.0〜1.7／国内1.5〜4／ビジネス5〜10超／ファースト7〜20）— [akirax 2026](https://news.akirax.online/2026/05/04/ana-mile-value-best-use-flight/)、[The Goal](https://matsunosuke.jp/jal-mile-way-to-use/)、[trip.com](https://jp.trip.com/guide/info/cost-of-1-mile.html)
- 公式見解の不在：「ANAもJALも『1マイル＝◯円』という価値を公式には定めていません。公式に決まっているのは特典航空券の必要マイル数と各種ポイントへの交換レートだけ」— 検索要約（[genryo-miler 検索](https://genryo-miler.com/mile-value)ほか複数サイトが同旨）
- YouTube：検索結果に動画は一件も含まれず（検索要約も「YouTube動画は結果に含まれていませんでした」と明記）。

### Inferences
- 「1マイル＝15〜20円」の生成構造は、(i) 分子＝正規ファースト／正規ビジネス運賃の往復額（ほぼ誰も現金で買わない水準）、(ii) 分母＝ローシーズン最低必要マイル（165,000／150,000など）、(iii) 燃油・諸税の現金負担を無視、(iv) 空席（特典枠）が取れる確率を無視、の4つのバイアスが同方向に積み重なった**上限値**であり、サイト自身も「最大」「狙える」という表現でこれを認めている（burio「最大15円以上」、abtem「3円以上を狙える」）。
- 分母に関しては2025〜2026年の改定（検索要約：「2025年の改定で特典航空券の必要マイル数がほぼ全路線で値上げ」「2026年5月の国内線必要マイル改定」、JAL「特典航空券PLUS」での変動）があり、古い記事の数値（2017〜2020年）はさらに上方バイアスを含む。
- 控除式（型B）を採る少数サイトの試算（約8円、約13円）でも、分子は依然として正規運賃級の現金価格であり、「実際に払うであろう価格（reasonable cash alternative）」には置き換えられていない。
- 国内線2円の定番例（30,000円÷15,000マイル、30,000円÷14,000マイル）は、分子が割引運賃水準であるため比較的「実勢」に近いが、変更不可・取消料などの条件差（rikei-milerが指摘）を無視している。

### Gaps
- 各サイトの計算式の**完全な原文転記**（本文取得不可のため）。特に travelers-lifehack、manekai、d-money、tabi-otoku、mile-bible の数表。
- YouTube での提示値（検索で動画がヒットせず）。
- 1-B に挙げた未帰属の提示値の出典特定。

## KQ2. 「普通運賃」「正規ビジネス／ファースト運賃」の実額（アンカーの大きさ）と、実際に販売されている比率

### Takeaway
ANA国内線は2026年5月19日搭乗分から「フレックス／スタンダード／シンプル」等の新運賃体系に移行しており、片道運賃表PDF（2026-04-07以降購入分、2026-10-15以降購入分）は公開されているが、本調査では羽田－那覇・福岡・伊丹・新千歳の**フレックス金額を数値として取得できなかった**。国際線は、ANA 東京－NY ビジネス往復が「タイムセールで56万円〜」「通常期サンプルで約86万〜98万円」である一方、ブログがアンカーとして用いるファースト運賃は「約257万〜295万円」であり、分子の選択だけで3〜5倍の差が生じる。正規運賃の購入比率を示す資料は見つからなかった。

### Cited Findings

| 項目 | 数値 | 前提（片道/往復・燃油・時期） | 算定方法/性質 | 出典URL | 掲載日 |
|---|---|---|---|---|---|
| ANA国内線 新運賃体系（フレックス／スタンダード／シンプル等）の届出 | 2026-05-19〜2026-10-24搭乗分 | — | 国交省届出プレスリリース | https://www.anahd.co.jp/group/pr/202505/20250520-4.html | 2025-05-20 |
| ANA国内線 運賃届出（次期） | 2026-10-25〜2027-03-27搭乗分 | 「フレックス（国際線接続専用）」は2026-05-19搭乗分から設定 | 同上 | https://www.anahd.co.jp/group/pr/202510/20251028-2.html | 2025-10-28 |
| ANA「フレックス/株主優待割引/島民割引/ユース/シニア 片道 運賃表」 | （金額は表の列が崩れて抽出不能。東京＝那覇の行は存在） | 2026-04-07以降購入分、片道 | 公式運賃表PDF | https://www.anahd.co.jp/group/pr/pdf/20260319-3-1.pdf | 2026-03-19 |
| ANA「スタンダード 片道 運賃表」 | （金額未取得） | 2026-07-01以降購入分 | 公式PDF | https://secure.ana-g.com/anacom/cgi-bin/applicablefare/pdf/standard_26w_01_ja.pdf | 2026 |
| ANA「シンプル 片道 運賃表」 | （金額未取得） | 2026-10-15以降購入分 | 公式PDF | https://secure.ana-g.com/anacom/cgi-bin/applicablefare/pdf/simple_26w_01_ja.pdf | 2026 |
| ANA「ANAカード優待割引 片道 運賃表」 | （東京－那覇、東京－福岡の行あり、金額未取得） | 2026-09-17以降購入分 | 公式PDF | https://secure.ana-g.com/anacom/cgi-bin/applicablefare/pdf/card_26s_01_ja.pdf | 2026 |
| ANA「代表的な運賃・料金一覧」／「ANA国内線利用運賃一覧表」 | （金額未取得） | — | 公式ページ | https://www.ana.co.jp/ja/jp/guide/plan/fare/domestic/ichiran/ ／ https://www.ana.co.jp/amcservice/pps/dom_unchin_list.html | — |
| ANA 東京－ニューヨーク ビジネス往復（タイムセール） | 560,000円〜 | 往復、2026-10-21まで発売、燃油込みか不明 | 旅行メディア報道 | https://tabiris.com/archives/anasale20261020/ | 2026-10-20 |
| ANA 羽田－ニューヨーク ビジネス往復（通常期サンプル） | 約983,230円（2025年12月下旬）／約858,230円（2026年2月上旬） | 往復、特定日サンプル | 価格比較記事（約9か月前の掲載。出典URLは要約上未確定：候補 https://mikan-travel-abroad.com/business-class-price/ または https://jp.trip.com/guide/airline-deals/ana-business-class.html ） | （候補URL参照） | 2026年初頭と推定 |
| ANA 米国線「正規ビジネス運賃・ビジ割」一覧（旅・コンシェルジュ） | （東京－NYの行あり、数値は抽出不能） | — | 旅行会社の運賃表 | https://the-sky.jp/tariff/C2USANH.html | 更新 2026-10-27 |
| 国際線ビジネスクラス運賃一覧（tokyo-airlines.com） | （数値未取得） | — | まとめ表 | https://tokyo-airlines.com/airline/airfare.html | 不明 |
| ANA「ビジネスクラスで行く旅」公式 | 「ニューヨーク（往復）」区分あり、金額未取得 | 往復 | 公式 | https://www.ana.co.jp/ja/jp/international/theme/business_class_tkt/ | — |
| ブログがアンカーに使うファースト運賃例① | 欧州往復 約295万円／2,915,000円 | 往復、Lシーズン165,000マイルと比較 | dietmiler | https://dietmiler.com/201803mile | 2018-03（推定） |
| 同② | NY往復 280万円 | 往復、150,000マイルと比較、諸経費別 | burio | https://burio-kyonomanabi.com/mile-skycoin/ | 不明 |
| 同③ | NY ファースト 1,725,020円 | 150,000マイルと比較 | happy-mi-life 2020年版 | https://www.happy-mi-life.net/entry/2017-04-01-144435 | 2020 |
| 同④ | NY ファースト 2,567,050円（出典未確定） | 165,000マイルと比較 | — | — | — |

### Inferences
- アンカーの大きさ（推定）：NYビジネスの「実勢」往復価格（56万〜98万円）に対し、ブログ分子のファースト往復（約257万〜295万円）は約3〜5倍。同じ路線でも分子をファースト正規運賃からビジネスのセール運賃に置き換えるだけで「円/マイル」は約1/3〜1/5に縮む（本推定は上表の数値の単純比較）。
- ANA国内線の運賃名称が2026年5月に変更された（旧「ANA FLEX」等から「フレックス／スタンダード／シンプル」）ため、2026年以前の「普通運賃」を分子に使う記事は現行運賃体系と整合しない。

### Gaps
- ANA国内線フレックス片道運賃（羽田－那覇／福岡／伊丹／新千歳）の金額：公式PDFは特定できたが数値を抽出できなかった。
- JAL国内線（フレックス）運賃：検索上限到達のため未調査。
- ANA/JAL 東京－ロンドン、東京－ホノルルの正規ビジネス／ファースト運賃：未調査。
- 正規運賃（フレックス・正規ビジネス）の販売比率・購入者割合を示す資料：見つからず（未調査）。

## KQ3. ANA/JAL公式の現金等価レート（フロア値）：SKYコイン、e JALポイント、他社ポイント交換、機内販売等

### Takeaway
航空会社自身が提示する最も確実な換算は、**JAL：10,000マイル→15,000 e JALポイント（1.5円/マイル、航空券・ツアー購入限定、1万マイル単位）**、**ANA：SKYコイン 1.0〜1.7倍（1〜9,999マイルは全員1.0倍、一般会員は最大1.2倍、上級会員が5万マイル以上で1.7倍）**である。他社ポイントへの交換は0.8円/マイル前後（ANA→楽天 最大80%、JAL→Amazon 1万マイル→8,000円相当）に下がり、ANAは2026年4月22日から楽天・V・nanacoへの交換に1日2口（2万マイル）の上限と「年度内3口目以降は50%（10,000マイル→4,000ポイント）」の逓減を導入した。したがって「現金等価の最低保証値」は**約0.4〜0.8円**、「航空会社内通貨としての下限」は**1.0〜1.5円**と整理できる。

### Cited Findings

| 項目 | 数値 | 条件・前提 | 算定方法/性質 | 出典URL | 掲載日 |
|---|---|---|---|---|---|
| ANA SKYコイン：プレミアムメンバーの交換率 | 最大1.7倍 | 「プレミアムメンバーのお客様は、10,000マイル以上をANA SKY コインに交換する際、交換率が最大1.7倍」（ANA公式） | 公式記載（掲載時期が古い可能性） | https://www.ana.co.jp/ja/jp/amc/premium/service/delight/detail/ | 不明 |
| ANA SKYコイン：1.7倍の適用マイル数（ブログ） | 上級会員（ブロンズ以上）は50,000マイル以上の交換で1.7倍 | 多くの解説記事が一致 | ブログ要約 | https://matsunosuke.jp/ana-sky-coin/ ／ https://abtem.hateblo.jp/entry/ana-sky-coin-complete-guide-2026 ／ https://otokurashi.jp/how-to-use-ana-skycoin/ | 2026 |
| ANA SKYコイン：カード別最大倍率 | ANA一般カード 最大1.2倍／ANAワイドカード 最大1.5倍／ゴールド・プレミアム系 最大1.6倍 | 交換数量・会員ステイタス・カード種類で変動 | ブログ要約 | https://www.pipinobu.com/entry/ana-male-skycoin-exchange ／ https://trippointslab.com/mile/ana-sky-coin-vs-tokuten-koukuken-family-2026/ | 2026 |
| ANA SKYコイン：1万マイル未満 | 1〜9,999マイルは「どんな条件でも」1.0倍 | 全会員 | ブログ要約 | https://www.warau.jp/style/article/ana-sky-%E3%82%B3%E3%82%A4%E3%83%B3... | 不明 |
| ANA SKYコイン：レンジ | 1マイル＝1〜1.7コイン（1コイン＝1円でANA航空券・ツアーに充当） | — | ブログ要約 | https://burio-kyonomanabi.com/skycoin/ ／ 公式ツアー利用 https://www.ana.co.jp/ja/jp/amc/skycoin/travel/ | — |
| JAL e JALポイント：基本レート | 1,000マイル→1,000ポイント（1.0円/マイル） | 1,000マイル単位 | ブログ要約（複数一致） | https://matsunosuke.jp/e-jal-point/ ／ https://www.pricey.jp/web/articles/6450 | 2026 |
| JAL e JALポイント：1.5倍レート | 10,000マイル→15,000ポイント（1.5円/マイル） | 1万マイル単位での交換 | JAL公式（ジャルパック案内「10,000マイルの交換で換算率が1.5倍」）＋ブログ | https://www.jal.co.jp/jp/ja/tour/otoku-guide/ ／ https://pay-route.co.jp/article/2026/03/17/how-to-use-ejal-points-for-flights-hotels-and-mile-exchange/ | 2026-03-17（pay-route） |
| JAL e JALポイント：食い違い | 「1,000マイル＝1,500ポイント」と書く記事あり | 多数派は1万マイル以上で1.5倍 | 要約が矛盾を指摘 | https://www.tansoratan.com/entry/jal-ejalpt | 不明 |
| JAL e JALポイント：有効期限 | 交換日から1年後の同月末。追加交換のたびに全残高の期限が延びる | — | ブログ要約（複数） | https://abtem.hateblo.jp/entry/jal-mile-expiration-guide-2026 ／ https://love-mileage.com/post-5976/ | 2026 |
| JAL e JALポイントは「損か」 | 「1マイル＝1.5円は損？得なパターン」を検証する記事 | — | ブログ | https://yumefuwa.com/e-jal-point/ | 不明 |
| JAL→Amazonギフト | 1万マイル→8,000円相当（0.8円/マイル） | — | ブログ要約 | https://abtem.hateblo.jp/entry/jal-mile-value-yen-conversion-guide | 2026 |
| ANA→楽天ポイント | 最大80%（0.8円/マイル相当） | 「ポイントに戻すのは割に合わない」との評価 | ブログ要約 | https://vie-simple.com/rakuten-point-to-ana-jal-mile/ ／ https://www.r-zyunin.com/rakuten-spu-point/rakuten-point-mile | 2026 |
| ANA→楽天／V／nanaco：上限と逓減（2026-04-22〜） | 1日最大2口（2万マイル）。年度内累計で2口目まで100%、3口目以降は50%（例：3口目は10,000マイル→4,000ポイント＝0.4円/マイル） | 2026-04-22申込分から | 報道＋ブログ | https://www.traicy.com/posts/20260331366718/ ／ https://rakuten.tank.jp/...（2026年5月確認） | 2026-03-31（TRAICY） |
| 楽天ポイント→ANAマイル（逆方向、参考） | 2ポイント＝1マイル。期間限定ポイント不可。反映3〜4週間 | 月20,000ポイント等の上限 | ブログ要約 | https://matsunosuke.jp/rakuten-point-ana-mile/ | 2026 |
| JALマイル交換増量キャンペーン（他社→JAL、参考） | 「J-POINTは72％」など実質レート比較 | 2026年9月 | ブログ | https://dp-invest.hateblo.jp/entry/2026/02/19/124406 | 2026-02-19 |
| ドットマネー（参考） | 1マネー＝1円。dポイント最大15%増量キャンペーン 2026-11-01〜2027-01-05 | — | 公式 | https://d-money.jp/guide ／ https://d-money.jp/withdrawal/point/detail/1154 | 2026 |

### Inferences
- ANA SKYコインの倍率表（推定・記憶ベース、要公式確認）：交換マイル数の階段（10,000／20,000／30,000／40,000／50,000以上）×属性（一般会員／ANA一般カード／ワイド／ゴールド・プレミアム・SFC／プレミアムメンバー）で、一般会員は10,000マイル以上で一律1.2倍、ワイドは最大1.5倍、ゴールド等は最大1.6倍、プレミアムメンバーは50,000マイル以上で1.7倍、という構造と推定される。上表のブログ記載（最大倍率）と整合的。公式ページの「10,000マイル以上で最大1.7倍」は「10,000マイル以上から倍率が上がり始め、最大で1.7倍」の意味と解釈できるため、ブログの「50,000マイル以上」と矛盾しない。
- フロア値の階層（推定）：
  - 層0（真の現金等価に最も近い）：他社ポイント交換 0.4〜0.8円/マイル（ANA→楽天80%・逓減後40%、JAL→Amazon 80%）。
  - 層1（航空会社内通貨、用途・期限制限付き）：ANA SKYコイン 1.0円（1万マイル未満・一般）〜1.2円（一般会員1万マイル以上）〜1.7円（上級会員5万マイル以上）、JAL e JALポイント 1.0円（千マイル単位）〜1.5円（万マイル単位）。
  - 2026年の改悪（ANAの他社ポイント交換上限・逓減）は、層0のフロアを「0.8円」から「大量交換時は0.4円」へ実質的に引き下げた。
- モデルの「フロア値」として採用する場合、JAL=1.5円（e JAL、1万マイル単位、航空券購入に限定、1年期限）、ANA=1.2円（一般会員SKYコイン1万マイル以上）が「航空会社保証の下限」、0.8円が「現金に近い下限」と置くのが妥当。

### Gaps
- ANA SKYコインの公式倍率表（階段ごとの数値）の原文：本文取得不可。
- ANA→Vポイント／Ponta／iTunes、JAL→Ponta／dポイント／WAON の2026年時点レート：検索上限到達のため未取得。
- ANA機内販売・ANAショッピング（A-style）、JALショッピング・機内販売でのマイル利用レート：未取得（一般に1マイル＝1円と理解されているが本調査では未確認＝推定）。
- e JALポイントの1.5倍「キャンペーン」の有無（恒常レートか）：恒常レートとして各サイトが記載しているが公式ページ原文は未確認。

## KQ4. 会計上のマイル単価：ANA HD・JALの契約負債（マイレージ分）と未使用マイル残高からの1マイル当たり負債計上額

### Takeaway
ANAホールディングス（日本基準）の連結「契約負債」は2022年3月末2,560億円→2023年3月末3,935億円→2024年3月末4,450億円→2025年3月末5,261億円（決算短信、単位は百万円と推定）、JAL（IFRS）は2019年3月末約2,947億円→2025年3月末約4,379億円と増加しているが、**いずれも航空券前受金等を含む合計額で、マイレージ分の内訳と未使用マイル残高は本調査で取得できず、1マイル当たり負債計上額は算出できなかった**。JALの有価証券報告書は、収益認識基準適用後「将来顧客が行使すると見込まれるマイル」を履行義務として契約負債に計上し、利用時に収益認識する旨を記載している（＝負債は失効見込み控除後の金額）。

### Cited Findings

| 項目 | 数値 | 算定方法/性質 | 出典URL | 掲載日 |
|---|---|---|---|---|
| ANA HD 連結 契約負債（2022/3末→2023/3末） | 256,023 → 393,545（単位は表に明記なし。百万円と推定） | 2023年3月期決算短信（日本基準）の貸借対照表 | https://www.anahd.co.jp/group/pr/pdf/20230427-1-1.pdf | 2023-04-27 |
| ANA HD 連結 契約負債（2023/3末→2024/3末） | 393,545 → 444,982（百万円推定） | 2024年3月期決算短信 | https://www.anahd.co.jp/group/pr/pdf/20240426-1-1.pdf | 2024-04-26 |
| ANA HD 連結 契約負債（2024/3末→2025/3末） | 444,982 → 526,111（百万円推定、約5,261億円） | 2025年3月期決算短信 | https://www.anahd.co.jp/group/pr/pdf/20250430-1-1.pdf | 2025-04-30 |
| ANA HD 収益区分の説明 | 「マイレージ附帯収入、機内販売収入、整備受託収入等が含まれています」（収益の区分説明であり、マイレージ負債額ではない） | 2023年3月期決算短信 | https://www.anahd.co.jp/group/pr/pdf/20230427-1-1.pdf | 2023-04-27 |
| ANA HD 有価証券報告書（2025年3月期） | 提出日 2025-06-26（マイレージ分の契約負債内訳は本調査で未取得） | EDINET | https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100W708.pdf | 2025-06-26 |
| ANA HD IR資料室／統合報告書2025／決算説明会資料 | （マイル残高の開示は未確認） | 公式 | https://www.ana.co.jp/group/investors/irdata/ ／ https://www.ana.co.jp/group/investors/irdata/annual/pdf/25/25_00_2.pdf ／ https://www.ana.co.jp/group/investors/data/kessan/pdf/2025_04_2.pdf | 2025 |
| JAL 連結 契約負債（IFRS） | 2019年3月末 約2,947億円 → 2025年3月末 約4,379億円（航空運送の前受分を含む全体額） | 第三者集計（IRBANK） | https://irbank.net/E04272/ContractLiabilitiesCLIFRS?t=Q4 | 取得日2026-11-04 |
| JAL 会計処理の変更（2021年3月期有報） | 適用前：マイレージ利用による将来の費用負担を販管費計上し、未利用マイルを営業未払金として表示。適用後：マイルと交換される特典の履行義務に配分した対価を契約負債として計上 | 有価証券報告書本文 | https://ir-library.kitaishihon.com/IrLibrary/9201_securities_2020_os5r.pdf | 2021-06-18 |
| JAL マイレージの収益認識方針（直近有報） | 「旅客輸送サービス等の利用に応じて付与するマイルのうち、将来顧客が行使すると見込まれる分を履行義務として認識し、その配分額を契約負債として扱い、マイルの利用に応じて収益計上」 | 有価証券報告書本文（要約） | https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100W1KL.pdf | 2025-06-23 |
| JAL 有価証券報告書（2022年6月提出分、参考） | — | EDINET経由 | https://ssl4.eir-parts.net/doc/9201/yuho_pdf/S100OBZH/00.pdf | 2022-06-22 |

### Inferences
- 1マイル当たり負債計上額の算定式（モデル用）：
  - 単価A（残高ベース）＝ マイレージに係る契約負債残高 ÷ 期末未使用マイル残高
  - 単価B（期待行使ベース）＝ マイレージに係る契約負債残高 ÷（期末未使用マイル残高 ×（1 − 失効見込率））
  - JAL有報の記述（「将来顧客が行使すると見込まれる分」のみ負債計上）から、開示される契約負債は失効見込み控除後であり、単価Aは「1マイルの期待価値」を、単価Bは「行使される1マイルの価値」を表す。モデルの比較対象には単価Aが適切（推定）。
- 連結契約負債の全体額には航空券前受金（繁忙期前に増加）が含まれるため、マイレージ分の推移を見るには有報注記の内訳が必須。2025年3月末時点で ANA HD 5,261億円・JAL 4,379億円という全体額は、マイレージ負債の**上限**としてしか使えない。
- 収益認識基準（IFRS 15 / 企業会計基準第29号）の一般原則として、マイルは「追加的な財・サービスを取得するオプション（重要な権利）」として別個の履行義務となり、取引価格は独立販売価格に基づき配分される。したがって会計上の1マイル単価は、販売運賃と特典の独立販売価格（通常、失効見込みと特典の市場価値を織り込んだ推定値）から導かれ、ブログの「正規運賃÷必要マイル」よりも構造的に低くなる（推定。原文注記は未確認）。

### Gaps
- ANA HD・JALの有報注記における「マイレージ」に係る契約負債の金額（2023〜2026年度）：本文取得不可・検索上限で未取得。
- 未使用マイル残高（発行済未行使マイル）の開示有無：未確認（両社とも開示していない可能性が高い）。
- 2026年3月期決算短信（2026年4〜5月公表）の契約負債：未取得。
- JALの契約負債の年度別内訳（2020〜2024年3月末）：IRBANKの中間年は要約に含まれず。

## KQ5. 海外の評価手法：TPG／NerdWallet／Point.me／Upgraded Points／OMAAT のANA・JAL評価値と算定法、空席データに基づく評価、学術研究

### Takeaway
米国系評価では ANA Mileage Club は **1.4セント/マイル（TPG 2026年10月、Upgraded Points・OMAAT も2026年9月時点で1.4セント）**、TPG は2026年11月に **1.3セント**へ引き下げたと二次サイトが報じている（TPG本体ページでは未確認）。1マイル≒2円（1.3〜1.4セント×約150円/ドル）という水準は、日本語ブログの「15〜20円」とは桁が異なり、「実際に払うであろう妥当な現金価格」を分子に取る米国式手法との差を示す。学術面では Gao（2020）の概念フレームワーク、Goldfine（2024, Vanderbilt Law Review）の「消費者に高価値だと信じさせつつ実際の価値を制限する」構造批判、Monash の顕示選好推計などが存在する。

### Cited Findings

| 項目 | 数値 | 算定方法/性質 | 出典URL | 掲載日 |
|---|---|---|---|---|
| TPG：ANA Mileage Club 評価値（2026年10月） | 1.4セント/マイル | TPG月次評価（転送パートナー表） | https://thepointsguy.com/credit-cards/credit-card-transfer-partners ／ https://thepointsguy.com/loyalty-programs/monthly-valuations/ | 2026-10 |
| TPG：ANA 評価値（2026年11月） | 1.3セント（1.4から引き下げ） | 二次サイトがTPG 11月評価を転載（TPG本体で未確認） | https://newyorkmetropolitan.com/what-are-points-and-miles-worth-tpgs-november-2026-monthly-valuations/ | 2026-11 |
| TPG：2026年6月評価（参考） | （転載記事） | 二次サイト | https://travelzuma.com/what-are-points-and-miles-worth-tpgs-june-2026-monthly-valuations/ | 2026-06 |
| Points Plug：複数媒体のANA評価 | TPG・Upgraded Points・One Mile at a Time がいずれも 1.4セント（2026年9月時点） | 比較ページ | https://pointsplug.com/value/ana-mileage-club | 2026-09 |
| Mile Marketplace：ANA 評価ページ | （数値は要約未取得）2026年版 | 評価ページ＋計算ツール | https://milemarketplace.com/miles-value/ana-mileage-club ／ https://milemarketplace.com/miles-value-calculator | 2026 |
| Award Travel Finder：AA AAdvantage（参考） | 約1.4セント（2026） | 比較用 | https://awardtravelfinder.com/american-airlines-miles-value | 2026 |
| Gao（2020）IJAAA「A Conceptual Framework for Valuating Airline FFP Miles」 | 特典種別ごとの必要マイルと現金価格を比較し、消費者調査で知覚価値を推定する枠組み | 学術論文（Embry-Riddle） | https://commons.erau.edu/ijaaa/vol7/iss1/11/ ／ PDF https://commons.erau.edu/cgi/viewcontent.cgi?article=1447&context=ijaaa | 2020 |
| Goldfine（2024）Vanderbilt Law Review「The Financialization of Frequent Flyer Miles」 | 「プログラムは消費者にポイントが高価値だと信じさせつつ、実際の価値を制限することに依存している」と論じる（航空会社が償還時の価値を支配） | 法学論文 | https://scholarship.law.vanderbilt.edu/vlr/vol77/iss1/5/ | 2024 |
| Orhun, Guo & Hagemann「Reaching for Gold: Frequent-Flyer Status Incentives and Moral Hazard」 | 米航空会社350万会員（2010–2011）のデータ。ステータス目標に近づくほどスイッチングコスト上昇 | ワーキングペーパー | https://yesimorhun.com/wp-content/uploads/2021/10/Orhun_Guo_Hagemann_Final_Ver.pdf | 2021 |
| Monash Univ. Discussion Paper 04/11「Paying for status: the effect of frequent flier…」 | 無料旅行に近い会員の限界ポイント価値 約17〜28米セント/pt、平均推計 約12セント/pt（要約値。プログラム・単位の定義は原文要確認） | 顕示選好推計 | https://www.monash.edu/__data/assets/pdf_file/0003/925374/paying_for_status_-_the_effect_of_frequent_flier.pdf | 2011 |
| Chun et al.（Stanford GSB WP）「Loyalty Program Liabilities and Point Values」 | （mba.aero記事が引用。内容未確認） | ポインタのみ | https://www.mba.aero/frequent-flyer-programs-part-1-valuable-intangible-assets-effects-spend-based-programs/ | — |
| Martone, Administrative Law Review 77.4「Staying on Point: A Case for Limited DOT…」 | DOTのFFP規制権限の限界を論じる | 法学論文 | https://administrativelawreview.org/wp-content/uploads/sites/2/2025/12/ALR-77.4_Martone.pdf | 2025-12 |

### Inferences
- 1.3〜1.4セント/マイルを150円/ドルで換算すると約2.0〜2.1円/マイル。これは日本語ブログの「国内線特典2円」とほぼ同水準であり、日本語ブログの「国際線ビジネス5〜15円」「ファースト15〜20円」は、米国系評価が意識的に排除している「アスピレーショナル（憧れ）償還」を代表値に採用した結果と解釈できる（推定）。
- 米国系の評価が「what you would actually pay（実際に支払うであろう価格）」を分子に置く手法であることは一般に知られているが、本調査ではTPG本体の手法説明文を取得できなかった（Gap）。

### Gaps
- TPG のANA/JAL評価の算定法原文（methodology）、JAL Mileage Bank の評価値：取得不可。
- NerdWallet、Point.me、Bankrate、AwardWallet の ANA/JAL 評価値：検索上限により未取得。
- Seats.aero／Reward Flying 等の空席データに基づく評価：未調査。
- Monash論文の「12セント」の単位・対象プログラム：要原文確認。

## KQ6. 失効マイル・未使用マイルの統計（breakage率）

### Takeaway
米国の10-K開示では、Alaska Air Group（Mileage Plan）が breakage 率 **17.4%**（2013年に12%から引き上げ、2017・2018年も17.4%、1%の変動で負債約700万ドルの影響）、AIR MILES（Alliance Data／Loyalty Ventures）が **26%（2015）→20%（2016年12月以降、2019〜2021年も20%）**、累計償還率69%（2021年末）を開示している。業界一般には10〜20%とされるが、米大手3社（DL/UA/AA）およびANA/JALの失効率は本調査で取得できなかった。

### Cited Findings

| 項目 | 数値 | 算定方法/性質 | 出典URL | 掲載日 |
|---|---|---|---|---|
| Alaska Air Group（FY2013 10-K） | 失効見込率を12%→17.4%に引き上げ | 過去データの統計分析 | https://www.sec.gov/Archives/edgar/data/0000766421/000076642114000010/alk10-k123113.htm | 2014 |
| Alaska Air Group（FY2014/FY2015 10-K） | breakage 率 17.4%（「historical activity in our members' accounts and other factors」に基づく）。感応度：1%の変動で負債に約700万ドルの影響 | 10-K | https://www.sec.gov/Archives/edgar/data/0000766421/000076642115000009/alk10-k123114.htm ／ https://www.sec.gov/Archives/edgar/data/0000766421/000076642116000065/alk10-k123115.htm | 2015／2016 |
| Alaska Air Group（FY2018 10-K） | 2018年・2017年の breakage 率 17.4% | 10-K | https://www.sec.gov/Archives/edgar/data/766421/000076642119000008/alk10-k123118.htm | 2019 |
| Loyalty Ventures（AIR MILES, FY2021 10-K） | 2019〜2021年 breakage 率 20%。累計償還率（program-to-date redemptions ÷ issuance）69%（2021-12-31） | 10-K | https://www.sec.gov/Archives/edgar/data/1870997/000155837022002348/lylt-20211231x10k.htm | 2022 |
| Alliance Data（AIR MILES, FY2020 10-K ほか） | 2015年 26% → 2016年12月に20%へ変更。2018〜2020年 20% | 10-K | https://www.sec.gov/Archives/edgar/data/1101215/000110121521000036/ads-20201231x10k.htm | 2021 |
| CBS News | 「一部のプログラムでは償還されるマイルは8%にすぎない」と報道（breakageではなく償還率の指標。要原文確認） | 報道 | https://www.cbsnews.com/news/airline-loyalty-programs-getting-harder-to-redeem-frequent-flyer-miles/ | 不明 |
| Medium（非権威的） | FFPのbreakage率は通常10〜20%程度 | ブログ | https://medium.com/@siddharthreddy0912/how-airlines-turn-miles-into-gold-the-business-of-loyalty-9b17893ea518 | 不明 |
| JAL 有報 | 「将来顧客が行使すると見込まれる分」のみ履行義務として認識（＝失効見込みを控除。率は非開示） | 有報 | https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100W1KL.pdf | 2025-06-23 |

### Inferences
- マイルの期待価値を割り引く係数として、保守的には20%（AIR MILES）、航空会社型では17.4%（Alaska）が開示ベースの参照値。ANA/JALのマイル有効期限（搭乗月から36か月、上級会員等の例外あり）は北米大手の「無期限化」より短いため、失効率はAlaska並み以上になる可能性がある（推定。根拠は期限制度の違いのみ）。
- 会計上の契約負債は失効見込み控除後のため、「負債 ÷ 未使用マイル残高」で得られる単価には既に breakage が織り込まれている。

### Gaps
- Delta／United／American の10-K breakage 開示（2024年）：検索上限により未取得。
- ANA／JAL の失効マイル額・失効率、未使用マイル残高：開示を確認できず。
- IdeaWorks 等の業界推計：未調査。

## KQ7. 消費者保護の観点：米DOTのFFP調査（2024〜2025）、日本の消費者庁・公取委・国民生活センター、資金決済法上の位置づけ

### Takeaway
米DOTは2024年9月にAmerican・Delta・United・Southwestの4社に対し、マイルの価値切り下げ（遡及的な必要マイル変更）、追加手数料、透明性等について「unfair, deceptive or anticompetitive practices」の有無を調査する書簡を発出し、各社に「1マイルの平均ドル価値」や全手数料の開示を求めたが、**2025年以降の調査結果・処分は本調査で確認できなかった**（2025年12月のAdministrative Law Review論文もDOT権限の限界を論じるのみ）。日本では、国民生活センターがポイント失効・付与不履行の相談事例を報告（2021年、2025年）しており、資金決済法上は「対価と引き換えに発行」されない景品的ポイントは前払式支払手段の規制対象外、発行日から6か月以内に限り使用できるものも適用除外、有効期限の設定は発行者の裁量で期限切れ後の払い戻しは原則不可、という整理が確認できた。マイル固有の相談事例や消費者庁・公取委の見解は未取得。

### Cited Findings

| 項目 | 内容 | 出典URL | 掲載日 |
|---|---|---|---|
| DOT FFP調査の開始 | 2024年9月、AA・DL・UA・WNの4社を対象に「unfair, deceptive or anticompetitive practices」の有無を調査。懸念：必要マイル数の遡及的変更による価値切り下げ、追加手数料 | https://www.deseret.com/lifestyle/2024/09/06/frequent-flyer-program-dot-investigation/ ／ https://simpleflying.com/usdot-launches-loyalty-program-inquiry/ ／ https://www.ch-aviation.com/news/144552-dot-probes-us-airlines-frequent-flyer-programmes | 2024-09 |
| DOTが求めた資料 | 「各マイルの平均ドル価値」「ロイヤルティプログラムに関する全手数料」の提出 | https://viewfromthewing.com/breaking-new-government-investigation-demands-airlines-expose-frequent-flyer-devaluations/ ／ https://www.nerdwallet.com/travel/news/dots-frequent-flyer-program-inquiry-whats-being-investigated | 2024-09 |
| 業界団体の反応 | Airlines for America：「米航空会社はプログラムについて透明であり、政策当局は消費者がこれらの利益を受け続けられるようにすべき」 | https://thepointsguy.com/news/dot-investigate-frequent-flyer-programs | 2024-09 |
| DOT/CFPB 公聴会（2024年5月） | FFPの公正性が問われたワシントンDCでの公聴会 | https://thepointsguy.com/news/frequent-flyer-program-hearing-dot-cfpb/ | 2024-05 |
| DOT監察官（OIG）監査 | DOTの苦情審査はFFPにおける不公正・欺瞞的慣行の有無を判断するには不十分 | https://www.oig.dot.gov/library-item/33403 | 不明 |
| Administrative Law Review 77.4（Martone） | DOTのFFP規制権限の限界を論じる。調査結果への言及なし | https://administrativelawreview.org/wp-content/uploads/sites/2/2025/12/ALR-77.4_Martone.pdf | 2025-12 |
| 国民生活センター（2021-03-10）第40回インターネット消費者取引連絡会「ポイントサービス」報告 | 相談例：「付与されたポイントの有効期限が過ぎてしまい、ポイントが失効してしまった」「キャンペーン条件を満たしたのに付与されない」 | https://www.caa.go.jp/policies/policy/consumer_policy/meeting_materials/assets/internet_committee_210329_0004.pdf | 2021-03-10 |
| 国民生活センター（2025-03-28）「キャッシュレス決済が関わる消費生活相談の現状」 | 内閣府消費者委員会 決済ワーキング資料 | https://www.cao.go.jp/consumer/kabusoshiki/payment/doc/003_250328_shiryou1.pdf | 2025-03-28 |
| 国民生活センター 消費者トラブル解説集「電子マネーを使おうとしたら有効期限切れ」 | 有効期限6か月超等の要件を満たす場合は資金決済法の適用。「発行者は有効期限を自由に決めることができ、有効期限を過ぎた電子マネー等は使えなくなり、原則として払い戻しすることはできません」 | https://www.kokusen.go.jp/t_box/data/t_box-faq_qa2019_21.html | 2019 |
| 資金決済法：前払式支払手段の3要件 | 財産的価値／対価と引き換えに発行／代金の支払いに使用可能 | https://corporate.vbest.jp/columns/2124/ ／ https://topcourt-law.com/finance/point_fund_settlement_method | 不明 |
| 資金決済法：適用除外 | 「発行の日から政令で定める一定の期間内（6か月）に限り使用できる前払式支払手段」は適用除外。「ポイントを単なるおまけや景品として発行するものは資金決済法の規制対象外」 | https://aglaw.jp/point-shikinkessaihou/ | 不明 |
| 内閣府消費者委員会 資料6（坂勇一郎弁護士）「決済制度の現状と課題〜資金決済法関連を中心に〜」 | 決済制度・資金決済法の課題整理 | https://www.cao.go.jp/consumer/iinkai/2023/416/doc/20231114_shiryou6_3.pdf | 2023-11-14 |
| 国民生活センター（2020-01-23）特別調査 | 消費者トラブルからみる決済関連の調査（後払い決済中心） | https://www.kokusen.go.jp/pdf/n-20200123_1.pdf | 2020-01-23 |

### Inferences
- 航空マイルは「搭乗やカード利用の対価として無償付与される景品的ポイント」であるため、資金決済法上の前払式支払手段には該当せず、有効期限・価値切り下げ・失効は発行者（航空会社）の約款裁量に委ねられる構造（推定。上記法律事務所解説の一般論からの適用）。これが「公式の円換算価値が存在しない」ことと表裏一体で、ブログの換算値が規制上の歯止めなく流通する土壌になっている。
- 米DOT調査が「1マイルの平均ドル価値」の提出を航空会社に求めた事実は、規制当局も「航空会社内部には1マイルの現金等価値が存在する」と前提していることを示し、モデルで会計上単価を「比較対象」に用いる根拠になる。

### Gaps
- DOT調査の2025年以降の帰結（新政権下での継続・終了、公表の有無）：検索上限により未調査。
- 消費者庁（景品表示法・有利誤認）および公正取引委員会（ポイントサービス実態調査等）のマイルに関する見解：未調査。
- 国民生活センターのマイル固有の相談事例（失効・改悪）：検索結果に該当なし。
