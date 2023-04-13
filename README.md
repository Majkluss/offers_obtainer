## Offers Obtainer
This is a **Flask** web application for obtaining offers of given products.

User can add a new product to the system using the REST API. The product will be saved
in the database and application will call the **offers microservice** API, which provides
a list of offers to this product, which also will be saved in the database.

The application is started using the Docker with the `docker-compose up` 
command.

For working with the **offers microservice** you'll need an *access_token*, which is obtained 
using the *refresh_token* value. The *access_token* is obtained via `check_token`
decorator in the code. For working with API, you'll need a *api_token*.

Both base url for the **offers microservice** and the *refresh_token* value have to be 
inserted into the **.env** file

The base url for the **offers microservice**, the *refresh_token* and the *api_token* are
located in the **.env** file.


## Database structure

The application uses a **MySQL** database for storing data. 
Credentials for the database are located in the **.env** file.

The application uses two tables - *Products* and *Offers*.
Product has many offers, offer has one product.

The tables have the following structure (none of the columns can have NULL value):
### Table 1 - Products
```
id - varchar(36) PRIMARY KEY // UUID of the product 
name - varchar(155)
description - varchar(255)
```

### Table 2 - Offers
```
id - varchar(36) PRIMARY KEY // UUID of the offer
price - integer
items_in_stock - integer
product_id - varchar(36) FOREIGN KEY to Products.id
```

## REST API structure

***

### CREATE - Add a new product

You can add a new product to the system using the `POST` request on the 
`/api/products` endpoint with a JSON structure in a body of the request.

An example of the JSON structure:

`{
	"id": "3fa85f64-5717-4562-b3fc-2c963f66af22",
	"name": "Spice_Harvester",
	"description": "Spice harvester can harvest the Spice, known as a Melange."
}`

Calling this endpoint will update the database table *Products* and also updates its
offers in the *Offers* table.

You can also update the offers for the product using the `PUT` request on the 
`/api/offers/<product_id>` endpoint.

***

### READ - Get info about one specific or all existing products

You can obtain a list of all existing products using the `GET` request on the 
`/api/products` endpoint (implicitly limited to 100).

For obtaining a list of offers for the product you can use the `GET` request on the
`/api/offers/<product_id>` endpoint.

You can also get a list of all existing offers using the `GET` request on the
`/api/offers` endpoint (limited to 100).

***

### UPDATE - Update an existing product 

You can update an existing product in the database using the `PATCH` request 
on the `/api/products/<product_id>` endpoint with a JSON structure in a body
of the request. You can change both the `name` or the `description` of the product.

An example of the JSON structure:
`{
	"name": "Sand_Worm",
	"description": "Sand worm creates the Spice known as a Melange."
}`

***

### DELETE - Delete an existing product

You can delete an existing product from the database using the `DELETE` request
on the `/api/products/<product_id>` endpoint.

***

### API Responses
One of the API responses can be 409 CONFLICT, in case of any problem has occured.
You can find the details in the body of the response.

***

### Unit tests
A `test_app.py` module contains a unit tests. You can run them by using the 
`pytest test_app.py` command. You will need a running MySQL database, which can be 
started with the command 
`docker run --name mysql -u root -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql`.