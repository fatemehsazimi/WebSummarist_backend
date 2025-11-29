from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str
