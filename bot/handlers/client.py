from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import ShippingQuery, ShippingOption
from aiogram.types import PreCheckoutQuery, LabeledPrice
from aiogram.types.message import ContentType
from datetime import datetime
from os.path import isfile
from bot.misc.settings import IMAGES_ROOT
from bot.misc.database import session, r
from bot.misc.database import Shop, User
from bot.misc.database import Category, Product, Shipping
from bot.misc.database import Order, OrderedProduct, CustomerAddress
from bot.misc.config import config
from bot.misc.logger import logger
from bot.keyboards.dialogs import *

PAYMENTS_TOKEN = config["aiogram"]["PAYMENTS_TOKEN"]


async def start(message: Message):
    user_id = message.from_user.id
    categories = session.query(Category).all()

    list_categories_b = InlineKeyboardButton(
        list_categories_m,
        callback_data=list_categories_m
    )
    list_products_b = InlineKeyboardButton(
        list_products_m,
        callback_data=list_products_m
    )
    cart_b = InlineKeyboardButton(
        cart_m,
        callback_data=cart_m
    )
    empty_cart_b = InlineKeyboardButton(
        empty_cart_m,
        callback_data=empty_cart_m
    )
    markup = InlineKeyboardMarkup()

    cart = r.hgetall(user_id)

    if categories != []:
        markup.add(list_categories_b, list_products_b)
    else:
        markup.add(list_products_b)

    if cart != {}:
        markup.add(cart_b, empty_cart_b)

    query = session.query(Shop).filter(
        Shop.id.in_((1,))
    ).first()

    if query is not None:
        await message.answer(
            "Welcome {name}!\n\n{faq}".format(
                name=message.from_user.full_name,
                faq=query.welcome
            ),
            reply_markup=markup
        )
    else:
        await message.answer(
            "Welcome {name}!".format(name=message.from_user.full_name),
            reply_markup=markup
        )

    logger.info(
        "{name} has been started".format(name=message.from_user.username)
    )


async def list_categories(call: CallbackQuery):
    queries = session.query(Category).all()

    markup = InlineKeyboardMarkup()

    if queries != []:
        for query in queries:
            category_b = InlineKeyboardButton(
                query.name,
                callback_data=f"category:{query.id}"
            )
            markup.add(category_b)

        await call.message.answer("All categories:", reply_markup=markup)
    else:
        cart_b = InlineKeyboardButton(
            cart_m,
            callback_data=cart_m
        )
        markup.add(cart_b)

        await call.message.answer(
            "Now, we haven't categories",
            reply_markup=markup
        )


async def category_details(call: CallbackQuery):
    category_id = call.data.split(':')[1]
    category = session.query(Category).filter(
        Category.id.in_((category_id,))
    ).first()
    queries = session.query(Product).filter(
        Product.category_id.in_((category_id,))
    ).all()

    markup = InlineKeyboardMarkup()

    if queries != []:
        for query in queries:
            product_b = InlineKeyboardButton(
                query.name,
                callback_data=f"product:{query.id}"
            )
            markup.add(product_b)

        await call.message.answer(
            "{name}: ".format(name=category.name), reply_markup=markup
        )
    else:
        cart_b = InlineKeyboardButton(
            cart_m,
            callback_data=cart_m
        )
        markup.add(cart_b)

        await call.message.answer(
            "Now, we haven't products in this category",
            reply_markup=markup
        )


async def list_products(call: CallbackQuery):
    queries = session.query(Product).all()

    markup = InlineKeyboardMarkup()

    if queries != []:
        for query in queries:
            product_b = InlineKeyboardButton(
                query.name,
                callback_data=f"product:{query.id}"
            )
            markup.add(product_b)

        await call.message.answer("All products:", reply_markup=markup)
    else:
        cart_b = InlineKeyboardButton(
            cart_m,
            callback_data=cart_m
        )
        markup.add(cart_b)

        await call.message.answer(
            "Now, we haven't products",
            reply_markup=markup
        )


