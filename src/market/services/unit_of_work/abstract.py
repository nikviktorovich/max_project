import market.modules.cart.repositories
import market.modules.image.repositories
import market.modules.product.repositories
import market.modules.product_image.repositories
import market.modules.user.repositories


class UnitOfWork:
    """Abstract Unit Of Work pattern class"""
    cart: market.modules.cart.repositories.CartRepository
    images: market.modules.image.repositories.ImageRepository
    products: market.modules.product.repositories.ProductRepository
    product_images: market.modules.product_image.\
        repositories.ProductImageRepository
    users: market.modules.user.repositories.UserRepository


    def __enter__(self) -> 'UnitOfWork':
        ...
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
    

    def commit(self) -> None:
        ...
    

    def rollback(self) -> None:
        ...
