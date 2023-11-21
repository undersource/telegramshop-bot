from bot.misc.database import session
from bot.misc.database import Category, Product, Shipping


def addCategory(name: str):
    category = Category()
    category.name = name

    session.add(category)
    session.commit()


def addProduct(
    name: str,
    description: str,
    price: float,
    discount: float,
    picture_path: str,
    file_path: str,
    real: bool,
    category: str
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
    product.category_id = category

    session.add(product)
    session.commit()


def addShipping(title: str, price: float):
    shipping = Shipping()
    shipping.title = title
    shipping.price = price

    session.add(shipping)
    session.commit()
