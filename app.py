import streamlit as st
import json
import os

USER_FILE = "users.json"
DEFAULT_STOCK_PRICE = 120

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

def login():
    st.title("投資ゲーム ログイン")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        if username in users and users[username]["password"] == password:
            st.session_state["username"] = username
            st.success("ログイン成功！")
            st.experimental_rerun()
        else:
            st.error("ユーザー名またはパスワードが間違っています")

    if st.button("新規登録"):
        if username in users:
            st.error("このユーザー名は既に存在します")
        else:
            users[username] = {
                "password": password,
                "ebi": 5000,
                "stock": 0,
                "comment": "",
                "banned": False,
                "stock_price": DEFAULT_STOCK_PRICE
            }
            save_users(users)
            st.success("登録完了！ログインしてください")

def home():
    st.title("🦐 投資ゲーム ホーム")
    username = st.session_state["username"]
    user = users[username]

    if user.get("banned"):
        st.error("あなたのアカウントは凍結されています。")
        return

    st.write(f"### ようこそ、{username}さん")
    st.metric("🦐 エビ", user["ebi"])
    st.metric("📈 保有株数", user["stock"])
    st.metric("💹 あなたの株価", user["stock_price"])

    st.subheader("株の売買")
    trade_action = st.radio("売買選択", ["購入", "売却"])

    if trade_action == "購入":
        target_user = st.selectbox("購入対象プレイヤー", [u for u in users if u != username and not users[u]["banned"]])
        target_stock_price = users[target_user]["stock_price"]
        st.write(f"{target_user} の株価: {target_stock_price} エビ")
        trade_amount = st.number_input("購入株数", min_value=1, step=1, key="buy_amount")

        if st.button("購入実行"):
            total = target_stock_price * trade_amount
            if user["ebi"] >= total:
                user["ebi"] -= total
                user["stock"] += trade_amount
                if users[target_user]["ebi"] >= total:
                    users[target_user]["ebi"] -= total
                else:
                    users[target_user]["ebi"] = 0
                save_users(users)
                st.success(f"{target_user} の株を {trade_amount} 株購入しました！")
            else:
                st.error("エビが足りません")

    else:
        if user["stock"] > 0:
            sell_amount = st.number_input("売りに出す株数", min_value=1, max_value=user["stock"], step=1, key="sell_amount")
            if st.button("売却実行"):
                user["stock"] -= sell_amount
                user["ebi"] += user["stock_price"] * sell_amount
                save_users(users)
                st.success(f"{sell_amount} 株 売却しました！")
        else:
            st.info("売却できる株がありません")

    st.subheader("説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

    st.subheader("他のプレイヤーにエビを送る")
    to_user = st.selectbox("送信先", [u for u in users if u != username and not users[u]["banned"]], key="send_user")
    ebi_amount = st.number_input("送るエビ数", min_value=1, step=1, key="send_amount")
    if st.button("送信"):
        if user["ebi"] >= ebi_amount:
            user["ebi"] -= ebi_amount
            users[to_user]["ebi"] += ebi_amount
            save_users(users)
            st.success(f"{to_user} に {ebi_amount} エビを送信しました！")
        else:
            st.error("エビが足りません")

    st.subheader("プレイヤー一覧")
    for name, data in users.items():
        if not data.get("banned"):
            st.write(f"🧑‍💼 **{name}** ｜🦐 {data['ebi']} ｜📈 {data['stock']} 株 ｜💹 株価: {data['stock_price']}")
            st.caption(data.get("comment", ""))

    if username == "admin":
        st.subheader("👮 管理者パネル")

        ban_user = st.selectbox("BANするユーザー", [u for u in users if u != "admin"])
        if st.button("BAN実行"):
            users[ban_user]["banned"] = True
            save_users(users)
            st.success(f"{ban_user} をBANしました")

        st.markdown("---")

        st.subheader("🦐 エビ量の調整")
        target_user = st.selectbox("対象ユーザー", [u for u in users if u != "admin"], key="ebi_target")
        ebi_change = st.number_input("増減させるエビ量（マイナスも可）", value=0, step=100, key="ebi_change")
        if st.button("エビを調整する"):
            users[target_user]["ebi"] += ebi_change
            if users[target_user]["ebi"] < 0:
                users[target_user]["ebi"] = 0
            save_users(users)
            st.success(f"{target_user} のエビを {'増加' if ebi_change >= 0 else '減少'} させました")

        st.subheader("💹 株価自動計算")
        calc_user = st.selectbox("株価を計算するユーザー", [u for u in users if u != "admin"], key="stock_calc_user")
        base = 100
        city = st.number_input("都市数", min_value=0, step=1)
        army = st.number_input("軍の数", min_value=0.0, step=0.5)
        kill_rate = st.number_input("キルレ (K/D)", min_value=0.0, step=0.1)
        expect = st.number_input("私の期待値", min_value=0.0, step=1.0)

        if st.button("株価を計算して反映"):
            price = int(base + city * 2 + army * 0.5 + kill_rate * 10 + expect * 1)
            users[calc_user]["stock_price"] = price
            save_users(users)
            st.success(f"{calc_user} の株価を {price} に設定しました")

if "username" not in st.session_state:
    login()
else:
    home()






