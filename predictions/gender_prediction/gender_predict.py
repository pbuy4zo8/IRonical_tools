'''
    written by K.Kobayashi(jeffy890)
    2024.06.18

    研究者性別判定スクリプト

    公開データと他のデータを元に，姓名から性別を判定する．

    copied from name_test.py
    revised on 2024.08.22
    簡単に使えるように修正

    revised on 2024.09.11
    科研費データベースからのデータ以外の形式への対応

    revised on 2024.09.24
    軽微な修正
'''

import pandas as pd
import pickle
import sys

# prepare kaken based file
base_df = pd.read_csv("./base.csv")
base_df["性別"] = "na"

# 公開データを用いて判定するパート
open_name_df = pd.read_csv("./data/open_name_list.csv")
open_name_list = open_name_df["名前"].tolist()

for index, row in base_df.iterrows():
    temp_name = row["hit given name"]

    try:
        # namae = temp_name.split(" ")[1]
        namae = temp_name
        temp_data = open_name_df.query("名前 == @namae")
        
        if len(temp_data) == 1:            
            base_df.at[index, "性別"] = temp_data["性別"].values[0]

    except:
        pass

print(sum(base_df["性別"]=="na"))


# 他データを用いて判定するパート
other_df = pd.read_csv("./data/namelist.csv")
other_df = other_df.drop_duplicates()

for index, row in base_df.iterrows():
    if row["性別"] != "na":
        continue

    temp_name = row["hit given name"]

    try:
        # namae = temp_name.split(" ")[1]
        namae = temp_name
        temp_data = other_df.query("名 == @namae")

        if len(temp_data) == 1:
            base_df.at[index, "性別"] = temp_data["性別"].values[0]

    except:
        pass

# print(base_df)
print(sum(base_df["性別"]=="na"))
# base_df.to_csv("./result.csv", encoding="utf_8_sig", index=False)


# bayesの定理に基づく確率計算
# base_df = pd.read_csv("./test_result.csv")
base_df["bayes"] = "na"

with open("./dict/women_percent_dict.pkl", "rb") as f:
    percent_dict = pickle.load(f)

print(len(percent_dict))

for index, row in base_df.iterrows():
    if row["性別"] != "na":
        continue

    try:
        # namae = row["姓名"].split(" ")[1]
        namae = row["hit given name"]

        kakuritsu = 0
        dict_count = 0
        for i in range(len(namae)):
            if namae[i] in percent_dict:
                if kakuritsu == 0:
                    kakuritsu = percent_dict[namae[i]]
                else:
                    kakuritsu = kakuritsu * percent_dict[namae[i]]
            else:
                dict_count += 1
                    
        # print(namae, kakuritsu)

        if dict_count == len(namae):
            base_df.at[index, "bayes"] = "na"
        else:
            base_df.at[index, "bayes"] = kakuritsu

    except:
        pass

base_df.to_csv("./result_bayes.csv", encoding="utf_8_sig", index=False)