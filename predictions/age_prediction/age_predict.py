'''
    written by K.Kobayashi(jeffy890)
    2023.8.31
   
    age prediction
    過去所属情報をもとに推測を行う

    revised on 2024.02.20
    modified for kaken data
    tensorflowモデルの使用をループごとではなく，
    データ全てを一括で投入できるように改良
'''

import numpy as np
import pandas as pd
import sys

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf

# 職名の分類を行う関数
def exp_bunrui(position):
    bunrui = 0
    bunrui_dict = {"その他":0, "講師":1, "助手":2, "助教":3, "教授":4, "助教授":5, "准教":6, "医員":7}
    id_to_dict = {0:"その他", 1:"講師", 2:"助手", 3:"助教", 4:"教授", 5:"助教授", 6:"准教", 7:"医員"}
    for i in range(len(bunrui_dict)):
        if id_to_dict[i] in position:
            bunrui = i

    return bunrui

# kakenデータファイルが研究者データなのか，研究課題データなのかを判定する関数．
def kaken_file_check(filename):

    return "researcher"

# set variables
# ファイルの確認
files_name = os.listdir("./data/")

# ファイルが無い場合にはスクリプトを終了する
if len(files_name) == 0:
    print("seems like no file in data directory...\n")
    sys.exit()

filename_to_load = []
for i in range(len(files_name)):
    # _predictedがファイル名に含まれている場合にはすでに推測しているので飛ばす
    if "_predicted" not in files_name[i]:
        # Kakenファイルが研究者データの場合にのみ読み込むリストに加える
        if kaken_file_check(files_name[i]) == "researcher":
            filename_to_load.append("./data/"+files_name[i])

# ファイルが無い場合にはスクリプトを終了する
if len(filename_to_load) == 0:
    print("seems like no file in data directory...\n")
    sys.exit()

# 処理に使われるファイル名の確認
print("following files will be used")
for i in range(len(filename_to_load)):
    print(filename_to_load[i])
print()

# model load
lin_model_multiple = tf.keras.models.load_model("./models/saved_model_past")

for i in range(len(filename_to_load)):
    # データの読み込み
    base_df = pd.read_csv(filename_to_load[i])
    base_df["past_year"] = 0
    base_df["past_job_num"] = 0


    pred_age_array = np.zeros([len(base_df.index), 1])

    # 過去所属から一番古い職名と年度を取得する
    for index, row in base_df.iterrows():
        try:
            temp_past = row["所属 (過去の研究課題情報に基づく)"]
            temp_past = temp_past.split("\n")
            temp_past = temp_past[len(temp_past)-1]
            temp_year = str(temp_past)[:4]
            temp_past = temp_past.split(" ")
            temp_position = temp_past[len(temp_past)-1]
            temp_bunrui = exp_bunrui(temp_position)

            temp_year = (int(temp_year) - 1985)/(2023-1985)

            base_df.at[index, "past_year"] = temp_year
            base_df.at[index, "past_job_num"] = temp_bunrui

        except:
            base_df.at[index, "past_job_num"] = -1

    '''
    # 年度情報が取れていない場合には職名番号は0とする
    for index, row in base_df.iterrows():
        if row["past_year"] == 0:
            base_df.at[index, "past_job_num"] = -1
    '''

    # 職名番号が0かどうかで分類
    pred_df = base_df.query("past_job_num != -1")
    pred_df = pred_df.reset_index(drop=True)
    not_pred_df = base_df.query("past_job_num == -1")
    not_pred_df = not_pred_df.reset_index(drop=True)

    # 職名番号が0でないものの年齢を一度に推測
    value_for_pred = pred_df[["past_year", "past_job_num"]].to_numpy()
    pred_age = lin_model_multiple.predict([value_for_pred])

    # 分類した二つのdfをくっつける
    pred_df["pred_age"] = pred_age
    not_pred_df["pred_age"] = 0

    base_df = pd.concat([pred_df, not_pred_df], axis=0)
    base_df = base_df.drop("past_year", axis=1)
    base_df.to_csv(filename_to_load[i].replace(".csv", "")+"_predicted.csv", index=False, encoding="utf_8_sig")

    print(str(filename_to_load[i]) + " done\n")

print("seems like everything is now done")
print("check ./data directory\n")