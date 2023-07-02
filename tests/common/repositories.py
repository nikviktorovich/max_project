import datetime
import uuid
from typing import Dict
from typing import List
from typing import Generic
from typing import Optional
from typing import TypeVar

import market.modules.cart.domain.models
import market.modules.image.domain.models
import market.modules.product.domain.models
import market.modules.product_image.domain.models
import market.modules.user.domain.models
import market.services
from market.common import errors


T = TypeVar('T')


class FakeRepository(Generic[T]):
    items: Dict[uuid.UUID, T]


    def __init__(self, items: Optional[List[T]] = None) -> None:
        if items is None:
            items = []

        self.items = {item.id: item for item in items} # type: ignore
    

    def list(self, **filters) -> List[T]:
        filtered_items = []
        for item in self.items.values():
            for k, v in filters.items():
                if getattr(item, k) == v:
                    filtered_items.append(item)
        return filtered_items
    

    def get(self, item_id: uuid.UUID) -> T:
        if item_id not in self.items:
            raise errors.NotFoundError(
                f'Unable to find an item with id={item_id}',
            )

        return self.items[item_id]
    

    def add(self, item: T) -> T:
        self.items[item.id] = item # type: ignore
        return item
    

    def delete(self, item: T) -> None:
        if item.id not in self.items: # type: ignore
            raise errors.NotFoundError(
                f'Unable to find an item with id={item.id}', # type: ignore
            )

        del self.items[item.id] # type: ignore


class FakeCartRepository(FakeRepository[market.modules.cart.domain.models.CartItem]):
    pass


class FakeImageRepository(FakeRepository[market.modules.image.domain.models.Image]):
    pass


class FakeProductRepository(FakeRepository[market.modules.product.domain.models.Product]):
    def add(
        self,
        item: market.modules.product.domain.models.Product,
    ) -> market.modules.product.domain.models.Product:
        item.added = datetime.datetime.now()
        item.last_updated = datetime.datetime.now()
        return super().add(item)


class FakeProductImageRepository(
    FakeRepository[market.modules.product_image.domain.models.ProductImage],
):
    pass


class FakeUserRepository(FakeRepository[market.modules.user.domain.models.User]):
    pass
