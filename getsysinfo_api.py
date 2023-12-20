from fastapi import FastAPI
from typing import List
from getdevinfo import *
import pythoncom
import uvicorn


app = FastAPI()

pythoncom.CoInitialize()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get-device-information")
async def get_device_information():
    return get_device_infomation()

if __name__ =="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)