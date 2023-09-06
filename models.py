from tortoise.models import Model
from tortoise import fields

class City(Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255, unique=True)

class CityWeather(Model):
    id = fields.IntField(pk=True)
    city_name = fields.CharField(max_length=255, unique=True)
    weather = fields.CharField(max_length=255)
    temperature = fields.DecimalField(max_digits=5, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)
