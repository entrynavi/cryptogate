#!/usr/bin/env python3
"""
毎日実行: SNS投稿コンテンツを自動生成
X(Twitter)/Bluesky/Threads/Pinterest用
ですます調 + 初心者向け + 画像対応
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
day_of_year = today.timetuple().tm_yday
date_str = today.strftime("%Y-%m-%d")

BASE = "https://entrynavi.github.io/cryptogate"

# 投稿に添付する画像（imgディレクトリ内のファイル名）
# post_bluesky.py がこの情報を使って画像を添付する
IMAGES = {
    "ranking": "img/pin-ranking.png",
    "hyperliquid": "img/pin-hyperliquid.png",
    "wallet": "img/pin-wallet.png",
    "hajimekata": "img/pin-hajimekata.png",
    "defi": "img/pin-defi.png",
}

# ========== 投稿テンプレート ==========
# ですます調 + 初心者向けのわかりやすい解説
# 各投稿は (text, image_key or None) のタプル

EXCHANGE_POSTS = [
    # --- MEXC ---
    (f"""MEXCという海外取引所をご存じですか？

取引手数料がメイカー0%で、取扱通貨は2,700種類以上あります。まだ日本では知られていない通貨も多く取り扱っていて、早めに見つけたい方にはおすすめです。

詳しくはこちら
{BASE}/mexc/

