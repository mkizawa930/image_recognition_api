# YOLOを使用した物体検出API

**セットアップ**

``` bash
# uvがない場合はinstall
pip install uv

# プロジェクト初期化
uv sync
```


**APIサーバを起動する**

```bash
# ローカルでAPIサーバを起動
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8080

# コマンドラインからAPIを叩くサンプル
curl -X POST -F "file=@./data/sample_img.png" http://localhost:8080/api/recognition
```

**APIドキュメント**

http://localhost:8080/docs


**HTMLから画像をアップロードする**

http://localhost:8080/upload を開き、認識したい画像をファイラーから選択して送信する