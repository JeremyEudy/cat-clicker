#!/usr/bin/env python3
import json

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static, Log

from animation import frames
from subtitles import random_subtitle


catch_map = {
    1: "fish",
    2: "mouse",
    3: "rat",
    4: "squirrel",
    5: "sparrow",
    6: "pigeon",
    7: "chicken",
    8: "turkey",
    9: "peacock"
}

upgrade_map = {
    1: "mouse slingshot",
    2: "lizard on a bottle rocket",
    3: "rat parachute",
    4: "cat-apult",
    5: "fishbowl space helmet",
    6: "flying cat suit",
    7: "cat condo radio station",
    8: "catnik 1 launch (uncatted)",
    9: "bastet rocket launch",
}


def format_button_label(button_id, num) -> str:
    match button_id:
        case "catch":
            return f"Catch {catch_map[num].title()} ({num} food)"
        case "hire-cat":
            return f"Hire Cat ({num} food)"
        case "upgrade-catch":
            if num != 900:
                return f"Upgrade Catch ({num} food)"
            else:
                return "Fully Upgraded"
        case "catnip":
            return f"Buy Catnip ({num} food)"
        case "racoon":
            return f"Hire Racoon ({num} food)"
        case "science":
            return f"Do Science ({num} catnip)"
        case "upgrade":
            return f"Run Space Experiment ({num} science)"


class NumDisplay(VerticalScroll):
    BORDER_TITLE = "Stats"

    @staticmethod
    def render_screen(food: int = 0,
                      cats: int = 0,
                      catnip: int = 0,
                      catnip_rate: int = 0,
                      science: int = 0,
                      upgrade: int = 0) -> str:

        return f"""
Food:             {food}
Cats Employed:    {cats}
Catnip:           {catnip}
Racoons Employed: {catnip_rate}
Science:          {science}
Level:            {upgrade}
"""

    def on_mount(self) -> None:
        self.static = self.query_one(Static)
        self.static.update(self.render_screen())

    def update_screen(self, food, food_rate, catnip, catnip_rate, science, upgrade) -> None:
        self.static.update(self.render_screen(food, food_rate, catnip, catnip_rate, science, upgrade))


class Sprite(Static):
    clicked = reactive(False)
    frame_rate = 15
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
        self.send_message("You wake up and feel hungry, go catch some food!")

    def send_message(self, message) -> None:
        self.logger.write_line(message)


class Controls(VerticalScroll):
    BORDER_TITLE = "Actions"

    def compose(self) -> ComposeResult:
        catch_button = Button(id="catch", variant="success")
        hire_cat_button = Button(id="hire-cat", disabled=True, variant="warning")
        upgrade_catch_button = Button(id="upgrade-catch", disabled=True, variant="primary")

        catnip_button = Button(id="catnip", classes="hidden", disabled=True)
        racoon_button = Button(id="racoon", classes="hidden", disabled=True, variant="primary")
        science_button = Button(id="science", classes="hidden", disabled=True, variant="error")
        upgrade_button = Button(id="upgrade", classes="hidden", disabled=True, variant="success")

        catch_button.label = format_button_label("catch", 1)
        hire_cat_button.label = format_button_label("hire-cat", 5)
        upgrade_catch_button.label = format_button_label("upgrade-catch", 100)
        catnip_button.label = format_button_label("catnip", 10)
        racoon_button.label = format_button_label("racoon", 50)
        science_button.label = format_button_label("science", 5)
        upgrade_button.label = format_button_label("upgrade", 10)

        yield catch_button
        yield hire_cat_button
        yield upgrade_catch_button
        yield catnip_button
        yield racoon_button
        yield science_button
        yield upgrade_button


