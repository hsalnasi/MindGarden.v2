import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
import pygame
from MindGarden_main import TaskManager
from datetime import datetime
import csv

# ------------------------------
# App Configuration - sizes , fonts and all
# ------------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

EARTH = {
    "bg": "#F4EFE6",
    "panel": "#FBFAF7",
    "card": "#FBFAF7",
    "border": "#C8BFAE",
    "text": "#3E3A32"
}

MOODS = {
    "Happy":     {"accent": "#ebc734", "hover": "#E76F51"},
    "Calm":      {"accent": "#4665c3", "hover": "#6B9080"},
    "Focused":   {"accent": "#d392d5", "hover": "#354F52"},
    "Tired":     {"accent": "#8b6d5e", "hover": "#99582A"},
    "Stressed":  {"accent": "#464e5c", "hover": "#7B2CBF"},
}


LEAF_TINT = {
    "Happy": (255, 240, 200),
    "Calm": (210, 230, 215),
    "Focused": (200, 215, 210),
    "Tired": (220, 200, 180),
    "Stressed": (220, 200, 230)
}


FONT = {
    "title_xl": ("Inter", 32, "bold"),
    "title": ("Inter", 26, "bold"),
    "section": ("Inter", 20, "bold"),
    "body": ("Inter", 14),
    "small": ("Inter", 12),
    "button": ("Inter", 14, "bold"),
}
# ------------------------------------------------------
# Helper for loading images without crashing
# ------------------------------------------------------
def load_image(relative_path, size=None, tint=None):
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, relative_path)

    if not os.path.exists(path):
        print(f"[ERROR] Image not found at: {path}")
        return None

    img = Image.open(path).convert("RGBA")

    if tint:
        overlay = Image.new("RGBA", img.size, tint + (30,))
        img = Image.alpha_composite(img, overlay)

    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)

    return CTkImage(light_image=img, dark_image=img, size=size)
