import streamlit as st
import pandas as pd
import tensorflow as tf
from datetime import datetime

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

st.set_page_config(layout="wide", page_icon="IRonical_small.png")

base_df = pd.DataFrame(columns=[[
    "研究者番号",
    "姓名",
    "姓名 (カナ)",
    "姓名 (カナ) (英文)",
    "所属 (現在)",
    "所属 (現在) (英文)",
    "所属 (過去の研究課題情報に基づく)",
    "所属 (過去の研究課題情報に基づく) (英文)",
    "審査区分/研究分野",
	"キーワード",
    "研究課題数",
    "研究成果数"
]])
base_df = pd.read_csv("./data/kaken_sample.csv")

# model load
dnn_model_ar = tf.keras.models.load_model("./data/models/DNN_AR_MODEL_relu.keras")
dnn_model_aff = tf.keras.models.load_model("./data/models/DNN_AFF_MODEL_relu.keras")


get_year = datetime.now().year
get_month = datetime.now().month
def conv_year(get_year, get_month):
    if get_month >= 4:
        current_year = get_year
    else:
        current_year = get_year - 1
    return current_year
current_year = conv_year(get_year, get_month)

def convert_position(position):
    id = 0
    position_to_id_dict = {"その他":0, "講師":1, "助手":2, "助教":3, "教授":4, "助教授":5, "医員":6, "准教授":7, "研究員":8, "特任助教":9}
    if position in position_to_id_dict:
        id = position_to_id_dict[position]
    return id

def extract_job(position_info):
    try:
        temp_past = position_info.split("\r\n")
        the_job = temp_past[-1].split(",")[-1].replace(" ", "")
        return the_job
    except:
        return 0

def extract_year(position_info):
    try:
        temp_past = position_info.split("\r\n")
        the_year = str(temp_past[-1].split(":")[0])[:4]
        return int(the_year)
    except:
        return 0

def MinMaxNorm(value,max_value,min_value):
    ave_value = (max_value + min_value) / 2
    dif_value = max_value - min_value
    MMN_value = (value - ave_value) * 2 / dif_value
    return MMN_value

def prediction(base_df, mode):
    base_df["job"] = base_df["所属 (過去の研究課題情報に基づく)"].apply(extract_job)
    base_df["year"] = base_df["所属 (過去の研究課題情報に基づく)"].apply(extract_year)
    base_df["job_id"] = base_df["job"].apply(convert_position)

    # get_dummiesで抜けを作らないためのダミーデータ
    test_data = [
        [0, 0],
        [0, 1],
        [0, 2],
        [0, 3],
        [0, 4],
        [0, 5],
        [0, 6],
        [0, 7],
        [0, 8],
        [0, 9]
    ]
    input_df = pd.DataFrame(test_data, columns=["year", "job_id"])
    input_df = pd.concat([input_df, base_df[["year", "job_id"]]])
    input_df = pd.get_dummies(input_df, columns=["job_id"], dtype="int")
    input_dummy_df = input_df*2-1   # モデルが要求する入力へ変換
    input_dummy_df["year"] = MinMaxNorm(input_df["year"], current_year-1, current_year-39)

    if mode == "年度+過去所属+課題数+成果数":
        input_dummy_df["No_of_result"] = MinMaxNorm(base_df["研究課題数"], 118, 1)
        input_dummy_df["No_of_output"] = MinMaxNorm(base_df["研究成果数"], 1661, 0)

    input_df = input_dummy_df[10::]   # dummy_dataを削除

    if mode == "年度+過去所属+課題数+成果数":
        pred_data = dnn_model_ar.predict(input_df)
    else:
        pred_data = dnn_model_aff.predict(input_df)

    output_df = base_df.copy()
    output_df["推定年齢"] = pred_data
    output_df["推定年齢"] = output_df["推定年齢"].round(1)

    output_df = output_df.drop(["job", "year", "job_id"], axis=1)

    st.dataframe(output_df, hide_index=True)

def draw_acknowledgements():
    st.write("このサービスを運用するにあたって，機械学習モデルに修正・改良を加えてくださったRei Mitsuyasu氏に感謝いたします．")

def draw_commit():
    st.markdown("### versions")
    st.write("0.0   basic prediction service by K.Kobayashi")
    st.write("1.0   bug fix and modification by Rei Mitsuyasu")
    st.write("1.1   modification for product env by K.Kobayashi")

st.title("age prediction")
st.write("科研費研究者データの過去所属から年齢を推定します．")
mode = st.radio("年齢推定に使用するモデルを選択してください", ("年度+過去所属", "年度+過去所属+課題数+成果数"))

up_data = st.file_uploader("plz upload kaken csv (researcher ver)")
if up_data:
    base_df = pd.read_csv(up_data)

prediction(base_df, mode)

st.write("\n\n")
draw_commit()
draw_acknowledgements()