#MEXC #仮想通貨 #取引所""", "ranking"),

    (f"""「海外取引所ってどこを使えばいいの？」とよく聞かれます。

迷ったらMEXCがおすすめです。理由はシンプルで、手数料が安い・通貨が多い・日本語に対応しているからです。

始め方はこちらにまとめています
{BASE}/mexc/

#MEXC""", None),

    (f"""MEXCの特徴のひとつが、新しい通貨の上場スピードです。話題になったコインをすぐに取引できるので、情報を追っている方には便利な取引所です。

{BASE}/mexc/""", None),

    (f"""MEXCでは定期的にエアドロップイベントが開催されています。口座を持っておくだけで参加できるキャンペーンもありますので、登録しておくと便利です。

{BASE}/mexc/

#MEXC #エアドロップ""", None),

    (f"""MEXCは日本語表示に対応した海外取引所です。英語が苦手な方でも操作に困ることはありません。スマートフォンアプリも使いやすいと好評です。

詳しくはこちら
{BASE}/mexc/

#MEXC #海外取引所""", "ranking"),

    (f"""海外取引所の中でもMEXCは取扱通貨の多さが魅力です。国内では購入できないアルトコインを探している方にとって、選択肢の幅が大きく広がります。

{BASE}/mexc/

#MEXC #アルトコイン""", None),

    # --- Bitget ---
    (f"""「自分でチャートを分析するのは難しい…」という方には、Bitgetのコピートレードがおすすめです。

プロのトレーダーの売買を自動でコピーできる機能で、初心者の方でも始めやすい仕組みになっています。

詳しくはこちら
{BASE}/bitget/

#Bitget #コピートレード""", "ranking"),

    (f"""Bitgetのコピートレードは利用者数が世界トップクラスです。

成績の良いトレーダーを選ぶだけなので、取引の経験が少ない方でも始めやすいのが特徴です。

{BASE}/bitget/""", None),

    (f"""Bitgetはセキュリティ面でも信頼性の高い取引所です。ユーザー資産の保護基金を設けており、万が一に備えた体制が整っています。

{BASE}/bitget/

#Bitget #セキュリティ""", None),

    (f"""Bitgetではデモトレード機能も用意されています。実際のお金を使わずに取引の練習ができるので、初めての方でも安心して操作を覚えられます。

{BASE}/bitget/

#Bitget #デモトレード""", None),

    (f"""Bitgetは世界150カ国以上で利用されている大手取引所です。先物取引やコピートレードなど、中級者以上の方にも対応した機能が充実しています。

{BASE}/bitget/

#Bitget""", "ranking"),

    # --- Coincheck ---
    (f"""仮想通貨を始めてみたいけど不安…という方には、Coincheckがおすすめです。

金融庁に登録された国内取引所で、500円から購入できます。アプリも使いやすく、初めての方に人気があります。

今なら紹介で1,500円分のBTCがもらえます
{BASE}/coincheck/

#Coincheck #仮想通貨デビュー""", "ranking"),

    (f"""Coincheckの紹介キャンペーンが実施中です。口座を開設するだけで1,500円分のビットコインがもらえます。

まだ口座をお持ちでない方はこの機会にどうぞ
{BASE}/coincheck/""", None),

    (f"""Coincheckは国内で最も知名度の高い取引所のひとつです。操作画面がシンプルなので、初めてアプリを開いた方でも迷わず使えます。

{BASE}/coincheck/

#Coincheck""", None),

    (f"""Coincheckではビットコインの積立投資ができます。毎月一定額を自動で購入してくれるので、価格変動を気にせず投資を続けられます。

{BASE}/coincheck/

#Coincheck #積立投資""", None),

    # --- Binance Japan ---
    (f"""世界最大級の取引所Binanceが、日本向けにサービスを提供しています。金融庁に登録されているので、安心して利用できます。

{BASE}/binance-japan/

#BinanceJapan #仮想通貨""", None),

    (f"""Binance Japanでは50種類以上の通貨を取り扱っています。世界最大級の取引所の技術力を活かしつつ、日本の法律に準拠したサービスです。

{BASE}/binance-japan/

#BinanceJapan""", None),

    (f"""国内取引所で取扱通貨の多さを重視するなら、Binance Japanがおすすめです。グローバルな取引所の信頼性と、国内規制への対応を両立しています。

{BASE}/binance-japan/

#BinanceJapan #国内取引所""", None),

    # --- Hyperliquid ---
    (f"""Hyperliquidという分散型取引所（DEX）が注目されています。

CEX（中央集権型）と同じくらいスムーズに取引でき、ガス代（手数料）は0円です。過去のエアドロップで大きなリターンを得た方も多く、今から触っておく価値があります。

始め方はこちら
{BASE}/hyperliquid/

#Hyperliquid #エアドロップ""", "hyperliquid"),

    (f"""Hyperliquidが話題になっている理由は、前回のエアドロップで数百万円相当を受け取った方がいたからです。

次のエアドロップに向けて、今のうちに使い始めておくのがおすすめです。

{BASE}/hyperliquid/""", "hyperliquid"),

    (f"""分散型取引所（DEX）の中でも、Hyperliquidは操作性が優れています。中央集権型と変わらない使い心地で、すべてオンチェーンで完結します。

{BASE}/hyperliquid/""", None),

    (f"""Hyperliquidはすべての取引がオンチェーンで記録されるため、透明性の高い取引環境が特徴です。独自のL1チェーン上で高速に動作します。

{BASE}/hyperliquid/

#Hyperliquid #DEX""", "hyperliquid"),

    (f"""中央集権型の取引所に資産を預けることに不安がある方には、Hyperliquidのような分散型取引所がおすすめです。ウォレットから直接取引できます。

{BASE}/hyperliquid/

#Hyperliquid #分散型""", None),
]

