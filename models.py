from tortoise import fields
from pydantic import BaseModel

# モデルを定義
class CityWeather(BaseModel):
    id: int
    city_name: str
    current_weather: dict
    weekly_weather: dict

# ルートモデルを作成
class City(BaseModel):
    id: int
    city_name: str