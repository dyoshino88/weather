from fastapi import FastAPI, HTTPException
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import CityWeather, City
from typing import List
import requests # OpenWeather APIへのリクエストをするために追加
import os # 環境変数を読み取るために追加
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()

# 環境変数からOpenWeather APIキーを取得
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if OPENWEATHER_API_KEY is None:
    raise Exception("OpenWeather APIキーが設定されていません。")

origins = [
    "http://localhost:3000",
    "https://weather-app-front-eosin.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JAWSDB_URL環境変数から接続情報を取得
db_url = os.getenv("JAWSDB_URL")

if db_url is None:
    raise Exception("JAWSDB_URLが設定されていません。")

# URLをパースして必要な情報を取得
result = urlparse(db_url)
db_username = result.username
db_password = result.password
db_host = result.hostname
db_port = result.port
db_name = result.path.lstrip("/") # スラッシュを除外

# PydanticモデルをTortoise ORMモデルから自動生成
City_Pydantic = pydantic_model_creator(City)
CityWeather_Pydantic = pydantic_model_creator(CityWeather)

# Tortoise-ORMを初期化
Tortoise.init_models(["models"], "models")

# OpenWeather APIから天気情報を取得してデータベースに保存
def get_weather_data(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 都市を作成するエンドポイント
@app.post("/cities/", response_model=CityWeather_Pydantic)
async def create_city(city: City_Pydantic):
    # OpenWeather APIから天気情報を取得
    weather_data = get_weather_data(city.city_name)
    
    if weather_data is None:
        raise HTTPException(status_code=404, detail="City not found")

    # データベースに都市を作成
    city_obj = await CityWeather.create(
        city_name=city.city_name,
        current_weather=weather_data,
        weekly_weather={},
    )
    return city_obj

# 都市の天気情報を取得するエンドポイント
@app.get("/cities/{city_name}", response_model=CityWeather_Pydantic)
async def get_city_weather(city_name: str):
    # データベースから都市の天気情報を取得
    city_obj = await CityWeather.get_or_none(city_name=city_name)
    if city_obj is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city_obj

# FastAPIアプリケーションを起動
if __name__ == "__main__":
    from tortoise.contrib.fastapi import register_turtoise
    
    register_turtoise(
        app,
        db_url=f"mysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}",
        modules={"models": ["__main__"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    
