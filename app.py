import os
import requests
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import plantizador_engine

app = FastAPI()

origins = ["*"]
URL_GET_PLANTIZADOR = 'https://xup14y6trg.execute-api.us-east-2.amazonaws.com/dev/getPlantizacion'
URL_POST_PLANTIZADOR = 'https://xup14y6trg.execute-api.us-east-2.amazonaws.com/dev/postPlantizacion'


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos


class Data(BaseModel):
    finca_id: int
    labor_id: int
    persona_id: int
    fecha: date

    @validator("fecha", pre=True)
    def parse_birthdate(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()


def get_plantizacion(finca_id, labor_id, fecha, persona_id):
    heads = {'Authorization': 'gS8Jdz24bJgevS9loGuiCW9R2IJXLcpdme8nQ8b88No'}
    parametros = {'finca_id': finca_id, 'labor_id': labor_id,
                  'fecha': fecha.strftime("%Y-%m-%d"), 'persona_id': persona_id}
    x = requests.get(URL_GET_PLANTIZADOR, params=parametros, headers=heads)
    return x.json()


def postPlantizacion(data):
    r = requests.post(URL_POST_PLANTIZADOR, json=data)
    return True


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the API!"}


@app.post("/plantizar", tags=["Root"], status_code=status.HTTP_200_OK)
async def read_data(data: Data):
    dict_data = data.dict()
    json_data = get_plantizacion(dict_data['finca_id'], dict_data['labor_id'],
                                 dict_data['fecha'], dict_data['persona_id'])
    print(json_data)
    if len(json_data) == 0:
        return {'Error': 'No hay datos para procesar'}
    else:
        json_plantizado = plantizador_engine.plantizar(json_data)
        return {"plantizar": "ok"}
