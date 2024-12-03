import streamlit as st
import plotly.express as px

import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_icon="./IR_small.png")
base_df = pd.read_csv("./data/indication_plotter.csv")

def make_plot(color_col="nan", cols=["axis1", "axis2", "axis3"], marker_size=2):
    if len(cols) == 3:
        try:
            # color_col指定がなかったら通常プロット
            if color_col == "nan":
                fig = px.scatter_3d(
                    base_df,
                    x=cols[0],
                    y=cols[1],
                    z=cols[2],
                )

            else:
                fig = px.scatter_3d(
                    base_df,
                    x=cols[0],
                    y=cols[1],
                    z=cols[2],
                    color=color_col
                )
            fig.update_layout(title="3d plot", width=600, height=600)
            fig.update_traces(marker_size=marker_size)

            st.plotly_chart(fig, use_container_width=True)

        except:
            st.write("It seems like something is wrong. Plaese check data and try again.")
    
    elif len(cols) == 2:
        try:
            if color_col == "nan":
                fig = px.scatter(
                    base_df,
                    x=cols[0],
                    y=cols[1]
                )

            else:
                fig = px.scatter(
                    base_df,
                    x=cols[0],
                    y=cols[1],
                    color=color_col
                )
            fig.update_layout(title="2d plot", width=600, height=600)
            fig.update_traces(marker_size=marker_size)

            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write("It seems like something is wrong. Plaese check data and try again.")

    else:
        st.write("Please select two or three axis.")

st.title("indication")
st.write("csvデータから2D・3Dプロットを作成します．")
up_data = st.file_uploader("plz upload csv file")
if up_data:
    base_df = pd.read_csv(up_data)

axis_mode = st.radio("プロット列の選択", ("OFF", "ON"))
if axis_mode == "ON":
    usecols = st.multiselect(
        "プロットする列を選択してください(最大3列)",
        base_df.columns.to_list(),
        base_df.columns.to_list()[0]
    )

else:
    usecols = ["axis1", "axis2", "axis3"]


color_mode = st.radio("色分けON/OFF", ("OFF", "ON"))
if color_mode == "ON":
    color_col = st.multiselect(
        "色分けに使用する列名を選択してください．",
        base_df.columns.to_list(),
        base_df.columns.to_list()[0]
    )
    try:
        base_df = base_df.astype({color_col[0]: "object"})
        st.write("色分けには" + str(color_col[0]) + "が使用されます．")
    except:
        color_col = ["nan"]
else:
    color_col = ["nan"]

marker_size = st.slider("マーカーサイズ", 2, 20)

st.markdown("## Plotting")
make_plot(color_col[0], usecols, marker_size)