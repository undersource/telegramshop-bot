from pathlib import Path
from os import path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IMAGES_ROOT = path.join(BASE_DIR, "images")
FILES_ROOT = path.join(BASE_DIR, "files")
PRODUCT_IMAGES_DIR = path.join(IMAGES_ROOT, "product_images")
VIRTUAL_PRODUCTS_DIR = path.join(FILES_ROOT, "virtual_products")
