import requests
import time
from pythonosc import udp_client

# Create 5 separate clients, one per port
client_temp = udp_client.SimpleUDPClient("127.0.0.1", 7400)
client_wind = udp_client.SimpleUDPClient("127.0.0.1", 7401)
client_rain = udp_client.SimpleUDPClient("127.0.0.1", 7402)
client_pressure = udp_client.SimpleUDPClient("127.0.0.1", 7403)
client_humidity = udp_client.SimpleUDPClient("127.0.0.1", 7404)

while True:
    r = requests.get("https://api.openweathermap.org/data/2.5/weather?q=New%20York&appid=da180be4ea47a776e95e1df91d530e2d&units=imperial")
    d = r.json()
    
    # Normalize values - ADJUSTED FOR NYC WINTER
    temp_norm = (d['main']['temp'] - 23) / 36  # 23°F to 59°F → 0 to 1
    wind_norm = min(d['wind']['speed'] / 15, 1.0)  # 0 to 15 m/s (caps higher wind at 1.0)
    rain_norm = min(d.get('rain', {}).get('1h', 0) / 3, 1.0)  # 0 to 3mm → 0 to 1
    pressure_norm = (d['main']['pressure'] - 980) / 60  # UNCHANGED - good range
    humidity_norm = max(0, (d['main']['humidity'] - 40) / 60)  # 40% to 100% → 0 to 1
    
    # Send SAME addresses to DIFFERENT PORTS
    client_temp.send_message("/weather/temp", temp_norm)
    client_wind.send_message("/weather/wind", wind_norm)
    client_rain.send_message("/weather/rain", rain_norm)
    client_pressure.send_message("/weather/pressure", pressure_norm)
    client_humidity.send_message("/weather/humidity", humidity_norm)
    
    print(f"Sent: temp={temp_norm:.2f}, wind={wind_norm:.2f}, rain={rain_norm:.2f}, pressure={pressure_norm:.2f}, humidity={humidity_norm:.2f}")
    time.sleep(600)