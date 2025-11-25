from pydantic import BaseModel

# Model untuk Auth
class UserAuth(BaseModel):
    email: str
    password: str

# Model untuk ML
class AnalysisRequest(BaseModel):
    file_url: str