from market.services import unit_of_work


class FakeUnitOfWork(unit_of_work.UnitOfWork):
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