PRODUCT_POSTS = [
    # --- Tria ---
    (f"""Triaというウォレットをご紹介します。メールアドレスだけでWeb3ウォレットが作れます。

秘密鍵やシードフレーズの管理が不要なので、Web3が初めての方でも安心です。招待制のため、以下のリンクからどうぞ。

https://app.tria.so/?accessCode=C77B6U2297

#Tria #Web3ウォレット""", "wallet"),

    (f"""Web3ウォレットの中で一番簡単に使えるのはTriaかもしれません。

メールアドレスだけで登録でき、シードフレーズを覚える必要がありません。初めてのウォレットにおすすめです。

https://app.tria.so/?accessCode=C77B6U2297""", None),

    (f"""Web3を始めたいけどウォレットの設定が難しそう…という方にはTriaがおすすめです。メールアドレスだけで登録が完了します。

https://app.tria.so/?accessCode=C77B6U2297

#Tria #Web3""", "wallet"),

    # --- Wefi ---
    (f"""WefiというDeFiアグリゲーターが使いやすいです。

複数のDeFiプロトコルをまとめて操作できるので、DeFiを始めたい方にとって便利なツールです。

https://app.wefi.co/register?ref=m05h1tblot

#Wefi #DeFi入門""", "defi"),

    (f"""DeFiに興味はあるけど、どこから始めればよいかわからない方にはWefiがおすすめです。複数のプロトコルを一つの画面で管理できます。

https://app.wefi.co/register?ref=m05h1tblot

#Wefi #DeFi""", "defi"),

    (f"""Wefiを使えば、最適なDeFiプロトコルを効率的に比較できます。利回りの確認も簡単にできるので、運用先を探している方に便利です。

https://app.wefi.co/register?ref=m05h1tblot

#Wefi""", None),

    # --- Ledger ---
    (f"""仮想通貨を長期で保有する場合、ハードウェアウォレットの利用をおすすめします。

取引所に預けたままだと、万が一のハッキング時にリスクがあります。Ledgerならオフラインで秘密鍵を管理できるので安心です。

https://shop.ledger.com/?r=f80cdb813871

#Ledger #セキュリティ""", "wallet"),

    (f"""取引所のハッキング事件は毎年のように起きています。ご自身の資産を守るために、ハードウェアウォレットを一つ持っておくことをおすすめします。

Ledgerは世界で最も利用されているハードウェアウォレットです。

https://shop.ledger.com/?r=f80cdb813871""", None),

    (f"""仮想通貨を安全に保管するなら、Ledgerの導入をおすすめします。初期設定は日本語ガイドに沿って進めるだけなので、初めての方でも簡単です。

https://shop.ledger.com/?r=f80cdb813871

#Ledger #ハードウェアウォレット""", "wallet"),

    # --- SafePal ---
    (f"""Ledgerより手頃な価格のハードウェアウォレットをお探しなら、SafePalもおすすめです。コストパフォーマンスが良く、しっかりとセキュリティを確保できます。

https://www.safepal.com/store/s1?ref=ntu0oth

#SafePal #ウォレット""", "wallet"),

    (f"""SafePalはBinanceが出資しているハードウェアウォレットです。手頃な価格でありながら、セキュリティ機能が充実しています。

https://www.safepal.com/store/s1?ref=ntu0oth

#SafePal""", None),

    (f"""ハードウェアウォレットは高価なイメージがありますが、SafePalなら比較的お手頃な価格で入手できます。スマホアプリとの連携も簡単です。

https://www.safepal.com/store/s1?ref=ntu0oth

#SafePal #セキュリティ""", "wallet"),

    # --- edgeX ---
    (f"""edgeXという分散型取引所をご紹介します。Hyperliquidと同じオーダーブック型のDEXで、UIが洗練されていて日本語にも対応しています。

https://pro.edgex.exchange/ja-JP/referral/ZEROMEMO

#edgeX #DEX""", None),

    (f"""edgeXは日本語に完全対応した分散型取引所です。手数料が低く先物取引もできるため、コストを重視する方におすすめです。

https://pro.edgex.exchange/ja-JP/referral/ZEROMEMO

#edgeX""", None),

    # --- GMGN ---
    (f"""ミームコインのトレンドをリアルタイムで追いたい方にはGMGNが便利です。

トークンの値動きや取引量をすぐに確認できるので、情報収集のツールとしておすすめです。

https://gmgn.ai/r/MAKAI

#GMGN #ミームコイン""", None),

    (f"""GMGNを使うと、注目されているトークンをいち早く見つけることができます。ウォレット分析機能もあり、市場動向の把握に役立ちます。

https://gmgn.ai/r/MAKAI

#GMGN""", None),

    (f"""ミームコインの情報収集には専用ツールがあると便利です。GMGNではトレンドランキングやスマートマネーの動きをリアルタイムで確認できます。

https://gmgn.ai/r/MAKAI

#GMGN #ミームコイン""", None),

    # --- DeBot ---
    (f"""DeBotはAIを活用したDeFi自動運用ツールです。

まだ新しいサービスですが、自動でDeFiの運用をしてくれるので注目しています。興味のある方はぜひ試してみてください。

https://inv.debot.ai/r/294452?lang=ja

#DeBot #AI運用""", None),

    (f"""DeFiの運用を自動化したい方にはDeBotがおすすめです。AIが市場を分析し、最適な運用戦略を提案してくれます。

https://inv.debot.ai/r/294452?lang=ja

#DeBot #AI""", "defi"),

    (f"""DeBotのAI運用ツールは、DeFi初心者の方でも使いやすい設計になっています。難しい操作は不要で、AIに運用を任せることができます。

https://inv.debot.ai/r/294452?lang=ja

#DeBot""", None),
]