async def product_details(call: CallbackQuery):
    product_id = call.data.split(':')[1]

    query = session.query(Product).filter(
        Product.id.in_((product_id,))
    ).first()

    if query is not None:
        name = query.name
        description = query.description
        price = query.price
        discount = query.discount
        picture_path = query.picture_path
        file_path = query.file_path
        real = query.real

        add_to_cart_b = InlineKeyboardButton(
            add_to_cart_m,
            callback_data=f"add_to_cart:{query.id}"
        )
        markup = InlineKeyboardMarkup()
        markup.add(add_to_cart_b)

        if picture_path is not None:
            if isfile(picture_path):
                with open(picture_path, "rb") as picture:
                    if discount != 0:
                        discounted_price = price - (price * discount / 100)
                    else:
                        discounted_price = price

                    await call.message.answer_photo(
                        picture,
                        "{name}\n\n"
                        "{description}\n\n"
                        "(-{discount}%)  <del>${price}</del>  ${discounted_price}\n\n"
                        "Type: {product_type}".format(
                            name=name,
                            description="" if description is None else description,
                            discount=int(discount),
                            price=float(price),
                            discounted_price=float(discounted_price),
                            product_type="Delivered" if real else "Virtual"
                        ),
                        parse_mode="html",
                        reply_markup=markup
                    )
        else:
            if discount != 0:
                discounted_price = price - (price * discount / 100)
            else:
                discounted_price = price

            await call.message.answer(
                "{name}\n\n"
                "{description}"
                "(-{discount}%)  <del>${price}</del>  ${discounted_price}\n\n"
                "Type: {product_type}".format(
                    name=name,
                    description="" if description is None else description + "\n\n",
                    discount=int(discount),
                    price=float(price),
                    discounted_price=float(discounted_price),
                    product_type="Delivered" if real else "Virtual"
                ),
                parse_mode="html",
                reply_markup=markup
            )


async def add_to_cart(call: CallbackQuery):
    user_id = call.from_user.id
    product_id = call.data.split(':')[1]

    query = session.query(Product).filter(
        Product.id.in_((product_id,))
    ).first()

    if query is not None:
        product_count = r.hget(user_id, product_id)

        list_products_b = InlineKeyboardButton(
            list_products_m,
            callback_data=list_products_m
        )
        cart_b = InlineKeyboardButton(
            cart_m,
            callback_data=cart_m
        )
        markup = InlineKeyboardMarkup()
        markup.add(list_products_b, cart_b)

        if product_count is None:
            r.hset(user_id, product_id, 1)

            await call.message.answer(
                "{name} has been added to cart".format(name=query.name),
                reply_markup=markup
            )
        else:
            if query.real:
                r.hset(user_id, product_id, int(product_count) + 1)

                await call.message.answer(
                    "{name} has been added to cart".format(name=query.name),
                    reply_markup=markup
                )


async def del_from_cart(call: CallbackQuery):
    user_id = call.from_user.id

    product_id = call.data.split(':')[1]

    query = session.query(Product).filter(
        Product.id.in_((product_id,))
    ).first()

    if query is not None:
        product_count = r.hget(user_id, product_id)

        if product_count is not None:
            if int(product_count) <= 1:
                r.hdel(user_id, product_id)
            else:
                r.hset(user_id, product_id, int(product_count) - 1)

        list_products_b = InlineKeyboardButton(
            list_products_m,
            callback_data=list_products_m
        )
        cart_b = InlineKeyboardButton(
            cart_m,
            callback_data=cart_m
        )
        markup = InlineKeyboardMarkup()
        markup.add(list_products_b, cart_b)

        await call.message.answer(
            "{name} has been deleted from cart".format(name=query.name),
            reply_markup=markup
        )


async def empty_cart(call: CallbackQuery):
    user_id = call.from_user.id

    cart = r.hgetall(user_id)

    if cart != {}:
        r.delete(user_id)

        list_products_b = InlineKeyboardButton(
            list_products_m,
            callback_data=list_products_m
        )
        markup = InlineKeyboardMarkup()
        markup.add(list_products_b)

        await call.message.answer(
            "Cart has been emptied",
            reply_markup=markup
        )


