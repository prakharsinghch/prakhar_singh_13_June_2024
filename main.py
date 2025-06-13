from fastapi import FastAPI
import uuid
import db
import report_generation
import asyncio
import csv

app = FastAPI()

def write_csv(report,file):
    csv_rows = []
    print(type(report) , type(report[0]) )
    for tup in report:
        inner_dict = tup[0] 
        for uuid, stats in inner_dict.items():
            row = {"store_id": uuid}
            row.update(stats)
            csv_rows.append(row)

    with open(file, 'w', newline='') as f:
        fieldnames = csv_rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)


@app.post("/trigger_report")
async def trigger_report():
    id = uuid.uuid4()
    asyncio.create_task(report_generation.report_generation(report_id=id))
    return {"message" : f"report id is {id}"}

@app.get("/get_report/{id}")
def get_report(id):
    conn = db.get_connection()
    curr = conn.cursor()

    curr.execute("SELECT available FROM reports WHERE report_id = %s", (str(id),))
    result = curr.fetchone()
    if result is None: return {"message" : "no report found"}
    if(result[0] == False): return {"message" : "Report Geneartion in progress"}

    curr.execute("SELECT schedule FROM report_data WHERE report_id = %s", (str(id),))
    report_result = curr.fetchall()

    write_csv(report_result,'result.csv')

    return {"message" : f"{report_result}"}