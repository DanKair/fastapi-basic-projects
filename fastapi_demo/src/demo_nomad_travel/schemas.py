from pydantic import BaseModel, Field, model_validator, ValidationError
from slugify import slugify

class RegionBase(BaseModel):
    name: str = Field(max_length=50)
    slug: str | None = None

    @model_validator(mode="before")
    @classmethod
    def generate_slug_from_title(cls, data: dict) -> dict:
        """Generates a slug from the name field before Pydantic validation."""
        if isinstance(data, dict) and "name" in data and not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

class RegionCreate(RegionBase):
    """
    We used method overriding on the name field
    """
    name: str = Field(max_length=10)

"""
region1 = RegionBase(name="Almaty-City")
print(repr(region1))

region2 = RegionCreate(name="Almaty-City")
print(repr(region2))"""

"""try:
    region2 = RegionCreate(name="Kyzylorda Oblasy")
except ValidationError as e:
    print("Validation error: ", e)
finally:
    print(repr(region1))"""