EDUCATION_POSTS = [
    # --- 確定申告・税金 ---
    (f"""仮想通貨で利益が出た場合、確定申告が必要です。申告しないと追徴課税の対象になることもあります。

計算方法や節税のポイントをこちらにまとめていますので、ぜひご確認ください。
{BASE}/trending/tax-crypto-japan/

#仮想通貨 #確定申告""", None),

    (f"""仮想通貨の利益は「雑所得」として計算されます。他の収入と合算されるため、場合によっては高い税率が適用されることもあります。

事前に仕組みを理解しておくことが大切です。
{BASE}/trending/tax-crypto-japan/

#仮想通貨 #税金""", None),

    (f"""仮想通貨の確定申告では、損益計算ツールを活用すると効率的です。取引履歴をアップロードするだけで自動計算してくれるサービスもあります。

{BASE}/trending/tax-crypto-japan/

#確定申告 #仮想通貨""", None),

    # --- シードフレーズ ---
    (f"""シードフレーズをスクリーンショットで保存していませんか？

スマートフォンが乗っ取られた場合、資産をすべて失うリスクがあります。安全な管理方法をこちらで解説しています。
{BASE}/trending/seed-phrase/

#セキュリティ #シードフレーズ""", "wallet"),

    (f"""シードフレーズは、ウォレットを復元するための唯一の手段です。紛失すると資産にアクセスできなくなります。

紙に書いて安全な場所に保管することをおすすめします。
{BASE}/trending/seed-phrase/

#シードフレーズ""", "wallet"),

    # --- ガス代 ---
    (f"""ETHのガス代（手数料）が高いと感じている方は、L2（レイヤー2）を使ってみてください。

ArbitrumやOptimismなどを利用すると、手数料を大幅に抑えることができます。
{BASE}/trending/gas-fee-guide/

#イーサリアム #L2""", None),

    (f"""ブロックチェーンの手数料（ガス代）は、ネットワークの混雑状況で変動します。取引のタイミングを工夫するだけでも、コストを抑えることができます。

{BASE}/trending/gas-fee-guide/

#ガス代 #節約""", None),

    # --- DeFi ---
    (f"""DeFiでは年利10%以上のリターンが得られることもありますが、その分リスクもあります。

ラグプル（詐欺）やハッキングなどの危険性を理解した上で始めることが大切です。
{BASE}/trending/defi-toha/

#DeFi #リスク管理""", "defi"),

    (f"""DeFi（分散型金融）とは、銀行などの仲介者なしで金融サービスを利用できる仕組みです。レンディングやスワップなど、さまざまな機能があります。

{BASE}/trending/defi-toha/

#DeFi入門""", "defi"),

    (f"""DeFiを始める前に、リスクについて知っておくことが大切です。スマートコントラクトの脆弱性など、基本的な知識を身につけてから始めましょう。

{BASE}/trending/defi-toha/

#DeFi #セキュリティ""", None),

    # --- ステーキング ---
    (f"""ステーキングとは、仮想通貨を預けて報酬を受け取る仕組みです。銀行預金よりも高い利回りが期待できます。

初心者向けの始め方ガイドはこちらです。
{BASE}/trending/staking-guide/

#ステーキング #仮想通貨""", None),

    (f"""ステーキングは、保有している仮想通貨をネットワークに預けて報酬を得る仕組みです。長期保有をお考えの方に適した運用方法です。

{BASE}/trending/staking-guide/

#ステーキング""", None),

    (f"""ステーキングを始めるには、まず対応通貨を購入する必要があります。ETHやSOLなど、主要な通貨でステーキングが可能です。

始め方はこちら
{BASE}/trending/staking-guide/

#ステーキング入門""", None),

    # --- ウォレット選び ---
    (f"""仮想通貨を取引所に置きっぱなしにしていませんか？

取引所がハッキングされると、預けていた資産を失う可能性があります。自分専用のウォレットを持つことをおすすめします。
{BASE}/trending/wallet-erabikata/

#ウォレット #セキュリティ""", "wallet"),

    (f"""ウォレットには「ホットウォレット」と「コールドウォレット」の2種類があります。それぞれの特徴を知っておくと、資産管理がしやすくなります。

{BASE}/trending/wallet-erabikata/

#ウォレット選び""", "wallet"),

    # --- 始め方 ---
    (f"""仮想通貨の始め方は意外とシンプルです。

1. 取引所で口座を開設する（約5分）
2. 日本円を入金する
3. 好きな通貨を購入する

詳しい手順はこちらにまとめています。
{BASE}/hajimekata/

#仮想通貨の始め方""", "hajimekata"),

    (f"""仮想通貨投資は少額から始めるのがおすすめです。まずは500円〜1,000円程度で購入して、実際の値動きを体感してみてください。

{BASE}/hajimekata/

#仮想通貨の始め方""", "hajimekata"),

    (f"""仮想通貨投資で大切なのは、余裕資金で始めることです。生活費には手をつけず、なくなっても困らない金額から始めましょう。

基本的な始め方はこちら
{BASE}/hajimekata/

#投資の基本""", None),

    # --- ランキング ---
    (f"""取引所選びで迷っている方のために、手数料・取扱通貨数・セキュリティなどを一覧で比較できる表を作りました。

ぜひ参考にしてみてください。
{BASE}/ranking/

#取引所比較 #仮想通貨""", "ranking"),

    (f"""仮想通貨取引所を選ぶポイントは、手数料・取扱通貨数・セキュリティの3つです。ご自身の目的に合った取引所を選びましょう。

比較表はこちら
{BASE}/ranking/

#取引所選び""", "ranking"),
]