class Engine(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save Game"),
        ("l", "load", "Load Game"),
        ("d", "debug", "Load Debug Save"),
    ]
    CSS_PATH = "style.tcss"

    # Stats
    food = reactive(0)

    catch = reactive(1)
    catch_cost = 100

    food_rate = reactive(0)
    hire_cat_cost = 5

    catnip = reactive(0)
    catnip_cost = 10

    catnip_rate = reactive(0)
    racoon_cost = 50

    science = reactive(0)
    science_cost = 5

    upgrade = reactive(1)
    upgrade_cost = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_display = NumDisplay(Static())
        self.sprite = Sprite()
        self.controls = Controls()
        self.logger = LogDisplay(Log())

    def on_mount(self) -> None:
        self.title = "Cat Clicker"
        self.sub_title = random_subtitle()
        self.food_timer = self.set_interval(1, self.update_food)
        self.catnip_timer = self.set_interval(1, self.update_catnip)
        self.save_timer = self.set_interval(300, self.action_save)

    def action_save(self):
        save_dict = {
            "food": self.food,
            "food_rate": self.food_rate,
            "hire_cat_cost": self.hire_cat_cost,
            "catch": self.catch,
            "catch_cost": self.catch_cost,
            "catnip": self.catnip,
            "catnip_cost": self.catnip_cost,
            "catnip_rate": self.catnip_rate,
            "racoon_cost": self.racoon_cost,
            "science": self.science,
            "science_cost": self.science_cost,
            "upgrade": self.upgrade,
            "upgrade_cost": self.upgrade_cost,
        }
        with open("cat-save.json", "w+") as f:
            json.dump(save_dict, f)

        self.logger.send_message("Game saved!")

    def action_load(self):
        try:
            with open("cat-save.json") as f:
                save_dict = json.load(f)
            if not save_dict:
                self.logger.send_message("Save file is empty!")
                return
        except Exception:
            self.logger.send_message("Save file does not exist!")
            return
        self.food = save_dict["food"]
        self.food_rate = save_dict["food_rate"]
        self.hire_cat_cost = save_dict["hire_cat_cost"]
        self.catch = save_dict["catch"]
        self.catch_cost = save_dict["catch_cost"]
        self.catnip = save_dict["catnip"]
        self.catnip_cost = save_dict["catnip_cost"]
        self.catnip_rate = save_dict["catnip_rate"]
        self.racoon_cost = save_dict["racoon_cost"]
        self.science = save_dict["science"]
        self.science_cost = save_dict["science"]
        self.upgrade = save_dict["upgrade"]
        self.upgrade_cost = save_dict["upgrade_cost"]

        self.update_screen("load-file")

    def action_debug(self):
        try:
            with open("debug-cat-save.json") as f:
                save_dict = json.load(f)
            if not save_dict:
                self.logger.send_message("Debug save file is empty!")
                return
        except Exception:
            self.logger.send_message("Debug save file does not exist!")
            return
        self.food = save_dict["food"]
        self.food_rate = save_dict["food_rate"]
        self.hire_cat_cost = save_dict["hire_cat_cost"]
        self.catch = save_dict["catch"]
        self.catch_cost = save_dict["catch_cost"]
        self.catnip = save_dict["catnip"]
        self.catnip_cost = save_dict["catnip_cost"]
        self.catnip_rate = save_dict["catnip_rate"]
        self.racoon_cost = save_dict["racoon_cost"]
        self.science = save_dict["science"]
        self.science_cost = save_dict["science"]
        self.upgrade = save_dict["upgrade"]
        self.upgrade_cost = save_dict["upgrade_cost"]

        self.update_screen("load-debug")

    def update_screen(self, action: str = None) -> None:
        self.num_display.update_screen(self.food, self.food_rate, self.catnip, self.catnip_rate, self.science, self.upgrade)

        catch_button = self.query_one("#catch")
        catch_button.label = format_button_label("catch", self.catch)

        upgrade_catch_button = self.query_one("#upgrade-catch")
        upgrade_catch_button.label = format_button_label("upgrade-catch", self.catch_cost)
        if "Fully" in upgrade_catch_button.label:
            upgrade_catch_button.disabled = True

        hire_button = self.query_one("#hire-cat")
        hire_button.label = format_button_label("hire-cat", self.hire_cat_cost)

        catnip_button = self.query_one("#catnip")
        catnip_button.label = format_button_label("catnip", self.catnip_cost)

        racoon_button = self.query_one("#racoon")
        racoon_button.label = format_button_label("racoon", self.racoon_cost)

        science_button = self.query_one("#science")
        science_button.label = format_button_label("science", self.science_cost)

        upgrade_button = self.query_one("#upgrade")
        upgrade_button.label = format_button_label("upgrade", self.upgrade_cost)
        match action:
            case "catch":
                self.logger.send_message(f"You catch an unsuspecting {catch_map[self.catch]}.")
            case "hire-cat":
                self.logger.send_message("You pass some food (and an employment contract) to a street cat, and they nod.")
            case "upgrade-catch":
                self.logger.send_message(f"You spend a few minutes licking yourself and have an epiphany. You can now catch {catch_map[self.catch]}!")
            case "failed_upgrade_catch_max":
                self.logger.send_message("You realize that you're happy with your current catch, and you take comfort in your contentment.")
            case "catnip":
                self.logger.send_message(f"You hand over {self.catnip_cost} food to a shady looking racoon. He hands back 1 catnip.")
            case "racoon":
                self.logger.send_message(f"You decide to hire on a catnip growing racoon for {self.racoon_cost}")
            case "science":
                self.logger.send_message("You pay some catnip to an indoor cat to push some of their owner's glassware onto the floor. Gain 1 science!")
            case "upgrade":
                self.logger.send_message(f"Experiment Report: {upgrade_map[self.upgrade].title()} SUCCESS")
            case "failed_upgrade_max":
                self.logger.send_message("One small steppy for cat, one big steppy for catkind. You win!")
            case "load-file":
                self.logger.send_message("Save loaded!")
            case "load-debug":
                self.logger.send_message("Debug save loaded!")
            case _:
                return

    def update_food(self) -> None:
        if self.food_rate > 0:
            self.reset_food_timer()
            self.food += 1
        if self.food_rate >= 10 and self.food >= self.catnip_cost:
            catnip_button = self.query_one("#catnip")
            catnip_button.disabled = False
            catnip_button.remove_class("hidden")
        if self.catnip >= self.science_cost:
            science_button = self.query_one("#science")
            science_button.disabled = False
            science_button.remove_class("hidden")
        if self.science >= self.upgrade_cost:
            upgrade_button = self.query_one("#upgrade")
            upgrade_button.disabled = False
            upgrade_button.remove_class("hidden")

            if self.food >= self.racoon_cost:
                racoon_button = self.query_one("#racoon")
                racoon_button.disabled = False
                racoon_button.remove_class("hidden")

    def watch_food(self, food: int) -> None:
        hire_cat_button = self.query_one("#hire-cat")
        upgrade_catch_button = self.query_one("#upgrade-catch")
        catnip_button = self.query_one("#catnip")
        racoon_button = self.query_one("#racoon")
        hire_cat_button.disabled = False if food > self.hire_cat_cost else True
        upgrade_catch_button.disabled = False if food > self.catch_cost else True
        catnip_button.disabled = False if food > self.catnip_cost else True
        racoon_button.disabled = False if food > self.racoon_cost else True
        self.update_screen()

    def update_catnip(self) -> None:
        if self.catnip_rate > 0:
            self.reset_catnip_timer()
            self.catnip += 1

    def watch_catnip(self, catnip: int) -> None:
        science_button = self.query_one("#science")
        science_button.disabled = False if catnip > self.science_cost else True
        self.update_screen()

    def watch_science(self, science: int) -> None:
        upgrade_button = self.query_one("#upgrade")
        upgrade_button.disabled = False if science > self.upgrade_cost else True
        self.update_screen()

    def reset_food_timer(self) -> None:
        self.food_timer.stop()
        self.food_timer = self.set_interval(1 / self.food_rate, self.update_food)

    def reset_catnip_timer(self) -> None:
        self.catnip_timer.stop()
        self.catnip_timer = self.set_interval(1 / self.catnip_rate, self.update_catnip)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "catch":
                self.food += self.catch
                self.update_screen(button_id)
                self.sprite.clicked = True
            case "hire-cat":
                self.food_rate += 1
                self.food -= self.hire_cat_cost
                self.hire_cat_cost += 5
                self.reset_food_timer()
                self.update_screen(button_id)
            case "upgrade-catch":
                if (self.catch + 1) not in catch_map.keys():
                    self.update_screen("failed_upgrade_catch_max")
                    return
                self.food -= self.catch_cost
                self.catch_cost += 100
                self.catch += 1
                self.update_screen(button_id)
            case "catnip":
                self.catnip += 1
                self.food -= self.catnip_cost
                self.catnip_cost += 1
                self.update_screen(button_id)
            case "racoon":
                self.catnip_rate += 1
                self.food -= self.racoon_cost
                self.racoon_cost += 10
                self.reset_catnip_timer()
                self.update_screen(button_id)
            case "science":
                self.science += 1
                self.catnip -= self.science_cost
                self.science_cost += 2
                self.update_screen(button_id)
            case "upgrade":
                if (self.upgrade + 1) not in upgrade_map.keys():
                    self.update_screen("failed_upgrade_max")
                    return
                self.upgrade += 1
                self.science -= self.upgrade_cost
                self.upgrade_cost += 5
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
