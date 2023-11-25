---

# Iterative CLI Tool README 🚀

## Welcome to Iterative! 🌟

Iterative is a dynamic CLI and web application tool designed to kickstart your project development with ease and efficiency. It's perfect for crafting small, AI-driven services and comes packed with features for quick and customizable app creation.

## Key Features of Iterative 🛠️

- **Easy Initialization**: Set up your project structure in a snap.
- **Dynamic Script Discovery**: Automatically turns Python scripts into CLI commands or web endpoints.
- **Flexible Configuration**: Customize your app with a `config.yaml`.
- **Ready for AI**: Ideal for AI agents to automate tasks like model creation and endpoint generation.

## Getting Started 🏁

### Installation

To install Iterative, simply run:

```bash
pip install iterative
```

### Initialize Your Project

Create your new project with:

```bash
iterative init
```

This command creates a project structure similar to:

```
iter_bad_story
├── config.yaml
├── main.py
└── scripts
    └── your_starting_functions.py
```

### Configuring Your Application

Edit the `config.yaml` to tailor the application to your needs.

## Using the CLI 🎮

### Basic Commands

- **Help**: To view available commands, use:
  
  ```bash
  python main.py --help
  ```

- **Start Utility Server**: To start the web server, use:

  ```bash
  python main.py start-util-server --port <your_port>
  ```

### Advanced Script Commands

For more advanced functionalities:

```bash
python main.py scripts --help
```

This reveals commands for managing `nosql_yorm` models and FastAPI endpoints, such as `add_property_to_model`, `create_model`, and more.

## First Run of Your App 🌈

When you first run `main.py`, you get access to initial commands like `init-command` and `start-util-server`. As you develop your app and add scripts to the `/scripts` directory, `iterative` dynamically discovers these scripts and integrates them into the CLI, enriching your command options.

## The Magic of Iterative ✨

- **Model Management**: Easily add, edit, or remove properties from your models.
- **Endpoint Generation**: Automatically generate CRUD endpoints for FastAPI.
- **Extensibility**: Add your own scripts to extend the functionality further.

## Why Iterative? 🤔

Iterative is more than just a CLI tool; it's a comprehensive solution for rapidly building and deploying small services, especially those driven by AI. With its intuitive setup and powerful features, Iterative streamlines your development process, making it faster and more efficient.

---

Dive into the world of `Iterative` and experience a smoother, more AI-friendly way of developing applications. Happy coding! 🚀👩‍💻👨‍💻

---

## Models

#### Defining Models

Within `iterative`, models are defined by extending `IterativeModel` from `nosql_yorm`, providing a direct link to Firebase collections.

```python
from nosql_yorm.models import BaseFirebaseModel

class User(IterativeModel):
   name: str
    # Define user-related fields here
```

#### Performing CRUD Operations

Users of `iterative` can directly use the models to perform database operations:

```python
user = User(name="Alice", email="alice@example.com")
user.save()  # Create a new user

fetched_user = User.get_by_id(user.id)  # Read the user data

fetched_user.name = "Alice Smith"
fetched_user.save()  # Update user details

fetched_user.delete()  # Delete the user
```