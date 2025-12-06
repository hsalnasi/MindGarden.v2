import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from MindGarden_main import TaskManager, DifficultyTask


# If you defined TaskNotFoundError / other custom exceptions
# in logic.py, you can import them too, e.g.:
try:
    from MindGarden_main import TaskNotFoundError
except ImportError:
    TaskNotFoundError = Exception  # fallback


# ---------------------------------------------------------
# CSV helpers (do NOT modify your original TaskManager)
# ---------------------------------------------------------

def save_tasks_to_csv(task_manager: TaskManager, filename="plant_tasks.csv"):
    """
    Save tasks as proper CSV rows with a header.
    Uses DifficultyTask.to_csv_row() from your original code.
    """
    tasks = task_manager.get_all_tasks()
    if not tasks:
        # Still create an empty CSV with header
        fieldnames = [
            "task_id", "title", "difficulty", "status",
            "plant_state", "mood", "created_at", "last_updated"
        ]
    else:
        # Use first row's keys to be safe
        fieldnames = list(tasks[0].to_csv_row().keys())

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in tasks:
                writer.writerow(t.to_csv_row())
    except OSError as e:
        raise e


def load_tasks_from_csv(task_manager: TaskManager, filename="plant_tasks.csv"):
    """
    Load tasks from proper CSV rows and put them into the existing TaskManager.

    Uses Option A:
    - Construct DifficultyTask(task_id, title, difficulty, mood)
    - Then set status, plant_state, created_at, last_updated
    """
    new_tasks = []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    task_id = int(row["task_id"])
                    title = row["title"]
                    difficulty = row["difficulty"]
                    mood = row.get("mood", "Happy")

                    t = DifficultyTask(task_id, title, difficulty, mood)

                    # Restore additional fields
                    t.status = row.get("status", "new")
                    t.plant_state = row.get("plant_state", "Seed")
                    t.created_at = row.get("created_at", t.created_at)
                    t.last_updated = row.get("last_updated", t.last_updated)

                    new_tasks.append(t)
                except (KeyError, ValueError):
                    # Skip corrupted rows
                    continue
    except FileNotFoundError:
        new_tasks = []

    # 👇 put the tasks into the existing TaskManager
    # (using name-mangled private attributes WITHOUT changing the original class)
    task_manager._TaskManager__tasks = new_tasks
    if new_tasks:
        task_manager._TaskManager__next_task_id = max(t.task_id for t in new_tasks) + 1
    else:
        task_manager._TaskManager__next_task_id = 1

    return len(new_tasks)


