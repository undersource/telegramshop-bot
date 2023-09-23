from bot.misc.database import session
from bot.misc.database import Product, Shipping


def addProduct(
    name: str,
    description: str,
    price: float,
    discount: float,
    picture_path: str,
    file_path: str,
    real: bool
):
    product = Product()
    product.name = name

    if description is not None:
        product.description = description

    product.price = price
    product.discount = discount

    if picture_path is not None:
        product.picture_path = picture_path

    if file_path is not None:
        product.file_path = file_path

    product.real = real

    session.add(product)
    session.commit()


def addShipping(title: str, price: float):
    shipping = Shipping()
    shipping.title = title
    shipping.price = price

    session.add(shipping)
    session.commit()
