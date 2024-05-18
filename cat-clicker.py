import json
from typing import Tuple

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static, Log


def multiplier_map() -> dict:
    return {
        1: "Fish",
        2: "Mouse",
        3: "Rat",
        4: "Squirrel",
        5: "Sparrow",
        6: "Pigeon",
        7: "Chicken",
        8: "Turkey",
        9: "Peacock"
    }


def format_multiplier(multiplier) -> str:
    label = multiplier_map().get(multiplier)
    if not label:
        raise ValueError(f"No mapping for multiplier {multiplier}")
    return label


class NumDisplay(Static):
    food = reactive(0)
    food_rate = reactive(0)
    multiplier = reactive(1)
    old_multiplier_cost = 100

    def on_mount(self) -> None:
        self.timer = self.set_interval(1, self.update_food)

    def update_food(self) -> None:
        if self.food_rate > 0:
            self.food += 1

    def watch_food(self, food: int) -> None:
        screen = f"""
        Food:           {self.food}
        Cats employed:  {self.food_rate}
        """
        self.update(screen)

    def reset_timer(self) -> None:
        self.timer.stop()
        self.timer = self.set_interval(1 / self.food_rate, self.update_food)

    def add(self, amount: int) -> None:
        multiplied = amount * self.multiplier
        self.food += multiplied

    def add_food_rate(self, amount: int, cost: int) -> int:
        if self.food >= cost:
            self.food_rate += amount
            self.food -= cost
            self.reset_timer()
            return cost + 5
        return cost

    def add_multiplier(self, amount: int, cost: int) -> Tuple[int, int]:
        if self.food >= cost:
            self.multiplier += amount
            self.food -= cost
            return self.multiplier, cost + self.old_multiplier_cost
        return self.multiplier, cost


class Controls(Static):
    multiplier = 1
    hire_cat_cost = 5
    multiplier_cost = 100

    def set_label(self, button: Button) -> None:
        match button.id:
            case "add":
                button.label = f"Catch {format_multiplier(self.multiplier)} (x{self.multiplier})"
            case "hire-cat":
                button.label = f"Hire Street Cat (Cost: {self.hire_cat_cost})"
            case "multiplier":
                button.label = f"Upgrade Catch (Cost: {self.multiplier_cost})"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        num_display = self.query_one(NumDisplay)
        match button_id:
            case "add":
                num_display.add(self.multiplier)
                self.set_label(event.button)
            case "hire-cat":
                self.hire_cat_cost = num_display.add_food_rate(1, self.hire_cat_cost)
                self.set_label(event.button)
            case "multiplier":
                self.multiplier, self.multiplier_cost = num_display.add_multiplier(1, self.multiplier_cost)
                self.set_label(event.button)
                self.set_label(self.query_one("#add"))

    def compose(self) -> ComposeResult:
        add_button = Button(id="add", variant="success")
        self.set_label(add_button)

        hire_cat_button = Button(id="hire-cat")
        self.set_label(hire_cat_button)

        multiplier_button = Button(id="multiplier")
        self.set_label(multiplier_button)

        yield NumDisplay()
        yield add_button
        yield hire_cat_button
        yield multiplier_button


class CatClickerApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save Game"),
        ("l", "load", "Load Game"),
    ]
    CSS_PATH = "style.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = Controls(id="controls")
        self.logger = Log(id="logger")
        self.logger.max_lines = 1

    def action_save(self):
        self.logger.clear()
        num_display = self.controls.query_one(NumDisplay)
        save_dict = {
            "food": num_display.food,
            "food_rate": num_display.food_rate,
            "hire_cat_cost": self.controls.hire_cat_cost,
            "multiplier": self.controls.multiplier,
            "multiplier_cost": self.controls.multiplier_cost,
            "old_multiplier_cost": num_display.old_multiplier_cost,
        }
        with open("cat-save.json", "w+") as f:
            json.dump(save_dict, f)

        self.logger.write_line("Game saved!")

    def action_load(self):
        self.logger.clear()
        with open("cat-save.json") as f:
            save_dict = json.load(f)
        if not save_dict:
            self.logger.write_line("Save file is empty!")
            return

        num_display = self.controls.query_one(NumDisplay)
        num_display.food = save_dict["food"]
        num_display.food_rate = save_dict["food_rate"]
        self.controls.hire_cat_cost = save_dict["hire_cat_cost"]
        self.controls.multiplier = save_dict["multiplier"]
        self.controls.multiplier_cost = save_dict["multiplier_cost"]
        num_display.old_multiplier_cost = save_dict["old_multiplier_cost"]
        self.logger.write_line("Save loaded!")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield self.logger
        yield Container(self.controls)

    def on_mount(self) -> None:
        self.title = "Cat Clicker"
        self.sub_title = "Click your way to space!"


if __name__ == "__main__":
    app = CatClickerApp()
    app.run()
