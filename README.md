# README for `nosql_yorm` Package

## Overview

`nosql_yorm` is a Python package designed to facilitate interaction with Firebase databases and provide a seamless testing experience by integrating a caching mechanism. This package is particularly useful for applications that require database operations like creating, updating, merging, and deleting records, both in development and testing environments.

## Key Features

- **Firebase ORM**: Leverages Firebase as the backend database, providing a robust and scalable solution for data storage and retrieval.
- **Integrated Caching**: Includes a caching layer for testing, preventing unnecessary database pollution and speeding up test execution.
- **Seamless Testing**: Allows for efficient and accurate testing by mimicking database interactions, ensuring consistency between test and production environments.
- **TypeScript Client Methods**: Supports TypeScript client methods for various operations, enhancing the development experience for applications using TypeScript.

## Installation

To install `nosql_yorm`, run the following command:

```bash
pip install nosql_yorm
```

## Usage

### Defining Models

Models in `nosql_yorm` inherit from `BaseFirebaseModel`, allowing them to interact directly with Firebase. Here's an example of a model definition:

```python
from nosql_yorm.models import BaseFirebaseModel

class Store(BaseFirebaseModel):
    collection_name = "stores"
    # Define your fields here
```

### CRUD Operations

The package supports various CRUD operations directly from the models:

#### Create and Save

```python
store = Store(name="New Store", org_id="123")
store.save()
```

#### Read

```python
store = Store.get_by_id("store_id")
```

#### Update

```python
store.name = "Updated Store Name"
store.save()
```

#### Delete

```python
store.delete()
```

### Testing with Caching

In test mode, `nosql_yorm` uses a temporary cache instead of the actual database, allowing for faster test execution and data isolation:

```python
from nosql_yorm.config import set_library_config

# Enable test mode
set_library_config(read_write_to_cache=True)

# Perform your tests here
```

### Integration with Endpoints

`nosql_yorm` can be seamlessly integrated with web frameworks like FastAPI to create endpoints. For example:

```python
from fastapi import FastAPI, HTTPException
from models import Store

app = FastAPI()

@app.put("/stores/{store_id}")
async def update_store(store_id: str, store_data: Store):
    store = Store.get_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.merge(store_data.dict())
    store.save()
    return store
```

## Another Example

```py
from nosql_yorm.models import BaseFirebaseModel
from nosql_yorm.config import set_library_config

set_library_config(read_write_to_cache=True)


class NewModel(BaseFirebaseModel):
    example_field: str

print(NewModel.get_all())

for NewMd in NewModel.get_all():
    NewMd.delete()

new_model = NewModel(example_field="test_data")
new_model.save()
print(new_model)
assert new_model.example_field == "test_data"
new_model.save()
assert new_model.id is not None
prev_model = NewModel.get_by_id(new_model.id)
print(prev_model)

assert new_model == NewModel.get_by_id(new_model.id)
```


## Contributing

Contributions to `nosql_yorm` are welcome! Please read our contributing guidelines to get started.

## License

`nosql_yorm` is released under [MIT License](LICENSE).

---

This README provides a basic overview of the `nosql_yorm` package. You can expand it with more detailed documentation, examples, and guidelines as needed for your package users.