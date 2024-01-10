from pydantic import BaseModel

class getDataRequest(BaseModel):
    variableName: str
    startDt: str
    endDt : str
    lat: float
    lon: float
