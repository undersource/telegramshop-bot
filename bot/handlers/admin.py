from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.misc.settings import PRODUCT_IMAGES_DIR, VIRTUAL_PRODUCTS_DIR
from bot.misc.database import session
from bot.misc.database import User, Category, Product, Shipping, Shop
from bot.misc.database import Order, OrderedProduct, CustomerAddress
from bot.misc.utils import addCategory, addProduct, addShipping
from bot.keyboards.dialogs import *
from os import remove
from os.path import isfile


class FSMCategory(StatesGroup):
    name = State()


class FSMProduct(StatesGroup):
    real = State()
    name = State()
    category = State()
    description = State()
    price = State()
    discount = State()
    photo = State()
    file = State()


class FSMShipping(StatesGroup):
    title = State()
    price = State()


class FSMShop(StatesGroup):
    faq = State()


async def add_category(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        await FSMCategory.name.set()
        await message.answer("Enter name of category", reply_markup=markup)


async def adding_category(message: Message, state: FSMContext):
    name = message.text
    query = session.query(Category).filter(Category.name == name).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        return await message.reply(
            "Category with name {name} exists.\nEnter again".format(name=name),
            reply_markup=markup,
        )

    addCategory(name)

    await message.answer(
        "Category \"{name}\" has been added".format(name=name)
    )
    await state.finish()


async def delete_category(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        queries = session.query(Category).all()

        markup = InlineKeyboardMarkup()

        if queries != []:
            for query in queries:
                category_b = InlineKeyboardButton(
                    query.name, callback_data=f"del_category:{query.id}"
                )
                markup.add(category_b)

            await message.answer(
                "Choose category to delete:",
                reply_markup=markup
            )
        else:
            await message.answer("No categories")


async def deleting_category(call: CallbackQuery):
    category_id = call.data.split(":")[1]

    query = session.query(Category).filter(
        Category.id.in_((category_id,))
    ).first()

    if query is not None:
        name = query.name

        session.delete(query)
        session.commit()

        await call.message.answer("{name} has been deleted".format(name=name))


async def add_product(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        yes_b = InlineKeyboardButton(yes_m, callback_data="real_yes")
        no_b = InlineKeyboardButton(no_m, callback_data="real_no")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(yes_b, no_b, cancel_b)

        await FSMProduct.real.set()
        await message.reply("Your product is real?", reply_markup=markup)


async def process_product_type(call: CallbackQuery, state: FSMContext):
    real = call.data

    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(cancel_b)

    async with state.proxy() as data:
        if real == "real_yes":
            data["real"] = True
        else:
            data["real"] = False

    await FSMProduct.next()
    await call.message.reply("Enter name of product", reply_markup=markup)


async def process_product_name(message: Message, state: FSMContext):
    name = message.text

    query = session.query(Product).filter(Product.name.in_((name,))).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        return await message.reply(
            "Product with name {name} exists.\nEnter again".format(name=name),
            reply_markup=markup,
        )

    async with state.proxy() as data:
        data["name"] = name

    queries = session.query(Category).all()

    markup = InlineKeyboardMarkup()

    if queries != []:
        for query in queries:
            category_b = InlineKeyboardButton(
                query.name,
                callback_data=f"category:{query.id}"
            )
            markup.add(category_b)

        skip_b = InlineKeyboardButton(skip_m, callback_data="skip_category")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup.add(skip_b, cancel_b)

        await FSMProduct.next()
        await message.reply("Choose category of product", reply_markup=markup)
    else:
        skip_b = InlineKeyboardButton(skip_m, callback_data="skip_description")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(skip_b, cancel_b)

        async with state.proxy() as data:
            data["category"] = None

        await FSMProduct.next()
        await call.message.reply(
            "Enter description of product", reply_markup=markup
        )
       

async def skipped_process_product_category(
    call: CallbackQuery,
    state: FSMContext
):
    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_description")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["category"] = None

    await FSMProduct.next()
    await call.message.reply(
        "Enter description of product", reply_markup=markup
    )


async def process_product_category(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_description")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["category"] = category_id

    await FSMProduct.next()
    await call.message.reply("Enter description of product", reply_markup=markup)


async def skipped_process_product_description(
    call: CallbackQuery,
    state: FSMContext
):
    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_price")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["description"] = None

    await FSMProduct.next()
    await call.message.reply("Enter price of product", reply_markup=markup)


async def process_product_description(message: Message, state: FSMContext):
    description = message.text

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_price")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["description"] = description

    await FSMProduct.next()
    await message.reply("Enter price of product ($)", reply_markup=markup)


async def skipped_process_product_price(
    call: CallbackQuery,
    state: FSMContext
):
    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_discount")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["price"] = 0

    await FSMProduct.next()
    await call.message.reply(
        "Enter discount of product (%)",
        reply_markup=markup
    )


async def process_product_price(message: Message, state: FSMContext):
    price = message.text

    if not price.isdigit():
        skip_b = InlineKeyboardButton(skip_m, callback_data="skip_price")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(skip_b, cancel_b)

        return await message.reply(
            "Price gotta be a number.\nEnter price of product (digits only)",
            reply_markup=markup,
        )

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_discount")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["price"] = price

    await FSMProduct.next()
    await message.reply("Enter discount of product (%)", reply_markup=markup)


async def skipped_process_product_discount(
    call: CallbackQuery,
    state: FSMContext
):
    discount = 0

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_photo")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["discount"] = discount

    await FSMProduct.next()
    await call.message.reply("Load photo of product", reply_markup=markup)


async def process_product_discount(message: Message, state: FSMContext):
    discount = message.text

    if not discount.isdigit():
        skip_b = InlineKeyboardButton(skip_m, callback_data="skip_discount")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="Cancel")
        markup = InlineKeyboardMarkup()
        markup.add(skip_b, cancel_b)

        return await message.reply(
            "Discount gotta be a number.\nEnter again (digits only)",
            reply_markup=markup,
        )

    if int(discount) >= 100 and int(discount) <= 0:
        skip_b = InlineKeyboardButton(skip_m, callback_data="skip_discount")
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="Cancel")
        markup = InlineKeyboardMarkup()
        markup.add(skip_b, cancel_b)

        return await message.reply(
            "Discount gotta be more then 0 and less then 100.\n"
            "Enter again (digits only)",
            reply_markup=markup,
        )

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_photo")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="Cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["discount"] = discount

    await FSMProduct.next()
    await message.reply("Load photo of product", reply_markup=markup)


async def skipped_process_product_photo(
    call: CallbackQuery,
    state: FSMContext
):
    async with state.proxy() as data:
        if data["real"] is False:
            data["photo"] = None

            cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
            markup = InlineKeyboardMarkup()
            markup.add(cancel_b)

            await FSMProduct.next()
            await call.message.reply(
                "Load file (no more then 2GB)", reply_markup=markup
            )
        else:
            name = data["name"]
            description = data["description"]
            price = data["price"]
            discount = data["discount"]
            picture_path = None
            file_path = None
            real = data["real"]
            category = data["category"]

            addProduct(
                name,
                description,
                price,
                discount,
                picture_path,
                file_path,
                real,
                category
            )

            await call.message.answer(
                "Product {name} has been added".format(name=data["name"])
            )
            await state.finish()


async def process_product_photo(message: Message, state: FSMContext):
    photo = message.document
    IsDocument = True

    if photo is None:
        photo = message.photo[0]
        IsDocument = False

    async with state.proxy() as data:
        data["photo"] = photo.file_id

        if data["real"] is False:
            cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
            markup = InlineKeyboardMarkup()
            markup.add(cancel_b)

            await FSMProduct.next()
            await message.reply(
                "Load file (no more then 2GB)",
                reply_markup=markup
            )
        else:
            name = data["name"]
            description = data["description"]
            price = data["price"]
            discount = data["discount"]
            picture_path = f"{PRODUCT_IMAGES_DIR}/{data['name']}"
            file_path = None
            real = data["real"]
            category = data["category"]

            addProduct(
                name,
                description,
                price,
                discount,
                picture_path,
                file_path,
                real,
                category
            )

            if IsDocument:
                await message.document.download(
                    destination_file=f"{PRODUCT_IMAGES_DIR}/{data['name']}"
                )
            else:
                await message.photo[0].download(
                    destination_file=f"{PRODUCT_IMAGES_DIR}/{data['name']}"
                )

            await message.answer(
                "Product {name} has been added".format(name=data["name"])
            )
            await state.finish()


async def process_product_file(message: Message, state: FSMContext):
    file_id = message.document.file_id

    async with state.proxy() as data:
        name = data["name"]
        description = data["description"]
        price = data["price"]
        discount = data["discount"]

        if data["photo"] is not None:
            picture_path = f"{PRODUCT_IMAGES_DIR}/{data['name']}"
            photo = await message.bot.get_file(data["photo"])

            await message.bot.download_file(photo.file_path, picture_path)
        else:
            picture_path = None

        file_path = f"{VIRTUAL_PRODUCTS_DIR}/{data['name']}"

        await message.document.download(destination_file=file_path)

        real = data["real"]
        category = data["category"]

        addProduct(
            name,
            description,
            price,
            discount,
            picture_path,
            file_path,
            real,
            category
        )

    await message.answer(
        "Product {name} has been added".format(name=data["name"])
    )
    await state.finish()


async def add_shipping(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        await FSMShipping.title.set()
        await message.reply("Enter title of shipping", reply_markup=markup)


async def process_shipping_title(message: Message, state: FSMContext):
    title = message.text

    query = session.query(Shipping).filter(
        Shipping.title.in_((title,))
    ).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        return await message.reply(
            "Shipping with title {title} exists.\nEnter again".format(
                title=title
            ),
            reply_markup=markup,
        )

    skip_b = InlineKeyboardButton(skip_m, callback_data="skip_price")
    cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
    markup = InlineKeyboardMarkup()
    markup.add(skip_b, cancel_b)

    async with state.proxy() as data:
        data["title"] = title

    await FSMShipping.next()
    await message.reply("Enter price of shipping", reply_markup=markup)


async def skipped_process_shipping_price(
    call: CallbackQuery,
    state: FSMContext
):
    async with state.proxy() as data:
        title = data["title"]
        price = 0

        addShipping(title, price)

        await call.message.answer(
            "Shipping {title} has been added".format(title=data["title"])
        )
        await state.finish()


async def process_shipping_price(message: Message, state: FSMContext):
    if not price.isdigit():
        return await message.reply(
            "Price gotta be a number.\nEnter price of product (digits only)",
        )

    async with state.proxy() as data:
        title = data["title"]
        price = message.text

        addShipping(title, price)

        await call.message.answer(
            "Shipping {title} has been added".format(title=data["title"])
        )
        await state.finish()


async def delete_product(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        queries = session.query(Product).all()

        markup = InlineKeyboardMarkup()

        if queries != []:
            for query in queries:
                product_b = InlineKeyboardButton(
                    query.name, callback_data=f"del_product:{query.id}"
                )
                markup.add(product_b)

            await message.answer(
                "Choose product to delete:",
                reply_markup=markup
            )
        else:
            await message.answer("No products")


async def deleting_product(call: CallbackQuery):
    product_id = call.data.split(":")[1]

    query = session.query(Product).filter(
        Product.id.in_((product_id,))
    ).first()

    if query is not None:
        name = query.name
        picture_path = query.picture_path
        file_path = query.file_path

        if picture_path is not None:
            if isfile(picture_path):
                remove(picture_path)

        if file_path is not None:
            if isfile(file_path):
                remove(file_path)

        session.delete(query)
        session.commit()

        await call.message.answer("{name} has been deleted".format(name=name))


async def delete_shipping(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        queries = session.query(Shipping).all()

        markup = InlineKeyboardMarkup()

        if queries != []:
            for query in queries:
                shipping_b = InlineKeyboardButton(
                    query.title, callback_data=f"del_shipping:{query.id}"
                )

            markup.add(shipping_b)

            await message.answer(
                "Choose shipping to delete:",
                reply_markup=markup
            )
        else:
            await message.answer("No shippings")


async def deleting_shipping(call: CallbackQuery):
    shipping_id = call.data.split(":")[1]

    query = session.query(Shipping).filter(
        Shipping.id.in_((shipping_id,))
    ).first()

    if query is not None:
        title = query.title

        session.delete(query)
        session.commit()

        await call.message.answer(
            "{title} has been deleted".format(title=title)
        )


async def change_faq(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        cancel_b = InlineKeyboardButton(cancel_m, callback_data="cancel")
        markup = InlineKeyboardMarkup()
        markup.add(cancel_b)

        await FSMShop.faq.set()
        await message.answer("Enter new FAQ", reply_markup=markup)


async def changing_faq(message: Message, state: FSMContext):
    shop = session.query(Shop).filter(Shop.id == 1).first()

    shop.welcome = message.text

    session.add(shop)
    session.commit()

    await message.answer("FAQ has been changed")
    await state.finish()


async def cancel(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await call.message.reply("Action has been stopped")


async def list_orders(message: Message):
    username = message.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        queries = session.query(Order).filter(Order.delivered == "False").all()

        markup = InlineKeyboardMarkup()

        if queries != []:
            for query in queries:
                order_b = InlineKeyboardButton(
                    f"{query.id}:    {query.date}",
                    callback_data=f"order:{query.id}"
                )
                markup.add(order_b)

            await message.answer("All orders:", reply_markup=markup)
        else:
            await message.answer("Now, we haven't orders")


async def order_details(call: CallbackQuery):
    username = call.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        order_id = call.data.split(':')[1]

        OrderedProductQuery = session.query(OrderedProduct).filter(
            OrderedProduct.order_id.in_((order_id,))
        ).first()

        CustomerAddressQuery = session.query(CustomerAddress).filter(
            CustomerAddress.order_id.in_((order_id,))
        ).first()

        ProductQuery = session.query(Product).filter(
            Product.id.in_((OrderedProduct.product_id,))
        ).first()

        mark_as_delivered_b = InlineKeyboardButton(
            mark_as_delivered_m,
            callback_data=f"delivered:{order_id}"
        )
        markup = InlineKeyboardMarkup()
        markup.add(mark_as_delivered_b)

        await call.message.answer(
            "{name}    x{count}\n\n"
            "Country code: {country_code}\n"
            "State: {state}\n"
            "City: {city}\n"
            "Street line 1: {street_line1}\n"
            "Street line 2: {street_line2}\n"
            "Post code: {post_code}".format(
                name=ProductQuery.name,
                count=OrderedProductQuery.count,
                country_code=CustomerAddressQuery.country_code,
                state=CustomerAddressQuery.state,
                city=CustomerAddressQuery.city,
                street_line1=CustomerAddressQuery.street_line1,
                street_line2=CustomerAddressQuery.street_line2,
                post_code=CustomerAddressQuery.post_code
            ),
            reply_markup=markup
        )


async def mark_as_delivered(call: CallbackQuery):
    username = call.from_user.username
    query = session.query(User).filter(User.name.in_((username,))).first()

    if query is not None:
        order_id = call.data.split(':')[1]

        session.query(Order).filter(Order.id == order_id).update(
            {"delivered": True}
        )
        session.commit()

        await call.message.answer(
            "Order {order_id} has been marked as delivered".format(
                order_id=order_id
            )
        )


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(add_category, text=add_category_m, state=None)
    dp.register_message_handler(
        adding_category,
        content_types=["text"],
        state=FSMCategory.name
    )
    dp.register_message_handler(delete_category, text=del_category_m)
    dp.register_callback_query_handler(
        deleting_category,
        lambda call: call.data.split(":")[0] == "del_category"
    )
    dp.register_message_handler(add_product, text=add_product_m, state=None)
    dp.register_callback_query_handler(
        process_product_type,
        lambda call: call.data in ("real_yes", "real_no"),
        state=FSMProduct.real
    )
    dp.register_message_handler(
        process_product_name,
        content_types=["text"],
        state=FSMProduct.name
    )
    dp.register_callback_query_handler(
        skipped_process_product_category,
        text="skip_category",
        state=FSMProduct.category
    )
    dp.register_callback_query_handler(
        process_product_category,
        lambda call: call.data.split(":")[0] == "category",
        state=FSMProduct.category
    )
    dp.register_callback_query_handler(
        skipped_process_product_description,
        text="skip_description",
        state=FSMProduct.description
    )
    dp.register_message_handler(
        process_product_description,
        content_types=["text"],
        state=FSMProduct.description
    )
    dp.register_callback_query_handler(
        skipped_process_product_price,
        text="skip_price",
        state=FSMProduct.price
    )
    dp.register_message_handler(
        process_product_price,
        content_types=["text"],
        state=FSMProduct.price
    )
    dp.register_callback_query_handler(
        skipped_process_product_discount,
        text="skip_discount",
        state=FSMProduct.discount
    )
    dp.register_message_handler(
        process_product_discount,
        content_types=["text"],
        state=FSMProduct.discount
    )
    dp.register_callback_query_handler(
        skipped_process_product_photo,
        text="skip_photo",
        state=FSMProduct.photo
    )
    dp.register_message_handler(
        process_product_photo,
        content_types=["document", "photo"],
        state=FSMProduct.photo
    )
    dp.register_message_handler(
        process_product_file,
        content_types=["document"],
        state=FSMProduct.file
    )

    dp.register_message_handler(add_shipping, text=add_shipping_m, state=None)
    dp.register_message_handler(
        process_shipping_title,
        content_types=["text"],
        state=FSMShipping.title
    )
    dp.register_callback_query_handler(
        skipped_process_shipping_price,
        text="skip_price",
        state=FSMShipping.price
    )
    dp.register_message_handler(
        process_shipping_price,
        content_types=["text"],
        state=FSMShipping.price
    )

    dp.register_message_handler(delete_product, text=del_product_m)
    dp.register_callback_query_handler(
        deleting_product,
        lambda call: call.data.split(":")[0] == "del_product"
    )

    dp.register_message_handler(delete_shipping, text=del_shipping_m)
    dp.register_callback_query_handler(
        deleting_shipping,
        lambda call: call.data.split(":")[0] == "del_shipping"
    )

    dp.register_message_handler(change_faq, text=change_faq_m, state=None)
    dp.register_message_handler(
        changing_faq, content_types=["text"],
        state=FSMShop.faq
    )

    dp.register_callback_query_handler(cancel, text="cancel", state="*")

    dp.register_message_handler(list_orders, text=list_orders_m)
    dp.register_callback_query_handler(
        order_details,
        lambda call: call.data.split(":")[0] == "order"
    )
    dp.register_callback_query_handler(
        mark_as_delivered,
        lambda call: call.data.split(":")[0] == "delivered"
    )