# ========== 日替わり選択 ==========
weekday = today.weekday()

if weekday in (0, 2, 4):  # Mon, Wed, Fri
    pool = EXCHANGE_POSTS + PRODUCT_POSTS
    post_type = "promo"
else:
    pool = EDUCATION_POSTS + PRODUCT_POSTS
    post_type = "education"

idx = (day_of_year * 7 + weekday) % len(pool)
post_text, image_key = pool[idx]

# ========== 出力 ==========
social_dir = Path("social")
social_dir.mkdir(exist_ok=True)

today_file = social_dir / f"{date_str}.txt"
today_file.write_text(post_text, encoding="utf-8")

(social_dir / "latest.txt").write_text(post_text, encoding="utf-8")

meta = {
    "date": date_str,
    "type": post_type,
    "char_count": len(post_text),
    "image": IMAGES.get(image_key) if image_key else None,
}
(social_dir / f"{date_str}.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
)

# 週間スケジュール
schedule = []
for i in range(7):
    d = today + timedelta(days=i)
    wd = d.weekday()
    day_name = ["月", "火", "水", "木", "金", "土", "日"][wd]
    ct = "プロモ" if wd in (0, 2, 4) else "教育/プロダクト"
    schedule.append(f"{d.strftime('%-m/%-d')}({day_name}) {ct}")

(social_dir / "schedule.txt").write_text(
    "今週のスケジュール\n" + "\n".join(schedule) + "\n",
    encoding="utf-8",
)

print(f"SNS content: {date_str} ({post_type})")
print(f"Length: {len(post_text)} chars")
if image_key:
    print(f"Image: {IMAGES[image_key]}")
