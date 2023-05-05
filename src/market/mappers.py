from sqlalchemy.orm import registry

from . import models
from . import domain


def start_mappers() -> None:
    mapper_registry = registry()

    mapper_registry.map_imperatively(domain.models.CartItem, models.CartItem)
    mapper_registry.map_imperatively(domain.models.Image, models.Image)
    mapper_registry.map_imperatively(domain.models.ProductImage, models.ProductImage)
    mapper_registry.map_imperatively(domain.models.Product, models.Product)
    mapper_registry.map_imperatively(domain.models.User, models.User)
