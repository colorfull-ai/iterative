Iterative generates endpoints and models that need to be tested in their behavior with and without using the api endpoints.

we test the menus api with test below, notice how we create.  In this example we have a TEST mode set, which is using the reade_write_to_cache set in the iterative config

// config.py
```python
from iterative import get_config

iter_config = get_config()

LOG_LEVEL = os.getenv("LOG_LEVEL", iter_config.get("logging_level", "DEBUG"))
```
```python
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from colorfull.models.store_models import Store
from colorfull.server import app  # Import your actual FastAPI app
from colorfull.models.menu_v2_models import Menu
from colorfull.cache_system.cache import test_cache_handler  # Import your actual cache_handler
from colorfull.config import TEST_MODE

if not TEST_MODE:
    raise Exception("Test mode is not enabled, aborting tests")

client = TestClient(app)


class TestMenuAPI:
    def setup_method(self):
        # Create a dummy store object
        self.store = Store(
            id="store_125",
            org_id="org_125",
            name="Test Store 125",
            # Add other necessary fields for the Store model
        )
        self.store.save()

        # Create initial dummy menu objects
        self.menu1 = Menu(
            id="menu_1",
            store_id="store_125",
            name="Test Menu 1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Add other necessary fields
        )
        self.menu1.save()

        self.menu2 = Menu(
            id="menu_2",
            store_id="store_125",
            name="Test Menu 2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Add other necessary fields
        )
        self.menu2.save()

    def teardown_method(cls):
        # Clear the test cache after all tests are done
        test_cache_handler.clear_all_data()

    def test_create_menu(self):
        new_menu_data = {"store_id": self.store.id, "name": "New Menu"}
        response = client.post("/menus", json=new_menu_data)
        assert response.status_code == 200
        assert response.json()["name"] == new_menu_data["name"]
        # Verify cache update
        created_menu = Menu.get_by_id(response.json()["id"])
        assert created_menu is not None
        assert created_menu.name == new_menu_data["name"]

    def test_get_menu_by_id(self):
        response = client.get(f"/menus/{self.menu1.id}")
        assert response.status_code == 200
        menu_data = response.json()
        assert menu_data["id"] == self.menu1.id
        assert menu_data["name"] == self.menu1.name

    def test_get_all_menus_by_store(self):
        response = client.get(f"/menus?store_id={self.store.id}")
        assert response.status_code == 200
        menus = response.json()
        assert len(menus) == 2

    def test_update_menu(self):
        updated_data = {"name": "Updated Menu Name"}
        response = client.put(f"/menus/{self.menu1.id}", json=updated_data)
        assert response.status_code == 200
        updated_menu = Menu.get_by_id(self.menu1.id)
        assert updated_menu.name == updated_data["name"]

    def test_delete_menu(self):
        response = client.delete(f"/menus/{self.menu2.id}")
        assert response.status_code == 200
        deleted_menu = Menu.get_by_id(self.menu2.id)
        assert deleted_menu is None

        not_deleted_menu = Menu.get_by_id(self.menu1.id)
        assert not_deleted_menu != None


if __name__ == "__main__":
    pytest.main()
```
