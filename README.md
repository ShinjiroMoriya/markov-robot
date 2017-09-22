# マルコフ連鎖による返答ロボット
コマンドラインで動作するアプリ

環境
- python 3.6

### ライブラリ
- mecab
- natto-py

```
brew install mecab
```
```
pip install natto-py
```

### 説明
「pattern.csv」の定型文で返答します。
定型文がなければ、マルコフ連鎖を利用して「import.txt」内の文章を元に返答します。

・動かす
```
python main.py
```
