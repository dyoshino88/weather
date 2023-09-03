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
    
from tortoise import fields, models

# Tortoise ORM モデルを定義
class CityWeather(models.Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255)
    current_weather = fields.JSONField()
    weekly_weather = fields.JSONField()

# Tortoise ORM モデルを作成
class City(models.Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255)