async def cart(call: CallbackQuery):
    user_id = call.from_user.id

    all_products = r.hgetall(user_id)

    total_price = 0

    for product_id in all_products:
        query = session.query(Product).filter(
            Product.id.in_((product_id,))
        ).first()

        if query is not None:
            product_count = all_products[product_id]

            name = query.name
            description = query.description
            price = query.price
            discount = query.discount
            picture_path = query.picture_path
            file_path = query.file_path
            real = query.real

            add_to_cart_b = InlineKeyboardButton(
                add_to_cart_m,
                callback_data=f"add_to_cart:{query.id}"
            )
            del_from_cart_b = InlineKeyboardButton(
                del_from_cart_m,
                callback_data=f"del_from_cart:{query.id}"
            )
            markup = InlineKeyboardMarkup()
            markup.add(add_to_cart_b, del_from_cart_b)

            if isfile(picture_path):
                with open(picture_path, "rb") as picture:
                    if description is None:
                        description = ""

                    if discount != 0:
                        discounted_price = price - (price * discount / 100)
                    else:
                        discounted_price = price

                    if real:
                        product_type = "Delivered"
                    else:
                        product_type = "Virtual"

                    total_price += (
                        discounted_price * int(all_products[product_id])
                    )

                    await call.message.answer_photo(
                        picture,
                        "{name}    x{product_count}\n\n"
                        "{description}\n\n"
                        "${discounted_price}    <del>${price}</del>\n\n"
                        "Type: {product_type}".format(
                            name=name,
                            product_count=product_count,
                            description=description,
                            discounted_price=float(discounted_price),
                            price=float(price),
                            product_type=product_type
                        ),
                        parse_mode="html",
                        reply_markup=markup
                    )
            else:
                if description is None:
                    description = ""

                if discount != 0:
                    discounted_price = price - (price * discount / 100)
                else:
                    discounted_price = price

                if real:
                    product_type = "Delivered"
                else:
                    product_type = "Virtual"

                total_price += (
                    discounted_price * int(all_products[product_id])
                )

                await call.message.answer(
                    "{name}    (x{product_count})\n\n"
                    "{description}\n\n"
                    "${discounted_price}    <del>${price}</del>\n\n"
                    "Type: {product_type}".format(
                        name=name,
                        product_count=product_count,
                        description=description,
                        discounted_price=float(discounted_price),
                        price=float(price),
                        product_type=product_type
                    ),
                    parse_mode="html",
                    reply_markup=markup
                )

    list_products_b = InlineKeyboardButton(
        list_products_m,
        callback_data=list_products_m
    )
    empty_cart_b = InlineKeyboardButton(
        empty_cart_m,
        callback_data=empty_cart_m
    )
    checkout_b = InlineKeyboardButton(
        checkout_m,
        callback_data=checkout_m
    )
    markup = InlineKeyboardMarkup()
    markup.add(list_products_b, empty_cart_b, checkout_b)

    await call.message.answer(
        "💸 Total: ${total_price}".format(total_price=float(total_price)),
        reply_markup=markup
    )


async def checkout(call: CallbackQuery):
    user_id = call.from_user.id

    all_products = r.hgetall(user_id)

    total_price = 0

    products = ""

    have_real = False

    for product_id in all_products:
        query = session.query(Product).filter(
            Product.id.in_((product_id,))
        ).first()

        if query is not None:
            product_count = all_products[product_id]

            name = query.name
            price = query.price
            discount = query.discount
            real = query.real

            if discount != 0:
                discounted_price = price - (price * discount / 100)
            else:
                discounted_price = price

            if real:
                have_real = True

            total_price += (
                discounted_price * int(all_products[product_id])
            )

            products += "📦 {name}    x{count}    ".format(
                name=name,
                count=all_products[product_id]
            )

    if total_price < 1:
        total_price = 1

    price = LabeledPrice(label="Buy", amount=int(total_price * 100))

    await call.bot.send_invoice(
        call.message.chat.id,
        title="Buy",
        description=products,
        provider_token=PAYMENTS_TOKEN,
        currency="usd",
        photo_url="https://clipartcraft.com/images/stripe-logo-two-5.png",
        is_flexible=have_real,
        prices=[price],
        payload=f"{all_products}"
    )


