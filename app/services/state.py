from pydantic import BaseModel


class PriceComparisonState(BaseModel):
    query: str
    response: str =""
