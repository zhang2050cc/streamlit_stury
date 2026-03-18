
import os
from typing import Optional, Tuple

import streamlit as st
from supabase import Client, create_client


def get_supabase_config() -> Tuple[Optional[str], Optional[str]]:
    """Load Supabase config from Streamlit secrets or environment variables."""
    try:
        supabase = st.secrets["supabase"]
        return supabase.get("URL"), supabase.get("KEY")
    except Exception:
        return os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")


@st.cache_resource
def init_supabase_client() -> Client:
    url, key = get_supabase_config()
    if not url or not key:
        raise RuntimeError(
            "未配置 Supabase URL/KEY。请在 .streamlit/secrets.toml 中添加，"
            "或设置 SUPABASE_URL/SUPABASE_KEY 环境变量。"
        )
    return create_client(url, key)


def login_or_signup(supabase: Client) -> None:
    st.header("登录 / 注册")
    email = st.text_input("邮箱")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        if not email or not password:
            st.error("请输入邮箱和密码")
            return
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if result:
                st.success("登录成功！")
                st.session_state.user = result
                st.session_state.session = result.session
                st.rerun()
            else:
                st.error("登录失败，检查邮箱/密码是否正确。")
        except Exception as e:
            st.error(f"登录时出错：{e}")
        return

    if st.button("注册"):
        if not email or not password:
            st.error("请输入邮箱和密码")
            return
        try:
            auth = supabase.auth.sign_up({"email": email, "password": password})
            st.write(auth.user.id)
            st.success("注册成功！请登录。")
        except Exception as e:
            st.error(f"注册时出错：{e}")
        return


def main() -> None:
    st.title("我的应用")

    try:
        supabase = init_supabase_client()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        st.markdown(f"欢迎，**{st.session_state.user.user.email}**！")
        #st.write(supabase.auth.get_user().user.email)
        if st.button("登出"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.session = None
            st.rerun()
    else:
        login_or_signup(supabase)


if __name__ == "__main__":
    main()
    
    


