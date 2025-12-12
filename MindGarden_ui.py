import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
import pygame
from MindGarden_main import TaskManager, DifficultyTask

# ------------------------------
# App Configuration
# ------------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


# ------------------------------------------------------
# Helper for loading images safely
# ------------------------------------------------------
def load_image(relative_path, size=None):
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, relative_path)

    if not os.path.exists(path):
        print(f"[ERROR] Image not found at: {path}")
        return None

    img = Image.open(path)
    if size:
        img = img.resize(size)
    return CTkImage(light_image=img, dark_image=img, size=size)



# ------------------------------------------------------
# Main App (manages Frame switching)
# ------------------------------------------------------
class MindGardenApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MindGarden – Productivity Garden")
        self.geometry("1100x650")
        #self.resizable(False, False)
        self.minsize(850,650)
        self.maxsize(850, 650)
   
        self.after(500, lambda: print("Window size:", self.winfo_width(), "x", self.winfo_height()))


        # Background music/sound system
        pygame.mixer.init()

        # Task manager from your existing logic file
        self.manager = TaskManager()

        self.user_mood = "Happy"   # default

        # Frame container
        self.current_frame = None

        # Start on landing page
        self.switch_frame(LandingPage)

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
# Landing Page (mood selection + welcome animation)
# ------------------------------------------------------
class LandingPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        # Load background
        bg_path = "assets/bg_landing.png"
        self.bg_image = load_image(bg_path, size=(1100, 650))

        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(relwidth=1, relheight=1)
        else:
            self.configure(fg_color="#f3f3f3")  # fallback

        # Animated welcome text
        self.text_label = ctk.CTkLabel(self, text="", font=("Arial", 32, "bold"))
        self.text_label.place(relx=0.5, rely=0.15, anchor="center")

        self.full_text = "Welcome to MindGarden!\nHow are you feeling today?"
        self.animate_text_index = 0
        self.animate_text()

        # Mood buttons
        mood_frame = ctk.CTkFrame(self, fg_color="#ffffff")  # or "transparent"
        mood_frame.place(relx=0.5, rely=0.45, anchor="center")

        moods = ["Happy", "Calm", "Focused", "Tired", "Stressed"]

        self.mood_var = ctk.StringVar(value="Happy")

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

    # Typing animation
    def animate_text(self):
        if self.animate_text_index <= len(self.full_text):
            self.text_label.configure(text=self.full_text[:self.animate_text_index])
            self.animate_text_index += 1
            self.after(35, self.animate_text)

    def go_to_garden(self):
        self.master.play_sound("click.wav")
        self.master.user_mood = self.mood_var.get()
        self.master.switch_frame(GardenPage)


