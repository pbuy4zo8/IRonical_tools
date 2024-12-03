import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_title="ironical", page_icon="./images/favicon_IR.ico")

img = Image.open("./images/IRonical_simple.png")
st.image(img)

st.title("addi(c)tion")
st.write("岡山大学 研究・イノベーション共創機構　URA/IRで作成したサービスを使用できます．")
st.write("各サービスは自由に幅広く利用・活用できます．")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.markdown(
    """
    ironicalは複雑な処理や計算を誰でも簡単に使えるようにラッピングしており，皮肉(irony)を文字通り体現しています．  
    スクリプトの一部は[github](https://github.com/pbuy4zo8/IRonical_tools)での公開を進めています．  
      
    All services written by Kensuke Kobayashi(jeffy890, pbuy4zo8), Okayama Univ. URA
    """
)