# manger or main frame here
class MindGardenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # The app's main configurations (window size)
        self.title("MindGarden – Productivity Garden")
        self.geometry("1100x650")
        #self.resizable(False, False)
        self.minsize(850,650)
        self.maxsize(850, 650)
   
        # Background music/sound system .. pygame. once the mixer is initilized we can play sounds
        pygame.mixer.init()
        
        # Task manager from main
        self.manager = TaskManager()
        self.user_mood = "Happy"   # default
        # frame1 - or the current page we're in:
        self.current_frame = None

        # start on landing page(switch frame is defined after)
        self.switch_frame(LandingPage)
    #joining paths to avoid import errors 
    def play_sound(self, filename):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "assets", filename)
        print("Playing sound:", path)

        if not os.path.exists(path):
            print("[ERROR] Sound not found:", path)
            return

        try:
            pygame.mixer.Sound(path).play()
        except Exception as e:
            print("[SOUND ERROR]:", e)


    def switch_frame(self, frame_class):
        """Destroy current frame and replace it with another."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)
# ------------------------------------------------------
# Landing Page (mood selection + welcome animation) /haifa
# ------------------------------------------------------
class LandingPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        # loading the bg image
        bg_path = "assets/bg_landing.png"
        self.bg_image = load_image(bg_path, size=(1100, 650))

        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        else:
            self.configure(fg_color="#f3f3f3") 

        # Animated welcome text
        self.text_label = ctk.CTkLabel(self, text="", font=FONT["title_xl"], fg_color="transparent")
        self.text_label.place(relx=0.5, rely=0.15, anchor="center")

        self.full_text = "Welcome to MindGarden!\nHow are you feeling today?"
        self.animate_text_index = 0
        self.animate_text()

        # Mood buttons
        mood_frame = ctk.CTkFrame(self, fg_color="#db9567",corner_radius=5)  # or "transparent"
        mood_frame.place(relx=0.5, rely=0.45, anchor="center")

        moods = ["Happy", "Calm", "Focused", "Tired", "Stressed"]

        self.mood_var = ctk.StringVar(value="Happy")
        # a loop to make the same widget(radiobutton) for every mood at once :) 
        for m in moods:
            btn = ctk.CTkRadioButton(
                mood_frame,
                text=m,
                value=m,
                variable=self.mood_var,
                font=("Arial", 18),
                fg_color="green",
                hover_color="#4caf50",
            )
            btn.pack(padx=10, pady=5)

        # Continue button
        continue_btn = ctk.CTkButton(
            self,
            text="Continue →",
            font=("Arial", 20, "bold"),
            command=self.go_to_garden, 
            border_color="#388e3c",
            border_width=2,
            fg_color="#4caf50", 
            hover_color="#66bb6a",
        )
        continue_btn.place(relx=0.5, rely=0.75, anchor="center")

    #functions  
    def animate_text(self):
        if self.animate_text_index <= len(self.full_text):
            self.text_label.configure(text=self.full_text[:self.animate_text_index], fg_color="#e1a075")
            self.animate_text_index += 1
            #recurrsive call ::) /HAIFA
            self.after(35, self.animate_text)

    def go_to_garden(self):
        self.master.play_sound("click.wav") # clckck sound :P
        self.master.user_mood = self.mood_var.get() # based on mood
        self.master.switch_frame(GardenPage)

class GardenPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_task_id = None
        # Background image
        self.bg_image = load_image("assets/bg_garden.png", size=(1100, 650))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relwidth=1, relheight=1)

        mood = master.user_mood
        accent = MOODS[mood]["accent"]

        header = ctk.CTkFrame(self, fg_color=accent, height=60)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=f"Your Garden🌿",
            font=FONT["title"],
            text_color="#ffffff"
        ).pack(pady=10)

        self.page_scroll = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=520,
            fg_color="transparent",
        )
        self.page_scroll.pack(fill="both", expand=True, padx=20, pady=10)
       
        # Actual content holder
        content = ctk.CTkFrame(self.page_scroll, fg_color="transparent")
        content.pack(fill="both", expand=True)
        title = ctk.CTkLabel(
            content,
            text=f"{master.user_mood}",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=15)

        layout = ctk.CTkFrame(content, fg_color="#f1f8e9")
        layout.pack(fill="both", expand=True, padx=20, pady=20)

        layout.grid_columnconfigure(0, weight=1)
        layout.grid_columnconfigure(1, weight=4)

        # Left side – Add Task Panel
        self.create_task_panel(layout)

        # Right side – Plant + Board
        self.create_visual_garden(layout)

    def create_task_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=EARTH["panel"])

        panel.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        ctk.CTkLabel(panel, text="Add Task", font=("Arial", 22, "bold")).pack(pady=10)

        self.title_entry = ctk.CTkEntry(panel, placeholder_text="Task title")
        self.title_entry.pack(pady=5, fill="x")

        self.diff_var = ctk.StringVar(value="Easy")
        diff_menu = ctk.CTkOptionMenu(panel, values=["Easy", "Medium", "Hard"], variable=self.diff_var)
        diff_menu.pack(pady=5, fill="x")
        self.time_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Estimated time (minutes)"
        )
        self.time_entry.pack(pady=5, fill="x")
        add_btn = ctk.CTkButton(panel, text="Add Task",font=FONT["button"], command=self.add_task)
        add_btn.pack(pady=15)

    def create_visual_garden(self, parent):

    # plant images...
        right = ctk.CTkFrame(parent, fg_color=EARTH["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Plant image
        self.plant_label = ctk.CTkLabel(
            right,
            text="",
            width=350,
            height=350,
            fg_color="transparent"      # to get rid of greyness around the plant
        )
        self.plant_label.pack(pady=20)

        # Title for tasks
        ctk.CTkLabel(
            right, text="Your Tasks",
            font=FONT["section"],
            fg_color="transparent"
        ).pack(pady=5)

        # Task list frame
        self.task_list = ctk.CTkScrollableFrame(
            right,
            width=500,
            height=350,
            fg_color=EARTH["card"]
        )

        self.task_list.pack(pady=10)
    def add_task(self):
        title = self.title_entry.get().strip()
        difficulty = self.diff_var.get()
        mood = self.master.user_mood

        if not title:
            return

        task = self.master.manager.create_task(title, difficulty, mood)
        raw_time = self.time_entry.get().strip()

        if raw_time.isdigit() and int(raw_time) > 0:
            task.estimated_minutes = int(raw_time)
        else:
            task.estimated_minutes = 25  # fallback default

        task.estimated_seconds = task.estimated_minutes * 60
        task.elapsed_seconds = 0
        task.focus_running = False

        self.title_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.start_focus(task)

        self.refresh_tasks()
        self.refresh_plant()

    def refresh_plant(self):
        task = None  # IMPORTANT!!!! / Haifa

        if self.selected_task_id is None:
            tasks = self.master.manager.get_all_tasks()
            if not tasks:
                stage = "Seed"
            else:
                task = tasks[-1]
                stage = task.plant_state
        else:
            task = manager.get_task_by_id(self.selected_task_id)
            stage = task.plant_state

        if task and task.status == "completed":
            stage = "Blooming"

        self.animate_plant_growth(stage)

    def _create_active_task_card(self, task):
        card = ctk.CTkFrame(self.task_list, fg_color="#ffffff", corner_radius=12)
        card.pack(fill="x", pady=6, padx=6)

        # Select task on click
        card.bind("<Button-1>", lambda e, tid=task.task_id: self.set_selected_task(tid))

        # Task title
        ctk.CTkLabel(
            card,
            text=f"{task.title} ({task.difficulty})",
            font=("Arial", 14)
        ).pack(side="left", padx=12)

        # Time progress
        ctk.CTkLabel(
            card,
            text=f"{task.elapsed_seconds // 60}/{task.estimated_seconds // 60} min",
            font=("Arial", 12),
            text_color="#777777"
        ).pack(side="left", padx=6)

        # ---------------- GROW ----------------
        grow_btn = ctk.CTkButton(
            card,
            text="Grow",
            font=FONT["button"],
            width=60,
            command=lambda t=task: self.try_grow(t)
        )
        grow_btn.pack(side="right", padx=4)

        # ---------------- COMPLETE ----------------
        complete_btn = ctk.CTkButton(
            card,
            text="Complete",
            font=FONT["button"],
            width=80,
            fg_color="#81c784",
            hover_color="#66bb6a",
            command=lambda tid=task.task_id: self.complete_task(tid)
        )
        complete_btn.pack(side="right", padx=4)

        # ---------------- DELETE ----------------
        delete_btn = ctk.CTkButton(
            card,
            text="🗑",
            font=FONT["button"],
            width=40,
            fg_color="#e57373",
            hover_color="#ef5350",
            command=lambda tid=task.task_id: self.delete_task(tid)
        )
        delete_btn.pack(side="right", padx=4)


    def set_selected_task(self, task_id):
        self.selected_task_id = task_id
        task = self.master.manager.get_task_by_id(task_id)
        self.start_focus(task)
        self.refresh_plant()

    def show_completion_popup(self, task):
        popup = ctk.CTkToplevel(self)
        self.master.play_sound("completed.mp3")
        popup.title("Task Completed 🌸")
        popup.geometry("460x360")
        popup.resizable(False, False)

        popup.transient(self)
        popup.grab_set()

        # Center popup
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 230
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 180
        popup.geometry(f"+{x}+{y}")

        mood_colors = {
            "Happy": "#c8e6c9",
            "Calm": "#b2dfdb",
            "Focused": "#bbdefb",
            "Tired": "#d7ccc8",
            "Stressed": "#f8bbd0",
        }

        bg = mood_colors.get(self.master.user_mood, "#e8f5e9")

        container = ctk.CTkFrame(popup, fg_color=bg, corner_radius=18)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Title
        ctk.CTkLabel(
            container,
            text="🌸 Task Completed!",
            font=("Arial", 22, "bold")
        ).pack(pady=(15, 5))

        # Task name
        ctk.CTkLabel(
            container,
            text=f"“{task.title}”",
            font=("Arial", 16),
            wraplength=380
        ).pack(pady=(0, 10))

        # Reflection prompt
        ctk.CTkLabel(
            container,
            text="How did this task make you feel?",
            font=("Arial", 14)
        ).pack(pady=(5, 4))

        reflection_box = ctk.CTkTextbox(
            container,
            height=90,
            corner_radius=12,
            wrap="word"
        )
        reflection_box.pack(fill="x", padx=15, pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=(5, 10))

        def save_and_close():
            reflection = reflection_box.get("1.0", "end").strip()

            if reflection:
                self.save_reflection(task, reflection)

            popup.destroy()

        ctk.CTkButton(
            btn_frame,
            text="Save Reflection",
            font=FONT["button"],
            fg_color="#4caf50",
            hover_color="#66bb6a",
            width=140,
            command=save_and_close
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="Skip",
            font=FONT["button"],
            fg_color="#a5d6a7",
            hover_color="#81c784",
            width=100,
            command=popup.destroy
        ).pack(side="right", padx=8)

    def save_reflection(self, task, reflection_text):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "task_reflections.csv"
        )

        file_exists = os.path.exists(path)

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "task_id",
                    "title",
                    "difficulty",
                    "mood",
                    "reflection",
                    "completed_at"
                ])

            writer.writerow([
                task.task_id,
                task.title,
                task.difficulty,
                self.master.user_mood,
                reflection_text,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    def refresh_tasks(self):
        for widget in self.task_list.winfo_children():
            widget.destroy()

        tasks = self.master.manager.get_all_tasks()

        active_tasks = [t for t in tasks if t.status != "completed"]
        completed_tasks = [t for t in tasks if t.status == "completed"]

        # ---------- ACTIVE TASKS ----------
        if active_tasks:
            ctk.CTkLabel(
                self.task_list,
                text="Active Tasks",
                font=FONT["body"],

            ).pack(anchor="w", padx=10, pady=(5, 2))

            for t in active_tasks:
                self._create_active_task_card(t)

        # ---------- COMPLETED TASKS ----------
        if completed_tasks:
            ctk.CTkLabel(
                self.task_list,
                text="Completed 🌸",
                font=FONT["body"],

            ).pack(anchor="w", padx=10, pady=(20, 2))

            for t in completed_tasks:
                self._create_completed_task_card(t)

   

    def start_focus(self, task):
        if task.focus_running:
            return

        task.focus_running = True
        self.tick_focus(task)

    def tick_focus(self, task):
        if not task.focus_running:
            return

        task.elapsed_seconds += 1
        self.refresh_tasks()

        self.after(1000, lambda: self.tick_focus(task))

    def try_grow(self, task):
        if task.estimated_seconds <= 0:
            return

        ratio = task.elapsed_seconds / task.estimated_seconds

        if ratio < 0.25:
            self.master.play_sound("needs_time.wav")
            self.show_hint("🌱 Needs more time...")
            return
        elif ratio < 0.5:
            stage = "Sprout"
        elif ratio < 1.0:
            stage = "Growing"
        else:
            stage = "Blooming"

        if task.plant_state == stage:
            self.master.play_sound("needs_time.wav")
            self.show_hint("✨ Already at this stage")
            return

        task.plant_state = stage
        self.animate_plant_growth(stage)

    def animate_plant_growth(self, stage):
        self.master.play_sound("grow_seed.wav")
        sizes = {
            "Seed": 200,
            "Sprout": 240,
            "Growing": 280,
            "Blooming": 320
        }

        size = sizes.get(stage, 240)
        tint = LEAF_TINT.get(self.master.user_mood)

        img = load_image(
            f"assets/plant_{stage.lower()}.png",
            (size, size),
            tint=tint
        )

        if img:
            self.plant_label.configure(image=img)
            self.plant_label.image = img

    def complete_task(self, task_id):
        task = self.master.manager.get_task_by_id(task_id)
        task.mark_completed()

        self.show_completion_popup(task)

        self.refresh_tasks()
        self.refresh_plant()


    def delete_task(self, task_id):
        try:
            self.master.manager.delete_task(task_id)
            if self.selected_task_id == task_id:
                self.selected_task_id = None
            self.refresh_tasks()
            self.refresh_plant()
        except Exception as e:
            print("[ERROR] Could not delete task:", e)

    # this will create the completed task label where all the finished tasks will be placed on 
    def _create_completed_task_card(self, task):
        card = ctk.CTkFrame(
            self.task_list,
            fg_color="#eeeeee",
            corner_radius=12
        )
        card.pack(fill="x", pady=4, padx=6)

        ctk.CTkLabel(
            card,
            text=f"✔ {task.title}",
            font=FONT["body"],
            text_color="#777777"
        ).pack(side="left", padx=12)

    # basically flashes the notification when you press grow . 
    def show_hint(self, text):
        hint = ctk.CTkLabel(
            self,
            text=text,
            fg_color="#e8f5e9",
            corner_radius=10
        )
        hint.place(relx=0.5, rely=0.9, anchor="center")
        self.after(1500, hint.destroy)

if __name__ == "__main__":
    app = MindGardenApp()
    app.mainloop()
