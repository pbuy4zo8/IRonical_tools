import streamlit as st
import datetime
import pandas as pd

scimag_df = pd.read_csv("./scimagojr_2023_zero.csv")
wos_df = pd.read_csv("./wos_q1_zero.csv")

st.set_page_config(layout="wide", page_title="Q1_check")

st.title("Q1 journal checker (ver. 0.1)")
st.write("2024年度APC支援制度の対象となるQ1ジャーナルを簡易チェックできます。")
st.write("簡易チェックなので、見つからない場合は念のため、対象のDBも検索してください。")
st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> DBで確認")
st.write("")


input_text = st.text_input("ジャーナルのISSNを入力してください", "")
st.write("")
st.write("")

if input_text:
    # save searched text to csv
    try:
        dt = datetime.datetime.now()
        with open("./searched_text.csv", "a", encoding="utf_8_sig") as f:
            f.write(str(dt) + "," + str(input_text) + "\n")
    except:
        print("file load failed...")
        
    input_text_re = input_text.replace("-", "")

    result_scimag_issn_df = scimag_df.query("ISSN == @input_text_re or eISSN == @input_text_re")

    st.markdown("### Scientific Journal Rankingsの検索結果")
    if len(result_scimag_issn_df) > 0:
        st.write(str(input_text_re) + " で検索した結果，以下のジャーナルが見つかりました．")
        st.dataframe(result_scimag_issn_df, hide_index=True)
    elif len(result_scimag_issn_df) == 0:
        # st.write("ISSN: " + str(input_text_re) + "は，今回のAPC支援制度の対象ではないようです．")
        st.write("Scientific Journal Rankingsでは見つかりませんでした．")

    result_wos_issn_df = wos_df.query("ISSN == @input_text_re or eISSN == @input_text_re")
    st.markdown("### Journal Citation Reportsの検索結果")
    if len(result_wos_issn_df) > 0:
        st.write(str(input_text_re) + " で検索した結果，以下のジャーナルが見つかりました．")
        st.dataframe(result_wos_issn_df, hide_index=True)
    elif len(result_wos_issn_df) == 0:
    #     st.write("ISSN: " + str(input_text_re) + "は，今回のAPC支援制度の対象ではないようです．")
        st.write("Journal Citation Reportsでは見つかりませんでした．")

    st.write("")
    st.write("")
    st.write("")

    if len(result_scimag_issn_df) > 0 or len(result_wos_issn_df) > 0:
        st.write("こちらをご確認の上、申請ください")
        st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> 図書館Webページ")
    
    elif len(result_scimag_issn_df) == 0 and len(result_wos_issn_df) == 0:
        st.write("ISSN: " + str(input_text_re) + "は見つかりませんでした。念のため、対象のDBも検索してください。")
        st.page_link("https://www.lib.okayama-u.ac.jp/campusonly_cms/apc_q1.html#Description", label="-> 確認方法はこちら")
    st.write("")

st.write("written by Kensuke Kobayashi, Okayama Univ. URA")