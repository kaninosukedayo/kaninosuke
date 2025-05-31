import streamlit as st
import json
import os

# ユーザーデータの保存ファイル
USER_FILE = "users.json"
STOCK_PRICE = 120  # 株価（管理者が決めた値）

# 初期データ作成
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

# ログイン機能
def login():
    st.title("投資ゲームログイン")
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
                "banned": False
            }
            save_users(users)
            st.success("登録完了！ログインしてください")

# ホーム画面
def home():
    st.title("🦐 投資ゲーム ホーム")
    username = st.session_state["username"]
    user = users[username]

    # BAN確認
    if user.get("banned"):
        st.error("あなたのアカウントは凍結されています。")
        return

    st.write(f"### ようこそ、{username}さん")
    st.metric("🦐 エビ", user["ebi"])
    st.metric("📈 保有株数", user["stock"])
    st.metric("💹 株価", STOCK_PRICE)

    # 株の売買
    st.subheader("株の売買")
    action = st.radio("売買選択", ["購入", "売却"])
    amount = st.number_input("株数", min_value=1, step=1)

    if st.button("実行"):
        if action == "購入":
            total = STOCK_PRICE * amount
            if user["ebi"] >= total:
                user["ebi"] -= total
                user["stock"] += amount
                st.success(f"{amount}株 購入しました！")
            else:
                st.error("エビが足りません")
        else:
            if user["stock"] >= amount:
                user["stock"] -= amount
                user["ebi"] += STOCK_PRICE * amount
                st.success(f"{amount}株 売却しました！")
            else:
                st.error("株が足りません")

        save_users(users)
        st.experimental_rerun()

    # コメント編集
    st.subheader("説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

    # エビ送金
    st.subheader("他のプレイヤーにエビを送る")
    to_user = st.selectbox("送信先", [u for u in users if u != username])
    ebi_amount = st.number_input("送るエビ数", min_value=1, step=1)
    if st.button("送信"):
        if user["ebi"] >= ebi_amount:
            user["ebi"] -= ebi_amount
            users[to_user]["ebi"] += ebi_amount
            save_users(users)
            st.success(f"{to_user} に {ebi_amount}エビを送信しました！")
        else:
            st.error("エビが足りません")

    # ユーザー一覧
    st.subheader("プレイヤー一覧")
    for name, data in users.items():
        if not data.get("banned"):
            st.write(f"🧑‍💼 **{name}** ｜🦐 {data['ebi']} ｜📈 {data['stock']}株")
            st.caption(data.get("comment", ""))

    # 管理者機能（"admin"ユーザー限定）
    if username == "admin":
        st.subheader("👮 管理者パネル")
        ban_user = st.selectbox("BANするユーザー", [u for u in users if u != "admin"])
        if st.button("BAN実行"):
            users[ban_user]["banned"] = True
            save_users(users)
            st.success(f"{ban_user} をBANしました")

# アプリ本体
if "username" not in st.session_state:
    login()
else:
    home()
