
# from nosql_yorm.cache import cache_handler
from iterative.config import Config as IterativeConfig, set_config, get_config
from iterative import start_app, cache, IterativeModel

iterative_config = IterativeConfig(user_config_path="config.yaml")
set_config(iterative_config)

class User(IterativeModel):
    yolo: str

user = User(id="1", yolo="John")
user.save()

assert User.get_by_id("1").yolo == "John"
assert cache.get_document("Users", "1")["yolo"] == "John"

if __name__ == "__main__":
    start_app()
