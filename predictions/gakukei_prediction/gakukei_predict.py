#
#   written by K.Kobayashi(jeffy890)
#   2023.7.25
#
#   neural network script
#   judge researchers' field from field and keyword columns
#   
#
#   revised on 2023.10.10
#   output 14 fields values
#
#   revised on 2023.10.12
#   output 20 fields values
#
#   revised on 2024.02.21
#   modified for exe
#

import MeCab
import numpy as np
import pandas as pd
import pickle
import sys
import os

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

# mecabの設定
mcb = MeCab.Tagger("-Owakati")

# 審査区分
field_title = "審査区分/研究分野"
key_title = "キーワード"

### 読み込みパート

# field dictの読み込み
with open("./dict/field_dict.pkl", "rb") as f:
    field_dict = pickle.load(f)

with open("./dict/key_dict.pkl", "rb") as f:
    key_dict = pickle.load(f)

# 学系の読み込み
with open("./dict/gakukei.pkl", "rb") as f:
    gakukei = pickle.load(f)

with open("./dict/id_to_gakukei.pkl", "rb") as f:
    id_to_gakukei = pickle.load(f)

# model load and predict
with open("./models/clf_model_field.pkl", "rb") as f:
    clf_field = pickle.load(f)

with open("./models/clf_model_key.pkl", "rb") as f:
    clf_key = pickle.load(f)

### 読み込みパート終わり


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

for file in range(len(filename_to_load)):
    base_df = pd.read_csv(filename_to_load[file])
    judge_df = base_df

    # modelによる判定部分
    # 審査区分・研究分野による分類
    data_array_judge = np.zeros([len(judge_df.index), 1])
    data_array_judge_full = np.zeros([len(judge_df.index), 20])
    field_count = 0
    for index, row in judge_df.iterrows():
        data_array_field_temp = np.zeros([1, len(field_dict)])
        try:
            field_temp = row.loc[field_title].split("/")
            for i in range(len(field_temp)):
                insert_field = field_temp[i].replace(" ", "")
                insert_field = mcb.parse(insert_field).split()
                for j in range(len(insert_field)):
                    if insert_field[j] in field_dict:
                        data_array_field_temp[0, field_dict[insert_field[j]]] += 1
                else:
                    pass

            predict = clf_field.predict(data_array_field_temp)
            pred_proba = clf_field.predict_proba(data_array_field_temp)
            
            data_array_judge[field_count, 0] = predict
            data_array_judge_full[field_count] = pred_proba

        except:
            data_array_judge[field_count, 0] = -1
            data_array_judge_full[field_count] = -1
        
        field_count += 1

    # キーワードによる分類
    data_array_judge_key = np.zeros([len(judge_df.index), 1])
    data_array_judge_key_full = np.zeros([len(judge_df.index), 20])
    field_count = 0
    for index, row in judge_df.iterrows():
        data_array_field_temp = np.zeros([1, len(key_dict)])
        try:
            field_temp = row.loc[key_title].split("/")
            for i in range(len(field_temp)):
                insert_field = field_temp[i].replace(" ", "")
                insert_field = mcb.parse(insert_field).split()
                for j in range(len(insert_field)):
                    if insert_field[j] in key_dict:
                        data_array_field_temp[0, key_dict[insert_field[j]]] += 1
                else:
                    pass

            predict = clf_key.predict(data_array_field_temp)
            pred_proba = clf_key.predict_proba(data_array_field_temp)

            data_array_judge_key[field_count, 0] = predict
            data_array_judge_key_full[field_count] = pred_proba

        except:
            data_array_judge_key[field_count, 0] = -1
            data_array_judge_key_full[field_count] = -1
        field_count += 1

    # 判定終了

    # idから学系への変換
    data_array_judge_gakukei = []
    for i in range(len(data_array_judge)):
        try:
            data_array_judge_gakukei.append(id_to_gakukei[data_array_judge[i, 0]])
        except:
            data_array_judge_gakukei.append("error")


    data_array_judge_gakukei_key = []
    for i in range(len(data_array_judge_key)):
        try:
            data_array_judge_gakukei_key.append(id_to_gakukei[data_array_judge_key[i, 0]])
        except:
            data_array_judge_gakukei_key.append("error")


    # 列の追加
    # fieldとkeyの追加
    result_df = judge_df
    result_df["from field"] = data_array_judge_gakukei
    result_df["from key"] = data_array_judge_gakukei_key

    # probability
    # もっともらしいかの判定
    probability = []
    for i in range(len(data_array_judge_gakukei)):
        if data_array_judge_gakukei[i] == "error":
            if data_array_judge_gakukei_key[i] == "error":
                probability.append(0)
            else:
                probability.append(50)
        elif data_array_judge_gakukei_key[i] == "error":
            if data_array_judge_gakukei[i] == "error":
                probability.append(0)
            else:
                probability.append(50)
        elif data_array_judge_gakukei[i] == data_array_judge_gakukei_key[i]:
            probability.append(100)
        elif data_array_judge_gakukei[i] != data_array_judge_gakukei_key[i]:
            probability.append(50)

    result_df["probability"] = probability

    # 結果の保存
    result_df.to_csv(filename_to_load[file].replace(".csv", "")+"_predicted.csv", encoding="utf-8_sig", index=False)
    print(str(filename_to_load[file]) + " done\n")

print("seems like everything is now done")
print("check ./data directory")