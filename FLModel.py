import sys

sys.path.append("../")
from BaseClasses.SDPModel import SDPModel
from collections import namedtuple
import pandas as pd
import random

class FrozenLakeModel(SDPModel):
    def __init__(
        self,
        t0: float = 0, # t0 (float, optional): Initial time. Defaults to 0.
        T: float = 30, # T (float, optional): Terminal time. Defaults to 30.
        seed: int = 42, # seed (int, optional): Seed for random number generation. Defaults to 42.
    ):  
        state_names = ["position"]
        decision_names = ["up", "down", "left", "right"]

        S0 = {"position": (0, 0)}

        super().__init__(state_names, decision_names, S0, t0, T, seed)

    def is_finished(self):
        """
        Check if the model run (episode) is finished.

        Returns:
            bool: True if the run is finished, False otherwise.
        """
        return super().is_finished() or self.state.position == (15, 15)
    
    def exog_info_fn(self, decision):
        """
        Generates exogenous information for the balloon model.

        Args:
            decision: The decision made.

        Returns:
            A dictionary containing whether the balloon popped or the score was claimed.
        """
        start_pos = self.state.position
        possible_positions = []
        for x in range(start_pos[0] - 1, start_pos[0] + 1):
            for y in range(start_pos[1] - 1, start_pos[1] + 1):
                if (15 >= x >= 0) and (15 >= y >= 0): possible_positions.append((x, y))
        
        print(possible_positions)
        if random.random() < 0.3:
            return {"position": possible_positions[random.randint(0, len(possible_positions) - 1)]}
        
    
    def transition_fn(self, decision, exog_info: dict):
        """
        Updates the state of the model based on the decision made and the exogenous info.

        Args:
            decision: The decision made.
            exog_info: The exogenous information provided (e.g., whether balloon popped).

        Returns:
            The new state after applying the transition.
        """
        clicks = self.state.times_clicked + decision.click
        money = self.state.money
        colour = self.state.current_colour
        history = self.state.history
        

        if exog_info["popped"]:  # Balloon popped
            new_row = pd.DataFrame({"Colour": [colour], "Clicks": [clicks], 'Popped': [True], "Claimed": [False]})
            history = pd.concat([self.state.history, new_row], ignore_index=True)
            colour = random.choice(["orange", "yellow", "blue"])  # New balloon
            clicks = 0  # Reset clicks
        
        if decision.claim:  # Player claimed money
            money += clicks * 5
            new_row = pd.DataFrame({"Colour": [colour], "Clicks": [clicks], 'Popped': [False], "Claimed": [True]})
            history = pd.concat([self.state.history, new_row], ignore_index=True)
            colour = random.choice(["orange", "yellow", "blue"])  # New balloon
            clicks = 0  # Reset clicks

        # Update the state
        self.state = {
            "current_colour": colour,
            "money": money,
            "times_clicked": clicks,
            "history": history
        }

        return self.state
    
    def objective_fn(self, decision, exog_info: dict):
        return self.state.money / 100 # /100 to turn pence into pounds
