from datetime import datetime
import csv

# -----------------------------------------------------
# Custom Exception
# -----------------------------------------------------
class TaskNotFoundError(Exception):
    """Exception raised when a task is not found."""
    pass

# -----------------------------------------------------
# Parent Class: Task
# -----------------------------------------------------
class Task:
    def __init__(self, task_id, title):
        self.task_id = task_id
        self.title = title
        self.status = "new"              # new, in progress, or done ... / Haifa
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # y-m-d 00:00:00
        self.last_updated = self.created_at # initialize the same as created_at at the start /Haifa

    def update_status(self, new_status): # setter
        """Update status of the task. {in progress, done, new}"""
        self.status = new_status
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # here time gets updated

    def get_summary(self):
        """Return simple summary of the task."""
        return f"[Task {self.task_id}] {self.title} - Status: {self.status}"

    def to_dict(self):
        """Convert task to dictionary (useful for saving to csv)/ Haifa"""
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
    # this is a class variable. in order to access it we use : class.varname (without self) /Haifa
    PLANT_STATES = ["Seed", "Sprout", "Growing", "Blooming", "Wilting"]

    def __init__(self, task_id, title):
        super().__init__(task_id, title)    # call the parent constructor
        self.plant_state = "Seed"           # initial status of the plant

    def grow(self):
        """Move plant to the next growth stage."""
        current_index = PlantTask.PLANT_STATES.index(self.plant_state)

        # If not at the final stage, grow to next stage
        # we're double checking if the status is between seed-growing only
        if current_index < len(PlantTask.PLANT_STATES) - 2:  # stop before Blooming/Wilting
            self.plant_state = PlantTask.PLANT_STATES[current_index + 1] # increase index by 1 -> growing by 1 and assign it as the new status ::) /Haifa
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
        self.plant_state = "Wilting" # updating the plant state
        self.update_status("ignored") # updating the task status

class DifficultyTask(PlantTask):
    def __init__(self, task_id, title, difficulty, mood="Happy"):
        super().__init__(task_id, title)
        self.difficulty = difficulty # ---> Easy, Medium, Hard .
        self.mood = mood # defalut is "Happy" :> /Haifa
        self.growth_speed = {"Easy": 2, "Medium": 1, "Hard": 0.5}
        self.completion_reward_message = ""
        self._growth_progress = 0

    # Getter . Will be used in GUI as a loading bar or we will see ... :*)/Haifa
    def get_growth_progress(self):
        needed = self.growth_speed[self.difficulty]
        return self._growth_progress, needed

    def grow_based_on_difficulty(self):
        self._growth_progress += 1
        speed = self.growth_speed[self.difficulty] # only takes the speed number needed for the plant to grow .

        if self._growth_progress >= speed:
            super().grow()
            self._growth_progress = 0 

        # Update status to in progress
        self.update_status("in progress")

    def mark_completed(self):
        self.status = "completed" # task status 
        self.plant_state = "Blooming" # plant status
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.difficulty == "Easy":
            self.completion_reward_message =  "Great job! 🌱 You finished an easy task!"
        elif self.difficulty == "Medium":
            self.completion_reward_message =  "Nice work! 🌿 You completed a medium task!"
        else:
            self.completion_reward_message =  "Amazing! 🌳 You finished a hard task!"
        return self.completion_reward_message

    # Ovverriden method . it still functions the same but with more columns /Haifa
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

# TESTUUUU 
task  = DifficultyTask("1", "Finish Math", "Hard", "Focus")
print(task.get_summary())
print(task.grow_based_on_difficulty())
print(task.mark_completed())
print(task.get_summary())

# -----------------------------------------------------
# Task Manager Class
# a task has a title, difficulty, mood, status, plant state, created at, last updated and ofc and ID 
# 
# -----------------------------------------------------
class TaskManager:
    def __init__(self, max_id = 0):
        self.__tasks = []
        self.__next_task_id = max_id + 1
    #getters
    def get_next_task_id(self):
        return self.__next_task_id #return next task id

    def get_all_tasks(self):
        return self.__tasks #return all tasks
    # ----------------------------------------
    def create_task(self,title,difficulty, mood = "Happy"):
        #check for valid title
        if not title or not isinstance(title, str): # it shouldn't be empty and non string!
            raise ValueError("Invalid title")
        #check for valid difficulty
        if difficulty not in ["Easy", "Medium", "Hard"]:
            raise ValueError("Invalid difficulty")
        
        #creating a new DifficultyTask
        """ WE ARE APPENDING THE ENTIRE OBJECT HERE TO THE LIST 
        . SO WHEN WE WANT TO ACCESS IT LATER FROM THE LIST, WE WILL NEED TO USE [OBJECT.TASK]
         (OBJECT) here could be any name / Haifa """
        task = DifficultyTask(self.__next_task_id, title, difficulty,mood)  # creating a task
        self.__tasks.append(task)  # adding a task to the list
        self.__next_task_id += 1  # updating next task's id
        print(f"Task {title} created successfully with ID {task.task_id}.")
        return task #return the created task

    def get_task_by_id(self, task_id):
        #find a task by id
        for t in self.__tasks:
            if t.task_id == task_id:
                return t

        raise TaskNotFoundError("Task not found.")

    def update_task_progress(self,task_id):
        #get task and update its plant state
        task = self.get_task_by_id(task_id)
        task.grow_based_on_difficulty()
        print(f"Task ID {task_id} updated: plant state = {task.plant_state}")
        return task

    def complete_task(self, task_id):
        #mark as completed and return a reward for the user
        task = self.get_task_by_id(task_id)
        reward = task.mark_completed()
        print(reward)
        return reward

  

# TESTU TESTU 
print("=== Creating TaskManager ===")
tm = TaskManager()

print("\n=== Creating Tasks ===")
t1 = tm.create_task("Study Python", "Easy")
t2 = tm.create_task("Finish Project", "Hard", mood="Tired")

print("\n=== Showing all tasks ===")
for task in tm.get_all_tasks():
    print(task.task_id, task.title, task.difficulty, task.plant_state)

print("\n=== Updating Progress ===")
tm.update_task_progress(1)
tm.update_task_progress(2)

print("\n=== Completing a Task ===")
tm.complete_task(1)










