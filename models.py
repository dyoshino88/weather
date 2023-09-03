from tortoise import fields
from pydantic import BaseModel

# モデルを定義
class CityWeather(BaseModel):
    id: fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255)
    current_weather = fields.JSONField()
    weekly_weather = fields.JSONField()

# ルートモデルを作成
class City(BaseModel):
    id: fields.IntField
    city_name: str