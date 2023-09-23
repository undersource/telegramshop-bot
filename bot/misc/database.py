from sqlalchemy import create_engine, Column
from sqlalchemy import Integer, Boolean, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import func
from bot.misc.config import config
from bot.misc.logger import logger
from redis import Redis

DB_TYPE = config["database"]["TYPE"]
DB_HOST = config["database"]["HOST"]
DB_PORT = config["database"]["PORT"]
DB_DATABASE = config["database"]["DATABASE"]
DB_USERNAME = config["database"]["USERNAME"]
DB_PASSWORD = config["database"]["PASSWORD"]
REDIS_HOST = config["redis"]["HOST"]
REDIS_PORT = config["redis"]["PORT"]
REDIS_PASSWORD = config["redis"]["PASSWORD"]

if DB_TYPE == "sqlite":
    DATABASE_URL = f"{DB_TYPE}:///{DB_DATABASE}"
elif DB_TYPE == "mariadb":
    DATABASE_URL = f"{DB_TYPE}+mariadbconnector://{DB_USERNAME}:{DB_PASSWORD}\
    @{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
elif DB_TYPE == "postgresql":
    DATABASE_URL = f"{DB_TYPE}+psycopg2://{DB_USERNAME}:{DB_PASSWORD}\
    @{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
else:
    logger.critical("Unsupported database type \"{DB_TYPE}\"")
    exit(1)


class Base(DeclarativeBase):
    id = Column("id", Integer, primary_key=True, index=True)


class Shop(Base):
    __tablename__ = "shop"

    welcome = Column("welcome", Text)


class User(Base):
    __tablename__ = "users"

    name = Column("name", Text, nullable=False, unique=True, index=True)


class Product(Base):
    __tablename__ = "products"

    name = Column("name", Text, nullable=False, unique=True, index=True)
    description = Column("description", Text)
    price = Column("price", DECIMAL(precision=12, scale=12), nullable=False)
    discount = Column("discount", Integer, nullable=False)
    picture_path = Column("picture_path", Text)
    file_path = Column("file_path", Text)
    real = Column("real", Boolean, nullable=False, index=True)


class Order(Base):
    __tablename__ = "orders"

    currency = Column("currency", Text, nullable=False)
    total_amount = Column("total_amount", Integer, nullable=False)
    date = Column(
        "date",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    delivered = Column(
        "delivered",
        Boolean,
        server_default="False",
        nullable=False,
        index=True
    )


class OrderedProduct(Base):
    __tablename__ = "ordered_products"

    order_id = Column(
        "order_id",
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )
    product_id = Column(
        "product_id",
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    count = Column("count", Integer, nullable=False)


class CustomerAddress(Base):
    __tablename__ = "customer_address"

    order_id = Column(
        "order_id",
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )
    country_code = Column("country_code", Text, nullable=False)
    state = Column("state", Text, nullable=False)
    city = Column("city", Text, nullable=False)
    street_line1 = Column("street_line1", Text, nullable=False)
    street_line2 = Column("street_line2", Text, nullable=False)
    post_code = Column("post_code", Text, nullable=False)


class Shipping(Base):
    __tablename__ = "shippings"

    title = Column("title", Text, nullable=False, unique=True, index=True)
    price = Column("price", DECIMAL(precision=12, scale=12), nullable=False)


engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)
logger.info("Tables has been created")

Session = sessionmaker(bind=engine)
session = Session()


r = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)
