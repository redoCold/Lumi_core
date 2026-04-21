import tkinter as tk
import psutil  
import os
os.environ["DISPLAY"] = ":0"
class RobotFace:
    def __init__(self, root):
        self.root = root
        self.root.title("HMI")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<F11>", lambda event: self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen")))
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(root, width=screen_width, 
                                height=screen_height, 
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        self.up_loop()
    def draw_battery(self, percentage):
        self.canvas.delete("battery") 
        x_start = self.root.winfo_screenwidth() - 120
        y_start = 40
        self.canvas.create_rectangle(x_start, y_start, x_start + 80, y_start + 40, 
                                     outline="white", width=3, tags="battery")
        self.canvas.create_rectangle(x_start + 80, y_start + 10, x_start + 88, y_start + 30, 
                                     fill="white", tags="battery")
        if percentage < 20: 
            color = "red" 
        elif percentage < 50: 
            color = "yellow"
        else: 
            color = "green"

        fill_width = (percentage / 100) * 74
        self.canvas.create_rectangle(x_start + 3, y_start + 3, x_start + 3 + fill_width, y_start + 37, 
                                     fill=color, tags="battery")
        
        self.canvas.create_text(x_start - 40, y_start + 20, text=f"{percentage}%", 
                                fill="white", font=("Arial", 14), tags="battery")
    def up_loop(self):
        try:
            battery = psutil.sensors_battery()
            percent = int(battery.percent) if battery else 100
        except:
            percent = 99
            print("Battery read error")
            
        self.draw_battery(percent)
        self.root.after(5000, self.up_loop)

if __name__ == "__main__":
    root = tk.Tk()
    face = RobotFace(root)
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()