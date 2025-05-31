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
                "stock_price": DEFAULT_STOCK_PRICE,
                "stock_for_sale": 0  # ここを追加：売りに出している株数
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
    st.metric("🔄 売りに出している株数", user.get("stock_for_sale", 0))

    # 自分の株を売りに出す株数を調節できる
    st.subheader("自分の株を売りに出す数の調節")
    max_sellable = user["stock"]
    sell_for_market = st.number_input(
        "売りに出す株数を設定してください", 
        min_value=0, max_value=max_sellable, step=1, 
        value=user.get("stock_for_sale", 0)
    )
    if st.button("売りに出す株数を更新"):
        user["stock_for_sale"] = sell_for_market
        save_users(users)
        st.success(f"売りに出す株数を {sell_for_market} に更新しました")

    # 株の売買（買う側）
    st.subheader("他プレイヤーの株を買う")
    # 売りに出している株数があるユーザーのみ選択肢に表示
    sellers = [u for u in users if u != username and not users[u]["banned"] and users[u].get("stock_for_sale", 0) > 0]
    if sellers:
        target_user = st.selectbox("購入対象プレイヤー", sellers)
        target_user_data = users[target_user]
        max_buy = target_user_data.get("stock_for_sale", 0)
        target_stock_price = target_user_data["stock_price"]
        st.write(f"{target_user} の株価: {target_stock_price} エビ")
        buy_amount = st.number_input("購入株数", min_value=1, max_value=max_buy, step=1)

        if st.button("購入実行"):
            total_cost = buy_amount * target_stock_price
            if user["ebi"] < total_cost:
                st.error("エビが足りません")
            else:
                # 買い手のエビ減少、株増加
                user["ebi"] -= total_cost
                user["stock"] += buy_amount

                # 売り手のエビ増加、株減少、売りに出している株数も減少
                target_user_data["ebi"] += total_cost
                target_user_data["stock"] -= buy_amount
                target_user_data["stock_for_sale"] -= buy_amount

                save_users(users)
                st.success(f"{target_user} の株を {buy_amount} 株購入しました！")
    else:
        st.info("現在売りに出している株を持つユーザーはいません。")

    # コメント編集
    st.subheader("説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

    # 他の機能は管理者パネル等お好みで継続可能です

if "username" not in st.session_state:
    login()
else:
    home()







