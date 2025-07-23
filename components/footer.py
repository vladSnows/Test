import streamlit as st

def render_footer():
    st.markdown(
        """
        <style>
        .center-footer {
            position: fixed;
            left: 50%;
            bottom: 0;
            transform: translateX(-50%);
            width: max-content;
            padding: 10px 24px;
            text-align: center;
            font-size: 0.9em;
            color: gray;
            background: #fff;
            z-index: 9999;
        }
        </style>
        <div class="center-footer">
            Made with ❤️ from HUTA
        </div>
        """,
        unsafe_allow_html=True
    )
