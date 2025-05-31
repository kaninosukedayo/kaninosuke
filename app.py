
import streamlit as st
import json
import os

USER_FILE = "users.json"

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
                "price": 120,
                "comment": "",
                "banned": False,
                "cities": 0,
                "military": 0,
                "kd": 0.0,
                "expect": 0
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
    st.metric("💹 株価", user.get("price", 120))

    # 株数調整（ユーザー自身で）
    st.subheader("🛠 保有株数の調整")
    adjust_amount = st.number_input("増減させる株数（マイナスも可）", step=1, value=0, key="adjust_input")
    if st.button("株数を調整"):
        new_stock = user["stock"] + adjust_amount
        if new_stock < 0:
            st.error("株数を0未満にすることはできません")
        else:
            user["stock"] = new_stock
            save_users(users)
            st.success(f"株数を {new_stock} に更新しました")
            st.experimental_rerun()

    # 他プレイヤーの株を購入
    st.subheader("💸 他プレイヤーの株を購入")
    target = st.selectbox("購入対象ユーザー", [u for u in users if u != username and not users[u].get("banned")])
    buy_amount = st.number_input("購入株数", min_value=1, step=1, key="buy_stock")
    target_price = users[target]["price"]

    if st.button("購入実行"):
        total_price = target_price * buy_amount
        if user["ebi"] >= total_price and users[target]["stock"] >= buy_amount:
            user["ebi"] -= total_price
            users[target]["ebi"] += total_price
            user["stock"] += buy_amount
            users[target]["stock"] -= buy_amount
            save_users(users)
            st.success(f"{target} の株を {buy_amount} 株購入しました！")
            st.experimental_rerun()
        else:
            st.error("エビが足りないか、相手の株が不足しています")

    # コメント編集
    st.subheader("📝 説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

    
# エビ送金
st.subheader("📤 他のプレイヤーにエビを送る")
to_user = st.selectbox("送信先", [u for u in users if u != username])
ebi_amount = st.number_input("送るエビ数", min_value=1, step=1, key="ebi_send")

if st.button("送信"):
    if user["ebi"] >= ebi_amount:
        user["ebi"] -= ebi_amount
        users[to_user]["ebi"] += ebi_amount
        save_users(users)
        st.session_state["message"] = f"{to_user} に {ebi_amount} エビを送信しました！"
        st.session_state["rerun"] = True
    else:
        st.error("エビが足りません")

# メッセージがあれば表示
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

# rerun 実行
if st.session_state.get("rerun"):
    st.session_state["rerun"] = False
    st.experimental_rerun()

    # プレイヤー一覧
    st.subheader("👥 プレイヤー一覧")
    for name, data in users.items():
        if not data.get("banned"):
            st.write(f"🧑‍💼 **{name}** ｜🦐 {data['ebi']} ｜📈 {data['stock']}株 ｜ 💹 株価: {data.get('price', 120)}")
            st.caption(data.get("comment", ""))

    # 管理者パネル
    if username == "admin":
        st.subheader("👮 管理者パネル")

        # BAN機能
        ban_user = st.selectbox("BANするユーザー", [u for u in users if u != "admin"])
        if st.button("BAN実行"):
            users[ban_user]["banned"] = True
            save_users(users)
            st.success(f"{ban_user} をBANしました")
 　　　　
　　　　　# エビの増減機能
        st.subheader("🦐 エビ量の調整")
        target_user = st.selectbox("対象ユーザー", [u for u in users if u != "admin"], key="ebi_target")
        ebi_change = st.number_input("増減させるエビ量（マイナスもOK）", value=0, step=100, key="ebi_change_input")

        if st.button("エビを調整する"):
            users[target_user]["ebi"] += ebi_change
            if users[target_user]["ebi"] < 0:
                users[target_user]["ebi"] = 0  # マイナス防止
            save_users(users)
            if ebi_change >= 0:
                st.success(f"{target_user} に {ebi_change} エビを追加しました")
            else:
                st.success(f"{target_user} のエビを {abs(ebi_change)} 減らしました")
        # 株価自動設定
        st.subheader("📊 株価設定ツール")
        target = st.selectbox("株価を設定するユーザー", [u for u in users if u != "admin"], key="set_price_user")
        cities = st.number_input("都市数", min_value=0, key="cities")
        military = st.number_input("軍の数", min_value=0.0, key="military")
        kd = st.number_input("キルレ", min_value=0.0, key="kd")
        expect = st.number_input("期待値", min_value=0.0, key="expect")

        if st.button("株価自動更新"):
            price = 100 + cities * 2 + military * 0.5 + kd * 10 + expect * 1
            users[target]["price"] = round(price)
            users[target]["cities"] = cities
            users[target]["military"] = military
            users[target]["kd"] = kd
            users[target]["expect"] = expect
            save_users(users)
            st.success(f"{target} の株価を {round(price)} に設定しました")

# アプリ起動
if "username" not in st.session_state:
    login()
else:
    home()

