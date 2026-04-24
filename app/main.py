from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="DNS Management API")


# ===== Modelos de entrada =====

class ZoneCreate(BaseModel):
    name: str
    visibility: Literal["public", "private"]
    description: str | None = None


class RecordCreate(BaseModel):
    name: str
    record_type: Literal["A", "CNAME"]
    value: str


# ===== "Base de datos" en memoria =====

zones = []
records = []

zone_id_counter = 1
record_id_counter = 1


# ===== Endpoints =====

@app.get("/")
def read_root():
    return {"message": "DNS Management API is running"}


@app.post("/zones", status_code=201)
def create_zone(zone: ZoneCreate):
    global zone_id_counter

    # Validar duplicado por nombre de zona
    for existing_zone in zones:
        if existing_zone["name"] == zone.name:
            raise HTTPException(status_code=409, detail="Zone already exists")

    new_zone = {
        "id": zone_id_counter,
        "name": zone.name,
        "visibility": zone.visibility,
        "description": zone.description,
    }

    zones.append(new_zone)
    zone_id_counter += 1

    return {
        "message": "Zone created successfully",
        "zone": new_zone
    }


@app.get("/zones")
def list_zones():
    return {"zones": zones}


@app.post("/zones/{zone_id}/records", status_code=201)
def create_record(zone_id: int, record: RecordCreate):
    global record_id_counter

    # Verificar que la zona exista
    zone_exists = any(zone["id"] == zone_id for zone in zones)
    if not zone_exists:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Validar nombre duplicado dentro de la misma zona
    for existing_record in records:
        if existing_record["zone_id"] == zone_id and existing_record["name"] == record.name:
            raise HTTPException(
                status_code=409,
                detail="Record name already exists in this zone"
            )

    new_record = {
        "id": record_id_counter,
        "zone_id": zone_id,
        "name": record.name,
        "record_type": record.record_type,
        "value": record.value,
    }

    records.append(new_record)
    record_id_counter += 1

    return {
        "message": "Record created successfully",
        "record": new_record
    }


@app.get("/zones/{zone_id}/records")
def list_records(zone_id: int):
    # Verificar que la zona exista
    zone_exists = any(zone["id"] == zone_id for zone in zones)
    if not zone_exists:
        raise HTTPException(status_code=404, detail="Zone not found")

    zone_records = [record for record in records if record["zone_id"] == zone_id]

    return {"records": zone_records}
