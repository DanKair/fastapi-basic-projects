from decimal import Decimal
from typing import Annotated, List
from pydantic import BaseModel, ConfigDict, Field

PriceDecimal = Annotated[Decimal, Field(ge=0, decimal_places=2)]


class ProductBase(BaseModel):
    name: str
    price: PriceDecimal
    stock_quantity: int = Field(ge=0)


class ProductCreate(ProductBase):
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    price: PriceDecimal | None = None
    stock_quantity: int | None = Field(default=None, ge=0)


class ProductResponse(ProductBase):
    category_id: int
    id: int

    # Modern Pydantic V2 way to enable ORM mode (from_attributes)
    model_config = ConfigDict(from_attributes=True)


class PaginatedProductEnvelope(BaseModel):
    products: List[ProductResponse] 
    total_products: int
    page: int
    size: int # Limit value
    total_pages: int   