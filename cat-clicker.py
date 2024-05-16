from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static


class CountDisplay(Static):
    count = reactive(0)
    rate = reactive(0)
    multiplier = reactive(1)

    def on_mount(self) -> None:
        self.set_interval(1, self.update_count)

    def update_count(self) -> None:
        self.count += self.rate

    def watch_count(self, count: int) -> None:
        screen = f"""
        Count:          {self.count}
        Passive rate:   {self.rate}
        Multiplier:     {self.multiplier}
        """
        self.update(screen)

    def add(self, amount: int) -> None:
        multiplied = amount * self.multiplier
        self.count += multiplied

    def add_rate(self, amount: int, cost: int) -> Optional[int]:
        if self.count >= cost:
            self.rate += amount
            self.count -= cost
            return cost + 5
        return cost

    def add_multiplier(self, amount: int, cost: int) -> Optional[int]:
        if self.count >= cost:
            self.multiplier += amount
            self.count -= cost
            return self.multiplier, cost + 50
        return self.multiplier, cost


class Controls(Static):
    multiplier = 1
    passive_cost = 5
    multiplier_cost = 50

    def set_label(self, button: Button, value) -> None:
        match button.id:
            case "add":
                button.label = f"Add (x{value})"
            case "passive":
                button.label = f"Add Passive (Cost: {value})"
            case "multiplier":
                button.label = f"Add Multiplier (Cost: {value})"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        count_display = self.query_one(CountDisplay)
        match button_id:
            case "add":
                count_display.add(self.multiplier)
                self.set_label(event.button, self.multiplier)
            case "passive":
                self.passive_cost = count_display.add_rate(1, self.passive_cost)
                self.set_label(event.button, self.passive_cost)
            case "multiplier":
                self.multiplier, self.multiplier_cost = count_display.add_multiplier(1, self.multiplier_cost)
                self.set_label(event.button, self.multiplier_cost)
                self.set_label(self.query_one("#add"), self.multiplier)

    def compose(self) -> ComposeResult:
        yield CountDisplay()
        yield Button(f"Add (x{self.multiplier})", id="add", variant="success")
        yield Button(f"Add Passive (Cost: {self.passive_cost})", id="passive")
        yield Button(f"Add Multiplier (Cost: {self.multiplier_cost})", id="multiplier")


class CatClickerApp(App):
    # BINDINGS = [("d", "click", "Add")]
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header("Cat Clicker")
        yield Footer()
        yield Container(Controls())


if __name__ == "__main__":
    app = CatClickerApp()
    app.run()
