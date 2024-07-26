from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import config
from routers.products.products import router as product_router
from routers.products.categories import router as category_router
from routers.products.tags import router as tag_router
from routers.products.heading import router as heading_router
from routers.products.cart_products import router as cart_product_router
from routers.products.order import router as order_router

from routers.auth.preregister import router as pre_register_router
from routers.auth.register import router as register_router
from routers.auth.login import router as login_router
from routers.auth.forgot_password import router as forgot_password_router
from routers.user.me import router as me_router


from routers.admin.image import router as image_router

if config.DEBUG == 'True':
    app = FastAPI(debug=True, reload=True)
else:
    app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https:/thaihana.kz",
    "https:/thaihana.kz/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pre_register_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(forgot_password_router)
app.include_router(me_router)

app.include_router(product_router)
app.include_router(category_router)
#app.include_router(tag_router)
app.include_router(heading_router)
app.include_router(cart_product_router)
app.include_router(order_router)

app.include_router(image_router)
