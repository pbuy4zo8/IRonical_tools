# IRonical_public
IRonicalの公開版です．streamlitライブラリを使用し，年齢推定モデルと2D・3Dプロッターを包みこんでいます．  
お手元のPCにダウンロードして頂き，requirementsにあるライブラリをインストールしてお使いください．  
<div align="center">
  <img src="./IRonical_img.png" width="50%">
</div>

### 実行
streamlitとその他のライブラリをインストールした環境で，以下のコマンド実行によりサービスが立ち上がります．  
実行マシンで他サービスが動作していない場合，8501ポートにアクセスすることでサービス画面に到達します．
```
streamlit run main.py
```

### requirements
tensorflow 2.18.0  
pandas 2.2.3  
numpy 2.0.2  
pillow 10.4.0  
(足りなかった場合には都度インストールをお願い致します．)
