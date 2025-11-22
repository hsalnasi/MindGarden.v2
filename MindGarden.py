<<<<<<< HEAD
from datetime import datetime

# -----------------------------------------------------
# Parent Class: Task
# -----------------------------------------------------
class Task:
    def __init__(self, task_id, title):
        self.task_id = task_id
        self.title = title
        self.status = "new"              # "new", "in progress", "completed"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # y-m-d 00:00:00
        self.last_updated = self.created_at

    def update_status(self, new_status): # setter
        """Update status of the task. {in progress, done, new}"""
        self.status = new_status
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_summary(self):
        """Return simple summary of the task."""
        return f"[Task {self.task_id}] {self.title} - Status: {self.status}"

    def to_dict(self):
        """Convert task to dictionary (useful for saving to file)."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }


# -----------------------------------------------------
# Child Class: PlantTask (Inherits from Task)
# -----------------------------------------------------
class PlantTask(Task):
    PLANT_STATES = ["Seed", "Sprout", "Growing", "Blooming", "Wilting"]

    def __init__(self, task_id, title):
        super().__init__(task_id, title)    # call the parent constructor
        self.plant_state = "Seed"           # extra attribute for the plant

    def grow(self):
        """Move plant to the next growth stage."""
        current_index = PlantTask.PLANT_STATES.index(self.plant_state)

        # If not at the final stage, grow to next stage
        if current_index < len(PlantTask.PLANT_STATES) - 2:  # stop before Blooming/Wilting
            self.plant_state = PlantTask.PLANT_STATES[current_index + 1]
        else:
            self.plant_state = "Blooming"

        self.update_status("in progress")

    # -------- OVERRIDDEN METHOD --------
    def get_summary(self):
        """Override parent method to include plant info."""
        base_summary = super().get_summary()
        return f"{base_summary} | Plant state: {self.plant_state}"

    def mark_ignored(self):
        """Turn plant state to wilting if user stops working."""
        self.plant_state = "Wilting"
        self.update_status("ignored")

class DifficultyTask(PlantTask):
    def __init__(self, task_id, title, difficulty):
        super().__init__(task_id, title)
        self.difficulty = difficulty
        self.growth_speed = {"Easy": 2, "Medium": 1, "Hard": 0.5}
        self.completion_reward_message = ""

    def grow_based_on_difficulty(self):
        self.speed_counter = 0 # -> for Hard . only jumps when the counter reaches 2 attempts
        speed = self.growth_speed[self.difficulty] # only takes the speed number

        if speed == 2: # if it is Easy -> > ?
            super().grow()
            super().grow()
        elif speed == 1: # if it is medium , then grow only once
            super().grow()
        else:
            self.speed_counter += 1
            if self.speed_counter >= 2:
                super().grow()
                self.speed_counter = 0

        self.update_status("in progress")
    






=======
from datetime import datetime

# -----------------------------------------------------
# Parent Class: Task
# -----------------------------------------------------
class Task:
    def __init__(self, task_id, title):
        self.task_id = task_id
        self.title = title
        self.status = "new"              # "new", "in progress", "completed"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # y-m-d 00:00:00
        self.last_updated = self.created_at

    def update_status(self, new_status): # setter
        """Update status of the task. {in progress, done, new}"""
        self.status = new_status
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_summary(self):
        """Return simple summary of the task."""
        return f"[Task {self.task_id}] {self.title} - Status: {self.status}"

    def to_dict(self):
        """Convert task to dictionary (useful for saving to file)."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }


# -----------------------------------------------------
# Child Class: PlantTask (Inherits from Task)
# -----------------------------------------------------
class PlantTask(Task):
    PLANT_STATES = ["Seed", "Sprout", "Growing", "Blooming", "Wilting"]

    def __init__(self, task_id, title):
        super().__init__(task_id, title)    # call the parent constructor
        self.plant_state = "Seed"           # extra attribute for the plant

    def grow(self):
        """Move plant to the next growth stage."""
        current_index = PlantTask.PLANT_STATES.index(self.plant_state)

        # If not at the final stage, grow to next stage
        if current_index < len(PlantTask.PLANT_STATES) - 2:  # stop before Blooming/Wilting
            self.plant_state = PlantTask.PLANT_STATES[current_index + 1]
        else:
            self.plant_state = "Blooming"

        self.update_status("in progress")

    # -------- OVERRIDDEN METHOD --------
    def get_summary(self):
        """Override parent method to include plant info."""
        base_summary = super().get_summary()
        return f"{base_summary} | Plant state: {self.plant_state}"

    def mark_ignored(self):
        """Turn plant state to wilting if user stops working."""
        self.plant_state = "Wilting"
        self.update_status("ignored")

class DifficultyTask(PlantTask):
    def __init__(self, task_id, title, difficulty, mood):
        super().__init__(task_id, title)
        self.difficulty = difficulty
        self.mood = mood
        self.growth_speed = {"Easy": 2, "Medium": 1, "Hard": 0.5}
        self.completion_reward_message = ""
        self.speed_hard = 0

    def grow_based_on_difficulty(self):
        self.speed_counter = 0 # -> for Hard . only jumps when the counter reaches 2 attempts
        speed = self.growth_speed[self.difficulty] # only takes the speed number

        if speed == 2: # if it is Easy -> > ?
            super().grow()
            super().grow()
        elif speed == 1: # if it is medium , then grow only once
            super().grow()
        else:
            self.speed_hard += 1
            if self.speed_counter >= 2:
                super().grow()


        self.update_status("in progress")

    def mark_completed(self):
        self.status = "completed"
        self.plant_state = "Blooming"
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.difficulty == "Easy":
            self.completion_reward_message =  "Great job! 🌱 You finished an easy task!"
        elif self.difficulty == "Medium":
            self.completion_reward_message =  "Nice work! 🌿 You completed a medium task!"
        else:
            self.completion_reward_message =  "Amazing! 🌳 You finished a hard task!"
        return self.completion_reward_message

    def to_csv_row(self):
        return {
        "task_id": self.task_id,
        "title": self.title,
        "difficulty": self.difficulty,
        "status": self.status,
        "plant_state": self.plant_state,
        "mood": self.mood,
        "created_at": self.created_at,
        "last_updated": self.last_updated
        }


task  = DifficultyTask("1", "Finish Math", "Hard", "Focus")
print(task.get_summary())
print(task.grow_based_on_difficulty())
print(task.mark_completed())
print(task.get_summary())










>>>>>>> fe039c7 (first commit)
