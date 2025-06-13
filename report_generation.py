import db
from datetime import datetime,timedelta
from dateutil.parser import parse
import pytz
import json
import asyncio

def timezone_converstion(timezone, timestamp):
    time_str = timestamp.replace(" UTC", "")
    naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    naive_utc = pytz.utc.localize(naive)
    timez = pytz.timezone(timezone)
    time_final = naive_utc.astimezone(timez)
    date_time = datetime.fromisoformat(str(time_final))
    return date_time

async def report_generation(report_id):
    report = {}
    conn = db.get_connection()
    curr = conn.cursor()

    curr.execute("""
    INSERT INTO reports (report_id, available)
    VALUES (%s, %s)
    ON CONFLICT (report_id) DO NOTHING
    """, (str(report_id), False))

    conn.commit()

    await asyncio.sleep(1)
    curr.execute("""SELECT DISTINCT store_id FROM store_status""" )
    store_ids = curr.fetchall()
    conn.commit()

    for id in store_ids:
        curr.execute("SELECT * FROM timezones where store_id = %s",(str(id[0]),))
        timezones = curr.fetchall()
        if timezones:
            timezone = timezones[0][1]['timezone_str']
        else: 
            timezone = "America/Chicago"

        end_time = ""
        start_time = ""
        menu_present = True
        curr.execute("SELECT * FROM menu_hours WHERE store_id = %s", (str(id[0]),))
        menu_hours = curr.fetchall()

        if not menu_hours: 
            start_time = "00:00:00"
            end_time = "23:59:59"
            menu_present = False
        # print(start_time , end_time , c_m)
        
        curr.execute("SELECT * FROM store_status WHERE store_id = %s", (str(id[0]),))
        store_status = curr.fetchall()

        timestamp = list(store_status[0][1].keys())

        if(len(timestamp) == 1 ): 
            uptime_last_hour = 60
            uptime_last_day = 1
            uptime_last_week = 1
            downtime_last_day = 0
            downtime_last_week = 0
            downtime_last_hour = 0
        else : 
            timestamp.sort()  

            date_time_1 = timezone_converstion(timezone,timestamp[-1])
            date_time_2 = timezone_converstion(timezone,timestamp[-2])
            day = date_time_1.date().strftime("%w")
            if(menu_present and day in menu_hours[0][1]) : 
                start_time = menu_hours[0][1][day]['start_time_local']
                end_time = menu_hours[0][1][day]['end_time_local']
            else : 
                start_time = "00:00:00"
                end_time = "23:59:59"


            #hour compute

            stat_1= store_status[0][1][timestamp[-1]]['status']
            stat_2= store_status[0][1][timestamp[-2]]['status']

            uptime_last_hour = ""
            downtime_last_hour = ""

            if(stat_2=='actve') : 
                uptime_last_hour = min(60, (date_time_1-date_time_2).total_seconds()/60)
                downtime_last_hour = 0
            else :
                uptime_last_hour = 0
                downtime_last_hour = min(60, (date_time_1-date_time_2).total_seconds()/60)

            #print(c_len ,uptime_last_hour, downtime_last_hour ,c_run)


            #day compute
        
            uptime_last_day = 0
            downtime_last_day = 0
            c = 0

            for i in timestamp[::-1]:
                x = timezone_converstion(timezone,i)
                day_x = x.date().strftime("%w")
                x_time = x.time()
                if(str(x_time) > end_time) : continue
                if(day_x != day or str(x_time) < start_time ): break
                stat = store_status[0][1][i]['status']
                if(stat == 'active'): uptime_last_day+=1
                else: downtime_last_day+=1
                c+=1

            #print(c_len, uptime_last_day , downtime_last_day, c)

            ##week compute
            uptime_last_week = 0
            downtime_last_week = 0
            c_week = 0   

            days = set()
            date = set()

            for i in timestamp[::-1]:
                x = timezone_converstion(timezone,i)
                day_x = x.date().strftime("%w")
                date_x = str(x.date())
                if( day_x in days and date_x not in date ): break
                date.add(date_x)
                days.add(day_x)
                x_time = x.time()
                if(str(x_time) < start_time or str(x_time) > end_time) : continue
                stat = store_status[0][1][i]['status']
                if(stat == 'active'): uptime_last_week+=1
                else: downtime_last_week+=1
                c_week+=1

        report[f"{str(id[0])}"] = {
            "uptime_last_hour(in minutes)" : f"{uptime_last_hour}",
            "uptime_last_day(in hours)" : f"{uptime_last_day}",
            "uptime_last_week(in hours)" : f"{uptime_last_week}",
            "downtime_last_hour(in minutes)" : f'{downtime_last_hour}',
            "downtime_last_day(in hours)":  f"{downtime_last_day}",
            "downtime_last_week(in hours)" :  f'{downtime_last_week}'
        }

    # print(report)
    curr.execute("""
    INSERT INTO report_data (report_id, schedule)
    VALUES (%s, %s)
    ON CONFLICT (report_id)     
    DO UPDATE SET schedule = EXCLUDED.schedule
    """, (str(report_id), json.dumps(report)))
    conn.commit()

    curr.execute("""
    INSERT INTO reports (report_id, available)
    VALUES (%s, %s)
    ON CONFLICT (report_id)
    DO UPDATE SET available = EXCLUDED.available
    """, (str(report_id), True))

    conn.commit()
    
