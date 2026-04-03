from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.database import get_all_workers, get_conn
from app.services.trigger_engine import fetch_live_weather, detect_disruptions
from datetime import datetime

scheduler = BackgroundScheduler()

def poll_all_cities():
    workers = get_all_workers()
    active_cities = set(w["city"] for w in workers)
    
    for city in active_cities:
        weather = fetch_live_weather(city)
        if not weather:
            continue
        
        conn = get_conn()
        for trigger, value in [
            ("temperature", weather["temperature"]),
            ("rainfall", weather["rainfall"]),
            ("aqi", weather["aqi"])
        ]:
            conn.execute(
                "INSERT INTO weather_log (city, trigger_type, value, recorded_at) VALUES (?, ?, ?, ?)",
                (city, trigger, value, datetime.utcnow().isoformat())
            )
        conn.commit()
        conn.close()
        
        disruptions = detect_disruptions(
            city, 
            weather["temperature"], 
            weather["rainfall"], 
            weather["aqi"]
        )
        if disruptions:
            from app.routes.triggers import _process_disruptions
            _process_disruptions(city, disruptions, weather)

def start_weather_poller():
    scheduler.add_job(poll_all_cities, 'interval', minutes=30)
    scheduler.start()
    print("Weather poller started")

def stop_weather_poller():
    scheduler.shutdown()