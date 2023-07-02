import datetime
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import fastapi.testclient
import pytest

import market.modules.user.repositories
import market.modules.product.domain.models
import market.services
from market.apps.fastapi_app import deps
from market.apps.fastapi_app import fastapi_main
from market.common import errors
from market.services import unit_of_work


class FakeRepository:
    items: Dict[Any, Any]


    def __init__(self, items: Optional[List[Any]] = None) -> None:
        if items is None:
            items = []

        self.items = {item.id: item for item in items}
    

    def list(self, **filters) -> List[Any]:
        filtered_items = []
        for item in self.items.values():
            for k, v in filters.items():
                if getattr(item, k) == v:
                    filtered_items.append(item)
        return filtered_items
    

    def get(self, item_id: Any) -> Any:
        if item_id not in self.items:
            raise errors.NotFoundError(
                f'Unable to find an item with id={item_id}',
            )

        return self.items.get(item_id)
    

    def add(self, item: Any) -> Any:
        self.items[item.id] = item
        return item
    

    def delete(self, item: Any) -> None:
        if item.id not in self.items:
            raise errors.NotFoundError(
                f'Unable to find an item with id={item.id}',
            )

        del self.items[item.id]


class FakeProductRepository(FakeRepository):
    def __init__(self, items: Optional[List[Any]] = None) -> None:
        super().__init__(items)
    

    def add(self, item: Any) -> Any:
        item.added = datetime.datetime.now()
        item.last_updated = datetime.datetime.now()
        return super().add(item)


class FakeUnitOfWork(unit_of_work.UnitOfWork):
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def client():
    uow = FakeUnitOfWork(
        cart=FakeRepository([]),
        images=FakeRepository([]),
        products=FakeProductRepository([]),
        product_images=FakeRepository([]),
        users=FakeRepository([]),
    )
    fill_db(uow)
    app = fastapi_main.app
    app.dependency_overrides[deps.get_uow] = lambda: uow
    yield fastapi.testclient.TestClient(app)
    del app.dependency_overrides[deps.get_uow]


def fill_db(uow: unit_of_work.UnitOfWork) -> None:
    auth_service = market.services.AuthService(uow.users)

    test_user_1 = auth_service.register_user(
        user_id=uuid.uuid4(),
        username='testuser1',
        password='testuser1',
        full_name='Some Test User',
    )
    test_user_2 = auth_service.register_user(
        user_id=uuid.uuid4(),
        username='testuser2',
        password='testuser2',
        full_name='Another Test User',
    )
    
    uow.commit()
    
    
    # Adding 2 test products
    test_product_1 = market.modules.product.domain.models.Product(
        id=uuid.uuid4(),
        title='Some test product',
        stock=10,
        price_rub=1000,
        owner_id=test_user_1.id,
    )
    uow.products.add(test_product_1)

    test_product_2 = market.modules.product.domain.models.Product(
        id=uuid.uuid4(),
        title='Another test product',
        stock=0,
        price_rub=100,
        owner_id=test_user_2.id,
    )
    uow.products.add(test_product_2)

    uow.commit()
