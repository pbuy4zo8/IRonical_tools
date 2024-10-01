import streamlit as st

import pandas as pd

scimag_df = pd.read_csv("./scimagojr_2023_zero.csv")
wos_df = pd.read_csv("./wos_q1_zero.csv")

st.set_page_config(layout="wide", page_title="Q1_check")

st.title("Q1 journal checker (ver. 0.1)")
st.write("You can check Q1 journal list of the 2024 APC support service.")
st.write("This is a simple check system, so we recommend searching in database to be sure.")
st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> check database")
st.write("")


input_text = st.text_input("input journal's ISSN", "")
st.write("")
st.write("")

if input_text:
    input_text_re = input_text.replace("-", "")

    result_scimag_issn_df = scimag_df.query("ISSN == @input_text_re or eISSN == @input_text_re")

    st.markdown("### Search result of Scientific Journal Rankings")
    if len(result_scimag_issn_df) > 0:
        st.write(" As a result of searching on " + str(input_text_re) + ", the following journals were found.")
        st.dataframe(result_scimag_issn_df, hide_index=True)
    elif len(result_scimag_issn_df) == 0:
        # st.write("ISSN: " + str(input_text_re) + "は，今回のAPC支援制度の対象ではないようです．")
        st.write("We cannot find it in Scientific Journal Rankings.")

    result_wos_issn_df = wos_df.query("ISSN == @input_text_re or eISSN == @input_text_re")
    st.markdown("### Search result of Journal Citation Reports")
    if len(result_wos_issn_df) > 0:
        st.write(" As a result of searching on " + str(input_text_re) + ", the following journals were found.")
        st.dataframe(result_wos_issn_df, hide_index=True)
    elif len(result_wos_issn_df) == 0:
    #     st.write("ISSN: " + str(input_text_re) + "は，今回のAPC支援制度の対象ではないようです．")
        st.write("We cannot find it in Journal Citation Reports.")

    st.write("")
    st.write("")
    st.write("")

    if len(result_scimag_issn_df) > 0 or len(result_wos_issn_df) > 0:
        st.write("Please check here before applying.")
        st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> Library's Webpage")
    
    elif len(result_scimag_issn_df) == 0 and len(result_wos_issn_df) == 0:
        st.write("We cannot find ISSN: " + str(input_text_re) + ". Please search in database to be sure.")
        st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> Library's Webpage")
    st.write("")

st.write("written by Kensuke Kobayashi, Okayama Univ. URA")