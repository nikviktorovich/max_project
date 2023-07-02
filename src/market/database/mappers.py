from sqlalchemy.orm import registry

import market.database.models
import market.modules.cart.domain.models
import market.modules.image.domain.models
import market.modules.product.domain.models
import market.modules.product_image.domain.models
import market.modules.user.domain.models


def start_mappers() -> None:
    mapper_registry = registry()

    mapper_registry.map_imperatively(
        market.modules.cart.domain.models.CartItem,
        market.database.models.CartItem,
    )
    mapper_registry.map_imperatively(
        market.modules.image.domain.models.Image,
        market.database.models.Image,
    )
    mapper_registry.map_imperatively(
        market.modules.product.domain.models.Product,
        market.database.models.Product,
    )
    mapper_registry.map_imperatively(
        market.modules.product_image.domain.models.ProductImage,
        market.database.models.ProductImage,
    )
    mapper_registry.map_imperatively(
        market.modules.user.domain.models.User,
        market.database.models.User,
    )
