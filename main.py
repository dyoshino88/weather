from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields
from tortoise import Tortoise, run_async
from datetime import date

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
db_url = os.getenv("DATABASE_URL")

# OpenWeather APIのエンドポイントとAPIキー
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Tortoise ORMモデル
class City(Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255, unique=True)

class CityWeather(Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255, unique=True)
    weather = fields.CharField(max_length=255)
    temperature = fields.DecimalField(max_digits=5, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)
    
Tortoise.init(db_url=db_url)  # Herokuの環境変数からデータベース接続情報を読み込む

Tortoise.init_models(["__main__"], "models")
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
    Tortoise.generate_schemas()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))  # Herokuのポートを取得
