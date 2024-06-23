import pyxel
import PyxelUniversalFont as puf
import pandas as pd
import numpy as np

base_df = pd.read_csv("./result.csv")
base_df["highlight"] = 0
base_df["distance"] = 100
base_df["circle_distance"] = 100

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
        if pyxel.btnp(pyxel.KEY_W):
            self.dist_level += 0.5
        elif pyxel.btnp(pyxel.KEY_S):
            self.dist_level -= 0.5
            if self.dist_level == 0:
                self.dist_level = 0.5

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.save_data()

        

    def draw(self):
        # マウスが動いていない場合には描画処理をしない(描画がかわることはないので)
        if pyxel.mouse_x == self.mouse_x and pyxel.mouse_y == self.mouse_y and self.last_dist == self.dist_level:
            pass
        
        else:
            self.calc_distance()

            self.draw_baseUI()            
            
            # self.hover_list = []
            # self.draw_picked(self.hover_list)

            self.draw_tsne_plot()

            pyxel.rectb(self.offset*2+self.scale, self.offset-20, 400, 400, 13)

            # mouse pointer
            pyxel.blt(pyxel.mouse_x-8, pyxel.mouse_y-8, 0, 0, 0, 16, 16, 0)

            # save mouse position and dist_level
            self.mouse_x = pyxel.mouse_x
            self.mouse_y = pyxel.mouse_y
            self.last_dist = self.dist_level

    def draw_baseUI(self):
        pyxel.cls(7)
        self.writer.draw(6, 6, "いろにかる 分析ツール", 30, 13)
        self.writer.draw(5, 5, "いろにかる 分析ツール", 30, 0)

    def draw_tsne_plot(self):
        # self.writer.draw(421, 36, "t-SNE plot", 30, 13)
        self.writer.draw(self.offset+self.scale-150, self.offset-20, "t-SNE plot", 30, 13)
        self.writer.draw(self.offset-10, self.offset+30, "picked researcher: ", 20, 13)
        self.writer.draw(self.offset-10, self.offset-20, "circle size: ", 20, 13)
        self.writer.draw(self.offset, self.offset, str(int(self.dist_level*10)/10), 25, 13)

        pyxel.rectb(self.offset-20, self.offset-20, self.scale+40, self.scale+40, 13)
        self.writer.draw(self.offset-20, self.offset+20+self.scale, str(int(self.one_min)), 20, 13)
        self.writer.draw(self.offset+self.scale, self.offset+20+self.scale, str(int(self.one_max)), 20, 13)
        self.writer.draw(self.offset-55, self.offset+self.scale, str(int(self.two_min)), 20, 13)
        self.writer.draw(self.offset-50, self.offset-20, str(int(self.two_max)), 20, 13)


        for i in range(len(self.tsne0_draw)):
            if base_df.at[i, "circle_distance"] < self.dist_level:
                pyxel.circ(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.tsne1_draw[i]*self.scale + self.offset, 
                    2,
                    6
                )
            else:
                # pyxel.rect(
                #     self.tsne0_draw[i]*self.scale + self.offset, 
                #     self.tsne1_draw[i]*self.scale + self.offset, 
                #     3, 
                #     3, 
                #     13
                # )
                pyxel.circ(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.tsne1_draw[i]*self.scale + self.offset, 
                    2,
                    13
                )

            # highlightが1のときにマウスまでの直線を引く
            if base_df.at[i, "highlight"] == 1:
                pyxel.line(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.tsne1_draw[i]*self.scale + self.offset, 
                    pyxel.mouse_x,
                    pyxel.mouse_y,
                    8
                )
                pyxel.circb(
                    self.tsne0_draw[i]*self.scale + self.offset, 
                    self.tsne1_draw[i]*self.scale + self.offset, 
                    self.dist_level*25, # 円の大きさはdist_levelに合わせたいが，微妙にずれがある
                    6
                )
                # self.writer.draw(self.offset+1, self.offset+1, base_df.at[i, "職員名称"], 25, 13)
                self.writer.draw(self.offset, self.offset+55, base_df.at[i, "職員名称"], 25, 13)
        
    def calc_distance(self):
        # マウスポインタとプロット全ての距離を計算
        base_df["distance"] = np.sqrt((self.tsne0_draw*800 + 100 - pyxel.mouse_x) ** 2 + (self.tsne1_draw*800+100 - pyxel.mouse_y) ** 2)
        # print(base_df["distance"].min())    # 最小値をprint
        # print(base_df["distance"].idxmin())
        base_df["highlight"] = 0
        base_df.at[base_df["distance"].idxmin(), "highlight"] = 1

        # こちらは選択中の研究者に対する距離の計算
        base_x = base_df.at[base_df["distance"].idxmin(), "tsne0"]
        base_y = base_df.at[base_df["distance"].idxmin(), "tsne1"]
        base_df["circle_distance"] = np.sqrt((base_x - base_df["tsne0"]) ** 2 + (base_y - base_df["tsne1"]) ** 2)
            

    def save_data(self):
        try:
            result_df = base_df.query("circle_distance <= @self.dist_level")
            print(result_df)
            file_name = base_df.at[base_df["distance"].idxmin(), "職員名称"]
            result_df.to_csv("./" + str(file_name.replace("　", "")) + ".csv", encoding="utf_8_sig", index=False)
        except:
            pass

App()