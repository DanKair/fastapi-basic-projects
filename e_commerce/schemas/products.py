

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int

    class Config:
        from_attributes = True 