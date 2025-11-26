from pydantic import BaseModel
# Model untuk ML
class AnalysisRequest(BaseModel):
    file_url: str