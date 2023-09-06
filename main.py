from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import fields, Tortoise, run_async
from datetime import date
from models import City, CityWeather  # models.py からモデルをインポート

app = FastAPI()

# バックエンドのCORS設定
origins = [
    "http://localhost:3000",  # フロントエンドのアドレス
    "https://weather-app-front-eosin.vercel.app",  # プロダクション環境のフロントエンドアドレス
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 必要なHTTPメソッドを指定します
    allow_headers=["*"],  # 必要なHTTPヘッダーを指定します
)

# Herokuの環境変数からデータベース接続情報を取得
db_url = os.getenv("JAWSDB_URL")

# OpenWeather APIのエンドポイントとAPIキー
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# データベース接続の初期化を非同期関数で行う
async def initialize_db():
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["models"]},  # モデルが存在するモジュールを指定
        default_connection="default",  # デフォルトのデータベース接続を指定
    )
    await Tortoise.generate_schemas()  # スキーマの生成

City_Pydantic = pydantic_model_creator(City)
CityWeather_Pydantic = pydantic_model_creator(CityWeather)

# 都市の天気情報を取得してデータベースに格納し、同じ日の同一地域の天気情報をDBから取得するエンドポイント
@app.get("/get_weather/{city_name}", response_model=CityWeather_Pydantic)
async def get_and_store_weather(city_name: str):
    # すでに同じ日の同一地域の情報がDBにあるか確認
    today = date.today()
    existing_weather = await CityWeather.filter(city_name=city_name, created_at__date=today).first()
    
    if existing_weather:
        return existing_weather
    
    # DBに情報がない場合、OpenWeather APIから取得
    params = {
        "q": city_name,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # 温度の単位を摂氏に設定
    }

    response = requests.get(OPENWEATHER_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        weather = data.get("weather")[0].get("description")
        temperature = data.get("main").get("temp")

        # データベースに都市の天気情報を格納
        city_weather = await CityWeather.create(
            city_name=city_name,
            weather=weather,
            temperature=temperature,
        )

        return city_weather
    else:
        raise HTTPException(status_code=response.status_code, detail="City not found")

if __name__ == "__main__":
    run_async(initialize_db())
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))  # Herokuのポートを取得