# ------------------------------------------------------
# Garden Page — drag & drop tasks + plant visualization
# ------------------------------------------------------
class GardenPage(ctk.CTkFrame):

  
    def __init__(self, master):
        super().__init__(master)
        self.selected_task_id = None
        print("[DEBUG] GardenPage started")

        # Background
        self.bg_image = load_image("assets/bg_garden.png", size=(1100, 650))
        print("[DEBUG] Background image:", self.bg_image)
        bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        bg_label.place(relwidth=1, relheight=1)
        print("[DEBUG] Loaded background")

        # Title
        title = ctk.CTkLabel(
            self,
            text=f"Your Garden ({master.user_mood})",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=15)
        print("[DEBUG] Title created")

        # Section container
        layout = ctk.CTkFrame(self, fg_color="transparent")


        layout.pack(fill="both", expand=True, padx=40, pady=20)
        print("[DEBUG] Layout created")

        layout.grid_columnconfigure(0, weight=1)
        layout.grid_columnconfigure(1, weight=4)

        # Left side – Add Task Panel
        self.create_task_panel(layout)
        print("[DEBUG] Left panel created")

        # Right side – Plant + Board
        self.create_visual_garden(layout)
        print("[DEBUG] Right panel created")

        print("[DEBUG] GardenPage initialization finished")


    # -------------------------------------
    # LEFT PANEL – Create new task
    # -------------------------------------
    def create_task_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        ctk.CTkLabel(panel, text="Add Task", font=("Arial", 22, "bold")).pack(pady=10)

        self.title_entry = ctk.CTkEntry(panel, placeholder_text="Task title")
        self.title_entry.pack(pady=5, fill="x")

        self.diff_var = ctk.StringVar(value="Easy")
        diff_menu = ctk.CTkOptionMenu(panel, values=["Easy", "Medium", "Hard"], variable=self.diff_var)
        diff_menu.pack(pady=5, fill="x")

        add_btn = ctk.CTkButton(panel, text="Add Task", command=self.add_task)
        add_btn.pack(pady=15)

    # -------------------------------------
    # RIGHT PANEL – Plant visualization + tasks
    # -------------------------------------
    def create_visual_garden(self, parent):

    # plant images...
    
        right = ctk.CTkFrame(parent, fg_color="transparent")


        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Plant image
        self.plant_label = ctk.CTkLabel(
            right,
            text="",
            width=350,
            height=350,
            fg_color="transparent"      # important to avoid grey box around plant
        )
        self.plant_label.pack(pady=20)

        # Title for tasks
        ctk.CTkLabel(
            right, text="Your Tasks",
            font=("Arial", 20, "bold"),
            fg_color="transparent"
        ).pack(pady=5)

        # Task list frame
        self.task_list = ctk.CTkScrollableFrame(
            right,
            width=500,
            height=350,
            fg_color="#ffffff",          # or "transparent"
        )
        self.task_list.pack(pady=10)



    # -------------------------------------
    def refresh_plant(self):
        manager = self.master.manager

        if self.selected_task_id is None:
            tasks = manager.get_all_tasks()
            if not tasks:
                stage = "Seed"
            else:
                # default to last created
                stage = tasks[-1].plant_state
        else:
            task = manager.get_task_by_id(self.selected_task_id)
            stage = task.plant_state


        img = self.images.get(stage)

        if img:
            self.plant_label.configure(image=img)
        else:
            print("[ERROR] Missing plant stage image:", stage)
    

    # -------------------------------------
    def refresh_tasks(self):
        """Refresh the task cards list."""
        for widget in self.task_list.winfo_children():
            widget.destroy()

        tasks = self.master.manager.get_all_tasks()

        for t in tasks:
            card = ctk.CTkFrame(self.task_list, fg_color="#ffffff")
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(card, text=f"{t.title} ({t.difficulty})").pack(side="left", padx=10)

            update_btn = ctk.CTkButton(
            card,
            text="Grow",
            width=60,
            command=lambda tid=t.task_id: self.update_task(tid)
        )
            update_btn.pack(side="right", padx=5)

            card.bind("<Button-1>", lambda e, tid=t.task_id: self.set_selected_task(tid))

            
            del_btn = ctk.CTkButton(
                card,
                text="Complete",
                width=80,
                command=lambda tid=t.task_id: self.complete_task(tid)
            )
            del_btn.pack(side="right", padx=5)

    # -------------------------------------
    def add_task(self):
        title = self.title_entry.get().strip()
        difficulty = self.diff_var.get()
        mood = self.master.user_mood

        if not title:
            return

        task = self.master.manager.create_task(title, difficulty, mood)
        self.title_entry.delete(0, "end")
        self.refresh_tasks()
        self.refresh_plant()

    def set_selected_task(self, task_id):
        self.selected_task_id = task_id
        print("[DEBUG] Selected task:", task_id)
        self.refresh_plant()


    # -------------------------------------
    def update_task(self, task_id):
        self.master.manager.update_task_progress(task_id)
        self.refresh_tasks()
        self.refresh_plant()

    # -------------------------------------
    def complete_task(self, task_id):
        t = self.master.manager.get_task_by_id(task_id)
        t.mark_completed()
        self.refresh_tasks()
        self.refresh_plant()


# ------------------------------------------------------
# Run App
# ------------------------------------------------------
if __name__ == "__main__":
    app = MindGardenApp()
    app.mainloop()
