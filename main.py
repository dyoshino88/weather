from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

# OpenWeather APIのエンドポイントとAPIキー
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 都市の天気情報を取得するエンドポイント
@app.get("/get_weather/{city_name}")
async def get_weather(city_name: str):
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
        return {"city": city_name, "weather": weather, "temperature": temperature}
    else:
        raise HTTPException(status_code=response.status_code, detail="City not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
