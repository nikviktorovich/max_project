# Overview
Small market API project. Includes auth system, products data and user cart. Endpoints use root address as base. Made as a showcase of my current abilities in this particular field and not intended for real world use scenario.


# Technology stack
- FastAPI
- SQLAlchemy


# Requirements
- Python 3.8


# Setup and deployment
First, we need to install Python 3.8. More instructions in the link below:
`https://wiki.python.org/moin/BeginnersGuide/Download`


The second step is creating and activating a virtual environment:
- CMD
    ```cmd
    python -m venv .venv
    .venv/Scripts/activate
    ```


- PowerShell
    ```powershell
    python -m venv .venv
    & .venv/Scripts/activate
    ```

- Bash
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```


The next step is installing requirements:
```
python -m pip install -r requirements.txt
```


Finally, you can start the server (default address is `http://127.0.0.1:8000/`):
```
python -m uvicorn src.main:app
```


# API
## Database architecture
### Auth system
#### Users
Table `users` contains user information.

List of fields:
- `id` - User unique id
- `username` - User name
- `full_name` - User full name (optional, might be blank)
- `password` - User password hash


#### Permissions
Table `permissions` contains permissions information, which might be assigned to groups or individual users.

List of fields:
- `id` - Permission unique id
- `name` - Human-readable permission name
- `codename` - Permission codename


#### Groups
Table `groups` contains information about assignable user groups.

List of fields:
- `id` - Group unique id
- `name` - Human-readable group name

Also, there are helper tables `user_groups`, `user_permissions` and `group_permissions` which contain relations between users & groups, users & permissions and groups & permissions respectively.


### Media
#### Images
Table `images` contains image file name (with extension).

List of fields:
- `id` - Image id
- `image` - Image file name


### Products information
#### Products
Table `products` contains product information.

List of fields:
- `id` - Product id
- `title` - Product title
- `description` - Product description (optional, might be blank)
- `stock` - Amount of product in stock
- `price_rub` - Product price in RUB
- `is_active` - Is product listing active (optional, default is True)
- `added` - Datetime when the product was added. Filled automatically
- `last_updated` - Last product information update datetime. Filled automatically
- `owner_id` - Owner's user id


#### Product images
Table `productimages` contains relations between products and assigned images.

List of fields:
- `id` - Record id
- `product_id` - Product id
- `image_id` - Id of image, assigned to the product


### Cart
#### Cart items
Table `cartitems` contains information about products in user's cart.

List of fields:
- `id` - Cart item id
- `amount` - Amount of product in cart
- `product_id` - Product id
- `user_id` - User id


## Endpoints
### Overview
All the endpoints, except media and auth (more in the corresponding sections), accept parameters in `json` format. In case of failure, each endpoint provides a detailed response as a json-object with entry key `detail`. For more information on each endpoint you can use `/docs`, which provides an auto-generated Swagger interactive documentation.


### Auth system
#### _`/token`_
Description:

This endpoint is responsible for user authorization.

Methods:
- `POST`

#### _`/signup`_
Description:

This endpoint allows you to register a user.

Methods:
- `POST`


### User information
#### _`/user`_
Description:

This endpoint allows you to get and change user information.

Methods:
- `GET`
- `PATCH`
- `PUT`


### Products
#### _`/products`_
Description:

This endpoint allows you to get a list of all products or to add one.

Methods:
- `GET`
- `POST`


#### _`/products/{product_id}`_
Description:

This endpoint allows you to get a specific product information or manipulate it (edit or delete).

Methods:
- `GET`
- `PATCH`
- `PUT`
- `DELETE`


### Media
#### _`/images`_
Description:

This endpoint allows you to upload an image.

Methods:
- `POST`


#### _`/images/{image_id}`_
Description:

This endpoint allows you to get an uploaded image by its id.

Methods:
- `GET`


### Cart
#### _`/cart`_
Description:

This endpoing allows you to get cart items or add a new one.

Methods:
- `GET`
- `POST`


#### _`/cart/{product_id}`_
Description:

This endpoint allows you to get an information about a particular cart item. Notice that product id is used.

Methods:
- `GET`
- `PUT`
- `DELETE`
