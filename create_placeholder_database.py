import random

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, insert, select

from sqlalchemy.orm import Session

from models.base import DATABASE_URL, Base

import requests

from models.category import Category
from models.product import Product, ProductCategories, ProductTags
from models.tag import Tag
from utils import to_slug


def create_db(ses):

    # products
    for i in range(50):
        text = requests.get("https://loripsum.net/api/1/plaintext").text.replace(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "")
        split = text.split()
        name = " ".join(split[:2])
        weight = random.randint(1, 1000)
        slug = to_slug(f"{name} {weight}")
        img = "https://prd.place/400"
        price = (random.randint(1, 10) * 1000) + (999 * random.randint(0, 3))
        statement = insert(Product).values(product_name=name, short_description=" ".join(split[:10]),
                                           product_description=text,
                                           product_weight=weight, product_slug=slug, price=price, image_path=img,
                                           quantity=random.randint(1, 100))

        print(f"Added {name} product")

        session.execute(statement)
        session.commit()

    # category
    for i in range(5):
        text = requests.get("https://loripsum.net/api/1/plaintext").text.replace(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "")
        split = text.split()
        name = " ".join(split[:2])
        slug = to_slug(f"{name} {random.randint(0, 1000)}")
        img = "https://prd.place/400"
        statement = insert(Category).values(parent_id=0, category_name=name, category_slug=slug,
                                            image_path=img, category_description=text)

        print(f"Added {name} category")

        session.execute(statement)
        session.commit()

    # subcategory
    query = select(Category).where(Category.visible)
    result = session.execute(query)

    list = []
    for key, category in enumerate(result.fetchall()):
        list.append(jsonable_encoder(category[0]))

    for category in list:
        n = random.randint(0, 3)
        for j in range(n):
            text = requests.get("https://loripsum.net/api/1/plaintext").text.replace(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "")
            split = text.split()
            name = " ".join(split[:2])
            slug = to_slug(f"{name} {random.randint(0, 1000)}")
            img = "https://prd.place/400"
            statement = insert(Category).values(parent_id=category["id"], category_name=name, category_slug=slug,
                                                image_path=img, category_description=text)

            print(f"Added {name} subcategory")

            session.execute(statement)
            session.commit()

    # tags
    for i in range(20):
        text = requests.get("https://loripsum.net/api/1/plaintext").text.replace(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "")
        split = text.split()
        name = " ".join(split[:2])
        slug = to_slug(f"{name} {random.randint(0, 1000)}")
        img = "https://prd.place/400"
        statement = insert(Tag).values(tag_name=name, tag_slug=slug, image_path=img)

        print(f"Added {name} tag")

        session.execute(statement)
        session.commit()

    # product category and product tags
    query = select(Product)
    result = session.execute(query)

    products = []
    for key, product in enumerate(result.fetchall()):
        products.append(jsonable_encoder(product[0]))

    query = select(Category)
    result = session.execute(query)

    categories = []
    for key, category in enumerate(result.fetchall()):
        categories.append(jsonable_encoder(category[0]))

    query = select(Tag)
    result = session.execute(query)

    tags = []
    for key, tag in enumerate(result.fetchall()):
        tags.append(jsonable_encoder(tag[0]))

    for product in products:
        random.shuffle(categories)
        n = random.randint(1, 3)
        while n != 0:
            statement = insert(ProductCategories).values(product_id=product["id"], category_id=categories[n]["id"])
            n -= 1
            print(f"Added category: {categories[n]['category_name']} to product: {product['product_name']}")

            session.execute(statement)
            session.commit()

        random.shuffle(tags)
        n = random.randint(1, 5)
        while n != 0:
            statement = insert(ProductTags).values(product_id=product["id"], tag_id=tags[n]["id"])
            n -= 1
            print(f"Added tag: {tags[n]['tag_name']} to product: {product['product_name']}")

            session.execute(statement)
            session.commit()


def clear_data(ses):
    metadata = Base.metadata
    for table in reversed(metadata.sorted_tables):
        ses.execute(table.delete())
    ses.commit()


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
    session = Session(engine)

    create_db(session)
