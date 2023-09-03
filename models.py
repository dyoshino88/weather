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
