#!/usr/bin/env python3
import json

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static, Log

from animation import frames


catch_map = {
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


class NumDisplay(VerticalScroll):
    BORDER_TITLE = "Stats"

    def on_mount(self) -> None:
        self.static = self.query_one(Static)
        self.static.update("""
Food:           0
Cats Employed:  0
                           """)

    def update_screen(self, food, food_rate) -> None:
        self.static.update(f"""
Food:           {food}
Cats Employed:  {food_rate}
                           """)


class Sprite(Static):
    clicked = reactive(False)
    frame_rate = 5
    frame_position = reactive(0)

    def on_mount(self) -> None:
        self.timer = self.set_interval(1 / self.frame_rate, self.run_animation, pause=True)
        self.update(frames[self.frame_position])

    def run_animation(self) -> None:
        self.frame_position += 1
        try:
            self.update(frames[self.frame_position])
        except IndexError:
            self.frame_position = 0
            self.update(frames[self.frame_position])

    def watch_clicked(self) -> None:
        if not self.clicked:
            return
        self.clicked = False
        self.timer.resume()

    def watch_frame_position(self) -> None:
        if self.frame_position == 0:
            self.timer.pause()


class LogDisplay(VerticalScroll):
    BORDER_TITLE = "Info"

    def on_mount(self) -> None:
        self.logger = self.query_one(Log)
        self.logger.auto_scroll = True
        self.send_message("You feel hungry, go catch some food!")

    def send_message(self, message) -> None:
        self.logger.write_line(message)


class Controls(VerticalScroll):
    BORDER_TITLE = "Actions"

    def compose(self) -> ComposeResult:
        catch_button = Button(f"Catch {catch_map[1]} (1 food)", id="catch", variant="success")
        hire_cat_button = Button("Hire Cat (5 food)", id="hire-cat", variant="warning")
        upgrade_catch_button = Button("Upgrade Catch (100 food)", id="upgrade-catch", variant="primary")

        yield catch_button
        yield hire_cat_button
        yield upgrade_catch_button


class Engine(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save Game"),
        ("l", "load", "Load Game"),
    ]
    CSS_PATH = "style.tcss"

    # Stats
    food = reactive(0)
    food_rate = reactive(0)
    catch = reactive(1)
    catch_cost = 100
    hire_cat_cost = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_display = NumDisplay(Static())
        self.sprite = Sprite()
        self.controls = Controls()
        self.logger = LogDisplay(Log())

    def on_mount(self) -> None:
        self.title = "Cat Clicker"
        self.sub_title = "Click your way to space!"
        self.timer = self.set_interval(1, self.update_food)

    def action_save(self):
        save_dict = {
            "food": self.food,
            "food_rate": self.food_rate,
            "hire_cat_cost": self.hire_cat_cost,
            "catch": self.catch,
            "catch_cost": self.catch_cost,
        }
        with open("cat-save.json", "w+") as f:
            json.dump(save_dict, f)

        self.logger.send_message("Game saved!")

    def action_load(self):
        with open("cat-save.json") as f:
            save_dict = json.load(f)
        if not save_dict:
            self.logger.send_message("Save file is empty!")
            return
        self.food = save_dict["food"]
        self.food_rate = save_dict["food_rate"]
        self.hire_cat_cost = save_dict["hire_cat_cost"]
        self.catch = save_dict["catch"]
        self.catch_cost = save_dict["catch_cost"]

        self.update_screen("load-file")

    def update_screen(self, action: str = None) -> None:
        self.num_display.update_screen(self.food, self.food_rate)
        catch_button = self.query_one("#catch")
        catch_button.label = f"Catch {catch_map[self.catch]} ({self.catch} food)"
        upgrade_button = self.query_one("#upgrade-catch")
        upgrade_button.label = f"Upgrade Catch ({self.catch_cost})"
        hire_button = self.query_one("#hire-cat")
        hire_button.label = f"Hire Cat ({self.hire_cat_cost})"
        match action:
            case "catch":
                self.logger.send_message(f"You catch an unsuspecting {catch_map[self.catch]}.")
            case "hire-cat":
                self.logger.send_message("You pass some food (and an employment contract) to a street cat, and they nod.")
            case "upgrade-catch":
                self.logger.send_message(f"You spend a few minutes licking yourself and have an epiphany. You can now catch {catch_map[self.catch]}!")
            case "failed_hire_cat":
                self.logger.send_message("The cat rolls their eyes at your lowball offer.")
            case "failed_upgrade_catch_cost":
                self.logger.send_message("You try and fail to catch a bigger prey.")
            case "failed_upgrade_catch_max":
                self.logger.send_message("You realize that you're happy with your current catch, and you take comfort in your contentment.")
            case "load-file":
                self.logger.send_message("Save loaded!")
            case _:
                return

    def update_food(self) -> None:
        if self.food_rate > 0:
            self.food += 1

    def watch_food(self, food: int) -> None:
        self.update_screen()

    def reset_timer(self) -> None:
        self.timer.stop()
        self.timer = self.set_interval(1 / self.food_rate, self.update_food)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "catch":
                self.food += self.catch
                self.update_screen(button_id)
                self.sprite.clicked = True
            case "hire-cat":
                if self.food < self.hire_cat_cost:
                    self.update_screen("failed_hire_cat")
                    return
                self.food_rate += 1
                self.food -= self.hire_cat_cost
                self.hire_cat_cost += 5
                self.reset_timer()
                self.update_screen(button_id)
            case "upgrade-catch":
                if self.food < self.catch_cost:
                    self.update_screen("failed_upgrade_catch_cost")
                    return
                elif (self.catch + 1) not in catch_map.keys():
                    self.update_screen("failed_upgrade_catch_max")
                    return
                self.food -= self.catch_cost
                self.catch_cost += 100
                self.catch += 1
                self.update_screen(button_id)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Vertical(
            Horizontal(
                self.num_display,
                Vertical(
                    self.sprite,
                    self.logger,
                    id="sprite-container",
                ),
                id="display-container",
            ),
            self.controls
        )


if __name__ == "__main__":
    app = Engine()
    app.run()
