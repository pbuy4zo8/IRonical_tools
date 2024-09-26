'''
    written by K.Kobayashi(jeffy890)
    2024.07.01



'''

import pyxel
import PyxelUniversalFont as puf
import pandas as pd
import numpy as np

base_df = pd.read_csv("./result.csv")
base_df["highlight"] = 0
base_df["distance"] = 100
base_df["circle_distance"] = 100
base_df["picked_distance"] = 0

picked_df = base_df.copy()
print(picked_df)

class App:
    def __init__(self):
        pyxel.init(
            width=1500, 
            height=950,
            title="ironical",
            fps=60,
            display_scale=1
        )

        # 色の設定
        pyxel.colors[2] = 0xEEEEEE
        pyxel.colors[6] = 0x66DCE9
        pyxel.colors[7] = 0xFFFFFF
        pyxel.colors[8] = 0xfa12ac

        # イメージの読み込み(マウスカーソル用)
        pyxel.load("./pic.pyxres")

        # 日本語フォントの準備
        self.writer = puf.Writer("IPA_PMincho.ttf")

        self.mouse_x = pyxel.mouse_x
        self.mouse_y = pyxel.mouse_y
        self.last_dist = 1
        self.dist_level = 1
        self.last_picked = 0
        self.picked_num = 0

        self.scale = 800
        self.offset = 100

        self.one_max = base_df["tsne0"].max()
        self.one_min = base_df["tsne0"].min()
        self.two_max = base_df["tsne1"].max()
        self.two_min = base_df["tsne1"].min()
        self.thr_max = base_df["tsne2"].max()
        self.thr_min = base_df["tsne2"].min()

        self.pca_one_max = base_df["pca0"].max()
        self.pca_one_min = base_df["pca0"].min()
        self.pca_two_max = base_df["pca1"].max()
        self.pca_two_min = base_df["pca1"].min()

        # 描画用の値を計算しておく．0~1への正規化．
        self.tsne0_draw = ( base_df["tsne0"] - self.one_min ) / (self.one_max - self.one_min)
        self.tsne1_draw = ( base_df["tsne1"] - self.two_min ) / (self.two_max - self.two_min)
        self.tsne2_draw = ( base_df["tsne2"] - self.thr_min ) / (self.thr_max - self.thr_min)

        self.pca0_draw = ( base_df["pca0"] - self.pca_one_min ) / (self.pca_one_max - self.pca_one_min)
        self.pca1_draw = ( base_df["pca1"] - self.pca_two_min ) / (self.pca_two_max - self.pca_two_min)


        pyxel.run(self.update, self.draw)

    def update(self):
        # dist_levelの調節
        if pyxel.btnp(pyxel.KEY_D):
            self.dist_level += 0.5
        elif pyxel.btnp(pyxel.KEY_A):
            self.dist_level -= 0.5
            if self.dist_level == 0:
                self.dist_level = 0.5

        if pyxel.btnp(pyxel.KEY_S):
            self.picked_num += 1
            if self.picked_num > 4:
                self.picked_num = 4
        elif pyxel.btnp(pyxel.KEY_W):
            self.picked_num -= 1
            if self.picked_num < 0:
                self.picked_num = 0

        if pyxel.btnp(pyxel.KEY_E):
            self.show_picked()

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.save_data()

        
    def draw(self):
        # マウスが動いていない場合には描画処理をしない(描画がかわることはないので)
        if pyxel.mouse_x == self.mouse_x and pyxel.mouse_y == self.mouse_y \
        and self.last_dist == self.dist_level and self.last_picked == self.picked_num:
            pass
        
        else:
            if pyxel.frame_count % 2 == 0:
                self.calc_distance()

            self.draw_baseUI()            

            self.draw_tsne_plot()

            # pca plot
            self.draw_pca()

            # picked list
            self.draw_picked()

            # mouse pointer
            pyxel.blt(pyxel.mouse_x-8, pyxel.mouse_y-8, 0, 0, 0, 16, 16, 0)

            # save mouse position and dist_level
            self.mouse_x = pyxel.mouse_x
            self.mouse_y = pyxel.mouse_y
            self.last_dist = self.dist_level
            self.last_picked = self.picked_num


    def draw_baseUI(self):
        pyxel.cls(7)
        self.baseui_x = self.offset

        pyxel.circ(self.baseui_x, 30, 20, 2)
        pyxel.rect(self.baseui_x+1, 10, 400, 41, 2)
        pyxel.circ(self.baseui_x+401, 30, 20, 2)

        self.writer.draw(self.baseui_x+6, 15, "いろにかる 分析ツール", 30, 13)
        self.writer.draw(self.baseui_x+5, 14, "いろにかる 分析ツール", 30, 0)

        self.writer.draw(1000, 20, "W: 選択研究者↑　S: 選択研究者↓", 30, 13)

    def draw_tsne_plot(self):
        # self.writer.draw(421, 36, "t-SNE plot", 30, 13)
        self.writer.draw(self.offset+self.scale-150, self.offset-20, "t-SNE plot", 30, 13)
        self.writer.draw(self.offset-10, self.offset-20, "circle size: ", 20, 13)
        self.writer.draw(self.offset, self.offset, str(int(self.dist_level*10)/10), 25, 13)
        self.writer.draw(self.offset*2+self.scale, self.offset-50, "picked researcher: ", 20, 13)

        pyxel.rectb(self.offset-20, self.offset-20, self.scale+40, self.scale+40, 13)
        self.writer.draw(self.offset-20, self.offset+20+self.scale, str(int(self.one_min)), 20, 13)
        self.writer.draw(self.offset+self.scale, self.offset+20+self.scale, str(int(self.one_max)), 20, 13)
        self.writer.draw(self.offset-55, self.offset+self.scale, str(int(self.two_min)), 20, 13)
        self.writer.draw(self.offset-50, self.offset-20, str(int(self.two_max)), 20, 13)


        for i in range(len(self.tsne0_draw)):
            if base_df.at[i, "circle_distance"] < self.dist_level:
                pyxel.circ(
                    self.tsne0_draw[i]*self.scale + self.offset,
                    self.offset+self.scale - self.tsne1_draw[i]*self.scale,
                    2,
                    6
                )
            else:
                pyxel.circ(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.offset+self.scale - self.tsne1_draw[i]*self.scale, 
                    2,
                    13
                )

            # highlightが1のときにマウスまでの直線を引く
            if base_df.at[i, "highlight"] == 1:
                pyxel.line(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.offset+self.scale - self.tsne1_draw[i]*self.scale, 
                    pyxel.mouse_x,
                    pyxel.mouse_y,
                    8
                )
                pyxel.circb(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.offset+self.scale - self.tsne1_draw[i]*self.scale,  
                    self.dist_level*25, # 円の大きさはdist_levelに合わせたいが，微妙にずれがある
                    6
                )
                # self.writer.draw(self.offset+1, self.offset+1, base_df.at[i, "職員名称"], 25, 13)
                # self.writer.draw(self.offset, self.offset+self.scale-10, base_df.at[i, "職員名称"], 25, 13)

    def draw_pca(self):
        pca_base_x = self.offset*2 + self.scale
        pca_base_y = self.offset + self.scale/2 + 20
        pca_width = 400

        self.writer.draw(pca_base_x, pca_base_y, "PCA", 35, 13)
        pyxel.rectb(pca_base_x, pca_base_y, pca_width, pca_width, 13)

        for i in range(len(self.tsne0_draw)):
            if base_df.at[i, "circle_distance"] < self.dist_level:
                pyxel.circ(
                    pca_base_x + self.pca0_draw[i]*self.scale/2,
                    pca_base_y + self.scale/2 - self.pca1_draw[i]*self.scale/2,
                    2,
                    8
                )
            else:
                pyxel.circ(
                    pca_base_x + self.pca0_draw[i]*self.scale/2,
                    pca_base_y + self.scale/2 - self.pca1_draw[i]*self.scale/2,
                    1,
                    13
                )
        
    def draw_picked(self):
        self.picked_x = self.offset*2+self.scale
        self.picked_y = self.offset-20

        pyxel.rectb(self.picked_x, self.picked_y, 400, 400, 13)

        self.calc_distance_picked()
        
        picked_df = base_df.query("circle_distance <= @self.dist_level")
        picked_df = picked_df.sort_values("circle_distance", ascending=True)

        if len(picked_df) < 6: 
            self.picked_loop_len = len(picked_df)
            if self.picked_num > len(picked_df):
                self.picked_num = len(picked_df) -1
        else:
            self.picked_loop_len = 5

        for i in range(self.picked_loop_len):
            if self.picked_num == i:
                self.writer.draw(self.picked_x, self.picked_y+i*80, str(picked_df.iat[i, 3]), 34, 8)
            else:
                self.writer.draw(self.picked_x, self.picked_y+i*80, str(picked_df.iat[i, 3]), 34, 13)

        # self.writer.draw(800, 10, str(self.picked_num) + " " + str(len(picked_df)), 30, 8)

    def calc_distance_picked(self):
        # pickedの選択されたものをhighlight
        picked_df = base_df.query("circle_distance <= @self.dist_level")
        picked_df = picked_df.sort_values("circle_distance", ascending=True)
        base_df["highlight"] = 0

        if self.picked_num > len(picked_df) - 1:
            self.picked_num = len(picked_df) - 1
        self.highlighted_index = picked_df.index[self.picked_num]
        base_df.at[self.highlighted_index, "highlight"] = 1

        # こちらは選択中の研究者に対する距離の計算
        base_x = base_df.at[self.highlighted_index, "tsne0"]
        base_y = base_df.at[self.highlighted_index, "tsne1"]
        base_z = base_df.at[self.highlighted_index, "tsne2"]
        base_df["picked_distance"] = np.sqrt(
            (base_x - base_df["tsne0"]) ** 2 + \
            (base_y - base_df["tsne1"]) ** 2 + \
            (base_z - base_df["tsne2"]) ** 2
            )

    def show_picked(self):
        picked_df = base_df.query("picked_distance <= @self.dist_level")
        picked_df = picked_df.sort_values("picked_distance", ascending=True)

        print(picked_df)
                
    def calc_distance(self):
        # マウスポインタとプロット全ての距離を計算
        base_df["distance"] = np.sqrt((self.tsne0_draw*800 + 100 - pyxel.mouse_x) ** 2 + (900 - self.tsne1_draw*800 - pyxel.mouse_y) ** 2)
        # print(base_df["distance"].min())    # 最小値をprint
        # print(base_df["distance"].idxmin())
        base_df["highlight"] = 0
        base_df.at[base_df["distance"].idxmin(), "highlight"] = 1

        # こちらは選択中の研究者に対する距離の計算
        base_x = base_df.at[base_df["distance"].idxmin(), "tsne0"]
        base_y = base_df.at[base_df["distance"].idxmin(), "tsne1"]
        base_z = base_df.at[base_df["distance"].idxmin(), "tsne2"]
        base_df["circle_distance"] = np.sqrt(
            (base_x - base_df["tsne0"]) ** 2 + \
            (base_y - base_df["tsne1"]) ** 2 + \
            (base_z - base_df["tsne2"]) ** 2
            )
            

    def save_data(self):
        try:
            # result_df = base_df.query("circle_distance <= @self.dist_level")
            picked_df = base_df.query("picked_distance <= @self.dist_level")
            picked_df = picked_df.sort_values("picked_distance", ascending=True)

            print(picked_df)

            # file_name = base_df.at[base_df["distance"].idxmin(), "職員名称"]
            file_name = picked_df.iat[0, 3]
            print(file_name)
            picked_df.to_csv("./" + str(file_name.replace("　", "")) + ".csv", encoding="utf_8_sig", index=False)

        except:
            pass

App()
