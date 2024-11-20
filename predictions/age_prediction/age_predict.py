'''
    written by K.Kobayashi(jeffy890, pbuy4zo8)
    2024.11.12

    revised from rei mitsuyasu's script

'''

# 処理の流れ
# 被予測データの読み込み
# 　↓
# モデルの読み込み
# 　↓
# 予測
# 　↓
# 予測データの保存

from datetime import datetime
import numpy as np
import pandas as pd
import os
import sys

import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

base_df = pd.read_csv("./kaken.csv")

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

# -1~1の間でMin-Max正規化関数
def MinMaxNorm(value,max_value,min_value):
    ave_value = (max_value + min_value) / 2
    dif_value = max_value - min_value
    MMN_value = (value - ave_value) * 2 / dif_value
    return MMN_value

# base_df = base_df[:10]
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
input_dummy_df = input_df*2-1
input_dummy_df["year"] = MinMaxNorm(input_df["year"], current_year-1, current_year-39)
input_dummy_df["No_of_result"] = MinMaxNorm(base_df["研究課題数"], 118, 1)
input_dummy_df["No_of_output"] = MinMaxNorm(base_df["研究成果数"], 1661, 0)
input_df = input_dummy_df[10::]   # dummy_dataを削除

dnn_model = tf.keras.models.load_model("./model/DNN_AR_MODEL_relu.keras")
# dnn_model = tf.keras.models.load_model("./model/DNN_AFF_MODEL_relu.keras")

pred_data = dnn_model.predict(input_df)

output_df = base_df.copy()
output_df["result"] = pred_data
output_df["year"] = base_df["year"]
output_df.to_csv("./result.csv", encoding="utf_8_sig", index=False)