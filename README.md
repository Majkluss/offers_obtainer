## Offers Obtainer
This is a **Flask** web application for obtaining offers of given products.

User can add a new product to the system using the REST API. The product will be saved
in the database and application will call the **offers microservice** API, which provides
a list of offers to this product, which also will be saved in the database.

The application is started using the Docker with the `docker-compose up` 
command. You have to set the environment variables in the **.env** file, see the
**.env.example** file for reference of file structure.

For working with the **offers microservice** you'll need an *access_token*, which is obtained 
using the *refresh_token* value. For working with API, you'll need a *api_token*.

The base url for the **offers microservice**, the *refresh_token* and the *api_token* are
provided to application via the **.env** file.


## Database structure

The application uses a **MySQL** database for storing data. 
Credentials for the database are provided to application via the **.env** file.
Hostname of the database is specified by the **docker-compose.yml** file, e.g. 
*mysql*.

The application uses two database models - *Products* and *Offers*.
Product has many offers, offer has one product.

The models have the following structure (None of the fields can be empty):
### Table 1 - Products
```
id - varchar/string (36) PRIMARY KEY // UUID of the product 
name - varchar/string (155)
description - varchar/string (255)
```

### Table 2 - Offers
```
id - varchar/string (36) PRIMARY KEY // UUID of the offer
price - integer
items_in_stock - integer
product_id - varchar/string (36) FOREIGN KEY to Products.id
```

## REST API structure

***

### CREATE - Add a new product

You can add a new product to the system using the `POST` request on the 
`/api/products` endpoint with a JSON structure in a body of the request.

An example of the JSON structure:

```
{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66af22",
    "name": "Spice_Harvester",
    "description": "Spice harvester can harvest the Spice, known as a Melange."
}
```

Calling this endpoint will update the database table *Products* and also updates its
offers in the *Offers* table.

***

### READ - Get info about one specific or all existing products

You can obtain a list of all existing products using the `GET` request on the 
`/api/products` endpoint or get info about one specific product using the `GET` request on the
`/api/products/<product_id>` endpoint.

For obtaining a list of offers for one product you can use the `GET` request on the
`/api/offers/<product_id>` endpoint.

You can also get a list of all existing offers using the `GET` request on the
`/api/offers` endpoint.

***

### UPDATE - Update an existing product 

You can update an existing product in the database using the `PATCH` request 
on the `/api/products` endpoint with a JSON structure in a body
of the request. You can change both the `name` or the `description` of the product.
The **id** of the product can't be changed and is required in the JSON structure.

An example of the JSON structure:
```
{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66af22",
    "name": "Sand_Worm",
    "description": "Sand worm creates the Spice known as a Melange."
}
```

***

### DELETE - Delete an existing product

You can delete an existing product from the database using the `DELETE` request
on the `/api/products` endpoint with an **id** of the product in the JSON structure
in the body of the request.

An example of the JSON structure:
```
{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66af22"
}
```

***

### Unit tests
Application contains unit tests for the `app.py` module. The tests have 
own `docker-compose-test.yml` file and `Dockerfile.test` file. You can run them
by using the Docker command `docker-compose -f docker-compose-test.yml up`.