async def shipping(query: ShippingQuery):
    shipping_options = []

    shipping_queries = session.query(Shipping).all()

    if shipping_queries != []:
        for shipping_query in shipping_queries:
            option = ShippingOption(
                id=shipping_query.id,
                title=shipping_query.title
            ).add(LabeledPrice(
                shipping_query.title,
                int(shipping_query.price)
            ))

            shipping_options.append(option)
    else:
        option = ShippingOption(
            id=0,
            title="Shipping"
        ).add(LabeledPrice("Shipping", 0))

        shipping_options.append(option)

    await query.bot.answer_shipping_query(
        query.id,
        ok=True,
        shipping_options=shipping_options
    )


async def pre_checkout(query: PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)


async def paid(message: Message):
    user_id = message.from_user.id
    payment = message.successful_payment
    ordered_products = eval(payment.invoice_payload)

    for product_id in ordered_products:
        query = session.query(Product).filter(
            Product.id.in_((product_id,))
        ).first()

        r.hdel(user_id, product_id)

        if query is not None:
            if query.real:
                address = payment.order_info.shipping_address

                order = Order()
                ordered_product = OrderedProduct()
                customer_address = CustomerAddress()

                order.currency = payment.currency
                order.total_amount = payment.total_amount / 100

                session.add(order)
                session.commit()

                ordered_product.order_id = order.id
                ordered_product.product_id = product_id
                ordered_product.count = ordered_products[product_id]

                customer_address.order_id = order.id
                customer_address.country_code = address.country_code
                customer_address.state = address.state
                customer_address.city = address.city
                customer_address.street_line1 = address.street_line1
                customer_address.street_line2 = address.street_line2
                customer_address.post_code = address.post_code

                session.add(ordered_product)
                session.add(customer_address)
                session.commit()
            else:
                with open(query.file_path, "rb") as file:
                    await message.answer_document(file)

            logger.info(
                "{name} make order {order_id}".format(
                    name=message.from_user.username,
                    order_id=order.id
                )
            )


async def admin(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(
        User.name.in_((username,))
    ).first()

    if query is not None:
        change_faq_b = KeyboardButton(change_faq_m)
        list_orders_b = KeyboardButton(list_orders_m)
        add_category_b = KeyboardButton(add_category_m)
        del_category_b = KeyboardButton(del_category_m)
        add_product_b = KeyboardButton(add_product_m)
        del_product_b = KeyboardButton(del_product_m)
        add_shipping_b = KeyboardButton(add_shipping_m)
        del_shipping_b = KeyboardButton(del_shipping_m)
        admin_markup = ReplyKeyboardMarkup()
        admin_markup.add(
            change_faq_b,
            list_orders_b,
            add_category_b,
            del_category_b,
            add_product_b,
            del_product_b,
            add_shipping_b,
            del_shipping_b
        )

        await message.answer("Welcome admin!", reply_markup=admin_markup)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])
    dp.register_callback_query_handler(list_categories, text=list_categories_m)
    dp.register_callback_query_handler(
        category_details,
        lambda call: call.data.split(':')[0] == "category"
    )
    dp.register_callback_query_handler(list_products, text=list_products_m)
    dp.register_callback_query_handler(
        product_details,
        lambda call: call.data.split(':')[0] == "product"
    )
    dp.register_callback_query_handler(
        add_to_cart,
        lambda call: call.data.split(':')[0] == "add_to_cart"
    )
    dp.register_callback_query_handler(
        del_from_cart,
        lambda call: call.data.split(':')[0] == "del_from_cart"
    )
    dp.register_callback_query_handler(empty_cart, text=empty_cart_m)
    dp.register_callback_query_handler(cart, text=cart_m)
    dp.register_callback_query_handler(checkout, text=checkout_m)
    dp.register_shipping_query_handler(shipping, lambda query: True)
    dp.register_message_handler(
        paid,
        content_types=ContentType.SUCCESSFUL_PAYMENT
    )
    dp.register_pre_checkout_query_handler(pre_checkout, lambda query: True)
    dp.register_message_handler(admin, commands=["admin"])
