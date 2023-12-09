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


we create unit tests and test directly against the cache at times as well


```python
from datetime import datetime
import json
from pathlib import Path

from colorfull.models.store_models import StoreState
from colorfull.models.menu_v2_models import Category, Menu, ModifierGroup, Photo
from colorfull.models.hours_models import StoreHours, StoreHoursConfiguration
from colorfull.models.store_models import Store
from colorfull.models.menu_v2_models import CurrencyAmount, Item, SaleStatus
from colorfull.integration_system.integrator import event_registrar
from iterative import cache as test_cache_handler

from colorfull.config import TEST_MODE

if not TEST_MODE:
    raise Exception("Test mode is not enabled, aborting tests")


class TestMenuEventHandler:
    def setup_method(self, method):
        self.store1 = Store(
            id="store_123",
            otter_id="9bf1297a-49b1-4a4a-ae19-2b0e09ca8cd1",
            org_id="org_123",
            name="Test Store 1",
            store_state=StoreState.OPEN.value,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            hours=StoreHoursConfiguration(
                delivery_hours=StoreHours(regular_hours=[], special_hours=[]),
                pickup_hours=StoreHours(regular_hours=[], special_hours=[]),
                timezone="America/New_York",
            ),
        )
        self.store1.save()

    def teardown_method(self, method):
        # This is run after each test method execution.
        # Clear the cache here
        test_cache_handler.clear_all_data(exclude_access_tokens=True)

    def test_menu_publish_handler(self):
        # Determine the path to the JSON file
        data_path = Path(__file__).parent / "testdata/menu_publish.json"

        # Load the payload from the JSON file
        with open(data_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        # Instantiate the MenuEventHandler class
        # Assuming the 'get_handler' method exists in event_registrar and returns a callable event handler.
        event_registrar.get_handler("OTTER", "menus.menu_publish")(payload)

        self.do_publish_menu_assertions()

    def test_menu_publish_handler_idempotency(self):
        call_number = 0
        # Determine the path to the JSON file
        data_path = Path(__file__).parent / "testdata/menu_publish.json"

        # Load the payload from the JSON file
        with open(data_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        event_registrar.get_handler("OTTER", "menus.menu_publish")(payload)

        # Call the handler and assert for the first time
        self.do_publish_menu_assertions()

        event_registrar.get_handler("OTTER", "menus.menu_publish")(payload)
        self.do_publish_menu_assertions()

    def test_update_menu_entities_availabilities_handler(self):
        # Determine the path to the JSON file
        data_path = (
            Path(__file__).parent / "testdata/update_menu_entities_availabilities.json"
        )

        # Load the payload from the JSON file
        with open(data_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        item = Item(
            id="1",
            otter_id="1",
            menu_id="1",
            name="Bagel",
            description="",
            price=CurrencyAmount(amount=100, currency_code="USD"),
            category_id="1",
            modifier_group_ids=["5"],
            sale_status=SaleStatus.FOR_SALE.value,
            suspended_until=datetime.now(),
        )

        item.save()
        # Instantiate the MenuEventHandler class
        # Assuming the 'get_handler' method exists in event_registrar and returns a callable event handler.
        handler = event_registrar.get_handler(
            "OTTER", "menus.update_menu_entities_availabilities"
        )
        # perform the event handling
        handler(payload)

        item_object = Item.get_by_id("1")
        assert item_object.sale_status == SaleStatus.TEMPORARILY_NOT_FOR_SALE.value

    # Function to call the event handler and perform assertions
    def do_publish_menu_assertions(self):
        # Call the MenuEventHandler
        # DB Collction assertions
        assert len(Menu.get_all()) == 1
        assert len(Category.get_all()) == 1
        assert len(Item.get_all()) == 2
        assert len(ModifierGroup.get_all()) == 1
        assert len(Photo.get_all()) == 1
        assert len(Menu.get_page(1, 1, {"otter_id": "1"})) == 1

        # === Store Assertions ===
        store_with_otter = Store.get_page(
            1, 10, {"otter_id": "9bf1297a-49b1-4a4a-ae19-2b0e09ca8cd1"}
        )
        assert len(store_with_otter) == 1
        assert store_with_otter[0].menu_ids == ["1"]
        assert store_with_otter[0].otter_id == "9bf1297a-49b1-4a4a-ae19-2b0e09ca8cd1"
        assert store_with_otter[0].id == "store_123"

        # === Menu Assertions ===
        first_menu = Menu.get_page(1, 10, {"otter_id": "1"})
        assert len(first_menu) == 1
        assert first_menu[0].otter_id == "1"
        assert first_menu[0].store_id == "store_123"
        assert first_menu[0].name == "Tasty BBQ"
        assert first_menu[0].category_ids == ["2"]
        # Check if hours are not empty
        assert first_menu[0].hours is not None

        # Assuming hours is a list of TimeInterval objects
        # Check the second interval in the hours list
        second_interval = first_menu[0].hours[1]

        assert second_interval.day == "TUESDAY"
        assert second_interval.from_hour == 11
        assert second_interval.from_minute == 0
        assert second_interval.to_hour == 20
        assert second_interval.to_minute == 30

        # === Category Assertions ===
        first_category = Category.get_page(1, 10, {"otter_id": "2"})
        assert len(first_category) == 1
        assert first_category[0].otter_id == "2"
        assert first_category[0].menu_id == "1"
        assert first_category[0].name == "Breakfast"
        assert first_category[0].item_ids == ["3"]

        # === Item Assertions ===
        first_item = Item.get_page(1, 10, {"otter_id": "3"})
        assert len(first_item) == 1
        assert first_item[0].description == "Delicious bagel!"
        assert first_item[0].modifier_group_ids == ["5"]
        assert first_item[0].photo_ids == ["6"]
        assert first_item[0].price.currency_code == "USD"
        assert first_item[0].price.amount == 25
        assert first_item[0].sale_status == "TEMPORARILY_NOT_FOR_SALE"
        assert (
            first_item[0].suspended_until.strftime("%Y-%m-%dT%H:%M:%SZ")
            == "2019-08-24T14:15:22Z"
        )

        # Assertions for the second item in the 'items' JSON structure
        second_item = Item.get_page(1, 10, {"otter_id": "4"})
        assert len(second_item) == 1
        assert second_item[0].id == "4"
        assert second_item[0].otter_id == "4"
        assert second_item[0].menu_id == "1"
        assert second_item[0].name == "Plain"
        assert second_item[0].description == "Plain bagel!"
        assert second_item[0].modifier_group_ids == []
        assert second_item[0].photo_ids == []
        assert second_item[0].price.currency_code == "USD"
        assert second_item[0].price.amount == 0
        assert second_item[0].sale_status == "TEMPORARILY_NOT_FOR_SALE"
        assert (
            second_item[0].suspended_until.strftime("%Y-%m-%dT%H:%M:%SZ")
            == "2019-08-24T14:15:22Z"
        )

        # === ModifierGroup Assertions ===
        first_modifier_group = ModifierGroup.get_page(1, 10, {"otter_id": "5"})
        assert len(first_modifier_group) == 1
        assert first_modifier_group[0].otter_id == "5"
        assert first_modifier_group[0].id == "5"
        assert first_modifier_group[0].name == "Choose your type of bagel"
        assert first_modifier_group[0].item_ids == ["4"]
        assert first_modifier_group[0].minimum_selections == 0
        assert first_modifier_group[0].maximum_selections == 0
        assert first_modifier_group[0].max_per_modifier_selection_quantity == 0

        # === Photo Assertions ===
        first_photo = Photo.get_page(1, 10, {"otter_id": "6"})
        assert len(first_photo) == 1
        assert first_photo[0].otter_id == "6"
        assert first_photo[0].id == "6"
        assert first_photo[0].file_name == "this image.jpg"
        assert (
            first_photo[0].url
            == "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        )

```