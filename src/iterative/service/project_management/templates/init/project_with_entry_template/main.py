
from iterative.config import Config as IterativeConfig, set_config
from iterative import start_app, IterativeModel

iterative_config = IterativeConfig(user_config_path="config.yaml")
set_config(iterative_config)

class User(IterativeModel):
    yolo: str

user = User(id="1", yolo="John")
user.save()

assert User.get_by_id("1").yolo == "John"

if __name__ == "__main__":
    start_app()
