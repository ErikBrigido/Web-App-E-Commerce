import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title, hide_pages
# import sys
# import os

# # Adicionar o diretório pai ao caminho de busca de módulos
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Flash_vendas import cards_vendas
st.set_page_config(layout='wide',page_icon = "foto1.png",initial_sidebar_state='expanded')

def main():
    st.markdown(
        """
        <style>
        .st-emotion-cache-lnugh9.eczjsme5 {
            color: White; /* Defina a cor desejada */
        }
        </style>
        <style>
        .st-emotion-cache-10qxj85.eczjsme5 {
            color: White; /* Defina a cor desejada */
        }
        </style>
        <style>
        .st-emotion-cache-6owzu9.e1y5xkzn3 {
            color: White; /* Defina a cor desejada */
        }
        </style>
        """,

        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()

cards_vendas()