import os
from tortoise import Tortoise

# Herokuの環境変数からデータベース接続情報を取得
db_url = os.getenv("JAWSDB_URL")

Tortoise.init(
    db_url=db_url,  # データベース接続情報を環境変数から取得
    models={"models": ["main"]},  # モデルの場所
    default_connection="default",  # デフォルトのデータベース接続名
)
