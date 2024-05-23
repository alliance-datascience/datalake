from pydantic import BaseModel

class getDataRequest(BaseModel):
    variableName: str
    startDt: str
    endDt : str
    lat: float
    lon: float
    
class getDataRequestArea(BaseModel):
    variableName: str
    startDt: str
    endDt : str
    xmax: float
    xmin: float
    ymax: float
    ymin: float
    
class getDataRequestAll(BaseModel):
    variableName: str
    xmax: float
    xmin: float
    ymax: float
    ymin: float