def append_stats_row(task, mood_text, reflection_text, stats_file="task_stats.csv"):
    """
    Append one row to a stats CSV whenever reflection is saved.
    """
    fieldnames = [
        "task_id", "title", "difficulty", "status",
        "plant_state", "mood", "reflection", "completed_at"
    ]
    row = {
        "task_id": task.task_id,
        "title": task.title,
        "difficulty": task.difficulty,
        "status": task.status,
        "plant_state": task.plant_state,
        "mood": mood_text,
        "reflection": reflection_text,
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    file_exists = False
    try:
        with open(stats_file, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(stats_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------
# Garden Canvas (Member 2 - drawing plants)
# ---------------------------------------------------------

class GardenCanvas(tk.Canvas):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.bind("<Button-1>", self.on_click)

    def redraw(self, tasks):
        self.delete("all")
        if not tasks:
            self.create_text(
                200, 150,
                text="No plants yet.\nAdd a task to grow your garden 🌱",
                justify="center",
                font=("Arial", 12)
            )
            return

        cols = 4
        cell_w, cell_h = 140, 150
        margin_x, margin_y = 80, 60

        for index, task in enumerate(tasks):
            col = index % cols
            row = index // cols
            x = margin_x + col * cell_w
            y = margin_y + row * cell_h
            self.draw_plant(task, x, y)

    def draw_plant(self, task, x, y):
        # Color based on difficulty
        if task.difficulty == "Easy":
            stem_color = "#66bb6a"
        elif task.difficulty == "Medium":
            stem_color = "#388e3c"
        else:  # Hard
            stem_color = "#1b5e20"

        # Soil
        self.create_oval(
            x - 20, y + 25, x + 20, y + 35,
            fill="#8d6e63",
            outline="",
            tags=("plant", f"task_{task.task_id}")
        )

        # Stem
        self.create_rectangle(
            x - 3, y - 10, x + 3, y + 25,
            fill=stem_color,
            outline=stem_color,
            tags=("plant", f"task_{task.task_id}")
        )

        state = getattr(task, "plant_state", "Seed")

        if state == "Seed":
            self.create_oval(
                x - 4, y + 15, x + 4, y + 23,
                fill="#4e342e",
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )

        if state in ["Sprout", "Growing", "Blooming"]:
            # Leaves
            self.create_oval(
                x - 15, y + 5, x - 3, y + 13,
                fill=stem_color,
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )
            self.create_oval(
                x + 3, y + 5, x + 15, y + 13,
                fill=stem_color,
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )

        if state == "Growing":
        # Bigger stem
            self.create_rectangle(
                x - 4, y - 35, x + 4, y - 10,
                fill=stem_color,
                outline=stem_color,
                tags=("plant", f"task_{task.task_id}")
            )

    # More leaves (4 instead of 2)
            self.create_oval(x - 20, y - 5, x - 5, y + 10, fill=stem_color, outline="", tags=("plant", f"task_{task.task_id}"))
            self.create_oval(x + 5, y - 5, x + 20, y + 10, fill=stem_color, outline="", tags=("plant", f"task_{task.task_id}"))

            self.create_oval(x - 15, y - 20, x - 3, y - 8, fill=stem_color, outline="", tags=("plant", f"task_{task.task_id}"))
            self.create_oval(x + 3, y - 20, x + 15, y - 8, fill=stem_color, outline="", tags=("plant", f"task_{task.task_id}"))

        # Tiny flower bud to hint it's close to blooming
            self.create_oval(
                x - 5, y - 45, x + 5, y - 35,
                fill="#e1bee7",
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )


        if state == "Blooming":
            petal_color = "#ffb74d"
            self.create_oval(
                x - 10, y - 40, x + 10, y - 20,
                fill=petal_color,
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )
            self.create_oval(
                x - 6, y - 36, x + 6, y - 24,
                fill="#fdd835",
                outline="",
                tags=("plant", f"task_{task.task_id}")
            )

        if state == "Wilting":
            self.create_line(
                x, y - 10, x - 12, y + 10,
                fill=stem_color, width=3,
                tags=("plant", f"task_{task.task_id}")
            )

        # Title under plant
        self.create_text(
            x, y + 48,
            text=f"{task.title} (ID {task.task_id})",
            font=("Arial", 8),
            tags=("plant", f"task_{task.task_id}")
        )

    def on_click(self, event):
        item = self.find_closest(event.x, event.y)
        if not item:
            return
        tags = self.gettags(item)
        task_id = None
        for tag in tags:
            if tag.startswith("task_"):
                try:
                    task_id = int(tag.split("_")[1])
                    break
                except ValueError:
                    pass
        if task_id is not None:
            self.app.on_plant_clicked(task_id)


# ---------------------------------------------------------
# Stats Panel (Member 3 - bottom panel)
# ---------------------------------------------------------

class StatsPanel(tk.Frame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app

        self.total_label = tk.Label(self, text="Total: 0")
        self.completed_label = tk.Label(self, text="Completed: 0")
        self.easy_label = tk.Label(self, text="Easy: 0")
        self.medium_label = tk.Label(self, text="Medium: 0")
        self.hard_label = tk.Label(self, text="Hard: 0")

        self.total_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.completed_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.easy_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.medium_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.hard_label.grid(row=0, column=4, padx=5, pady=2, sticky="w")

        self.save_btn = tk.Button(self, text="Save Tasks", command=self.app.on_save_tasks)
        self.load_btn = tk.Button(self, text="Load Tasks", command=self.app.on_load_tasks)
        self.save_btn.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.load_btn.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def update_stats(self, tasks):
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "completed")
        easy = sum(1 for t in tasks if t.difficulty == "Easy")
        medium = sum(1 for t in tasks if t.difficulty == "Medium")
        hard = sum(1 for t in tasks if t.difficulty == "Hard")

        self.total_label.config(text=f"Total: {total}")
        self.completed_label.config(text=f"Completed: {completed}")
        self.easy_label.config(text=f"Easy: {easy}")
        self.medium_label.config(text=f"Medium: {medium}")
        self.hard_label.config(text=f"Hard: {hard}")


# ---------------------------------------------------------
# Main App (ties Member 1, 2, 3 together)
# ---------------------------------------------------------

class MindGardenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MindGarden – Productivity Plant")

        # Task manager from your original code
        self.task_manager = TaskManager()

        # Layout frames
        self.left_frame = tk.Frame(root, padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky="nsw")

        self.canvas_frame = tk.Frame(root, padx=10, pady=10)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")

        self.bottom_frame = tk.Frame(root, padx=10, pady=5)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        # ---------- Member 1: Left Input Panel ----------
        tk.Label(self.left_frame, text="Add / Edit Task", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        tk.Label(self.left_frame, text="Title:").grid(row=1, column=0, sticky="w")
        self.title_entry = tk.Entry(self.left_frame, width=25)
        self.title_entry.grid(row=1, column=1, pady=2)

        tk.Label(self.left_frame, text="Difficulty:").grid(row=2, column=0, sticky="w")
        self.difficulty_var = tk.StringVar(value="Easy")
        self.difficulty_combo = ttk.Combobox(
            self.left_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=22
        )
        self.difficulty_combo.grid(row=2, column=1, pady=2)

        tk.Label(self.left_frame, text="Mood (optional):").grid(row=3, column=0, sticky="w")
        self.mood_entry = tk.Entry(self.left_frame, width=25)
        self.mood_entry.insert(0, "Happy")
        self.mood_entry.grid(row=3, column=1, pady=2)

        tk.Label(self.left_frame, text="Task ID for update/complete:").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )
        self.task_id_entry = tk.Entry(self.left_frame, width=10)
        self.task_id_entry.grid(row=5, column=0, pady=2, sticky="w")

        self.add_btn = tk.Button(self.left_frame, text="Add Task", command=self.on_add_task)
        self.add_btn.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")

        self.update_btn = tk.Button(self.left_frame, text="Update Progress", command=self.on_update_task)
        self.update_btn.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

        self.complete_btn = tk.Button(self.left_frame, text="Mark Completed", command=self.on_complete_task)
        self.complete_btn.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

        self.status_label = tk.Label(self.left_frame, text="Ready.", fg="gray")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(10, 0), sticky="w")

        # ---------- Member 2: Garden Canvas ----------
        self.canvas = GardenCanvas(self.canvas_frame, self, width=700, height=400, bg="#e8f5e9")
        self.canvas.pack(fill="both", expand=True)

        # ---------- Member 3: Stats Panel ----------
        self.stats_panel = StatsPanel(self.bottom_frame, self)
        self.stats_panel.pack(fill="x")

        self.refresh_view()

    # ---------- Utility ----------
    def refresh_view(self):
        tasks = self.task_manager.get_all_tasks()
        self.canvas.redraw(tasks)
        self.stats_panel.update_stats(tasks)

    def set_status(self, msg, error=False):
        self.status_label.config(text=msg, fg=("red" if error else "gray"))

    def _parse_task_id(self):
        text = self.task_id_entry.get().strip()
        if not text:
            raise ValueError("Please enter a Task ID.")
        return int(text)

    # ---------- Member 1: Button handlers ----------
    def on_add_task(self):
        title = self.title_entry.get()
        difficulty = self.difficulty_var.get()
        mood = self.mood_entry.get() or "Happy"
       


        try:
            # Your TaskManager.create_task(title, difficulty, mood)
            task = self.task_manager.create_task(title, difficulty, mood)
            self.set_status(f"Seed planted 🌱 — Task {task.task_id} created.")
            self.title_entry.delete(0, tk.END)
            self.refresh_view()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.set_status(str(e), error=True)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.set_status("Unexpected error while adding task.", error=True)
        self.task_id_entry.delete(0, tk.END)
        self.task_id_entry.insert(0, str(task.task_id))


    def on_update_task(self):
        try:
            task_id = self._parse_task_id()
            task = self.task_manager.update_task_progress(task_id)
            self.set_status(f"Task {task_id} grew to {task.plant_state} 🌿")
            self.refresh_view()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.set_status(str(e), error=True)
        except Exception as e:
            if "not found" in str(e).lower():

                messagebox.showerror("Task Not Found", str(e))
                self.set_status(str(e), error=True)
            else:
                raise

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.set_status("Unexpected error while updating task.", error=True)

    def on_complete_task(self):
        try:
            task_id = self._parse_task_id()
            task = self.task_manager.get_task_by_id(task_id)
            reward = task.mark_completed()
            messagebox.showinfo("Task Completed", reward)
            self.set_status(f"Task {task_id} completed. 🌸")
            self.refresh_view()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.set_status(str(e), error=True)
        except TaskNotFoundError as e:
            messagebox.showerror("Task Not Found", str(e))
            self.set_status(str(e), error=True)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.set_status("Unexpected error while completing task.", error=True)

    # ---------- Member 3: Save / Load ----------
    def on_save_tasks(self):
        try:
            save_tasks_to_csv(self.task_manager, "plant_tasks.csv")
            messagebox.showinfo("Save", "Tasks saved to plant_tasks.csv")
            self.set_status("Tasks saved.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")
            self.set_status("Error saving tasks.", error=True)

    def on_load_tasks(self):
        try:
            count = load_tasks_from_csv(self.task_manager, "plant_tasks.csv")
            self.refresh_view()
            messagebox.showinfo("Load", f"{count} tasks loaded from plant_tasks.csv")
            self.set_status("Tasks loaded.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load tasks:\n{e}")
            self.set_status("Error loading tasks.", error=True)

    # ---------- Member 3: Plant click → reflection popup ----------
    def on_plant_clicked(self, task_id):
        try:
            task = self.task_manager.get_task_by_id(task_id)
            self.task_id_entry.delete(0, tk.END)
            self.task_id_entry.insert(0, str(task_id))
            self.set_status(f"Selected Task {task_id}: {task.title}")
            self.open_reflection_popup(task)
        except TaskNotFoundError as e:
            messagebox.showerror("Task Not Found", str(e))
            self.set_status(str(e), error=True)

    def open_reflection_popup(self, task):
        popup = tk.Toplevel(self.root)
        popup.title(f"Reflection – Task {task.task_id}")

        tk.Label(popup, text=f"Title: {task.title}").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(popup, text=f"Difficulty: {task.difficulty}").grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(popup, text=f"Status: {task.status}").grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(popup, text=f"Plant state: {task.plant_state}").grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        tk.Label(popup, text="Mood:").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
        mood_entry = tk.Entry(popup, width=30)
        mood_entry.insert(0, getattr(task, "mood", ""))
        mood_entry.grid(row=4, column=1, padx=10, pady=(10, 0))

        tk.Label(popup, text="Reflection:").grid(row=5, column=0, sticky="nw", padx=10, pady=(10, 0))
        reflection_box = tk.Text(popup, width=35, height=5)
        reflection_box.grid(row=5, column=1, padx=10, pady=(10, 0))

        def on_save_reflection():
            mood_text = mood_entry.get().strip() or getattr(task, "mood", "Happy")
            reflection_text = reflection_box.get("1.0", tk.END).strip()
            try:
                # Update mood on the task
                task.mood = mood_text
                # If not completed, we can leave it or mark complete here.
                # To keep your logic unchanged, we won't auto-complete here.
                append_stats_row(task, mood_text, reflection_text)
                self.refresh_view()
                self.set_status("Reflection saved to task_stats.csv")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save reflection:\n{e}")

        save_btn = tk.Button(popup, text="Save Reflection", command=on_save_reflection)
        save_btn.grid(row=6, column=0, padx=10, pady=10, sticky="e")

        cancel_btn = tk.Button(popup, text="Cancel", command=popup.destroy)
        cancel_btn.grid(row=6, column=1, padx=10, pady=10, sticky="w")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = MindGardenApp(root)
    root.mainloop()
