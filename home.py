import tkinter as tk
import subprocess

root = tk.Tk()
root.title("Home")
root.geometry("500x400")
root.config(bg="#2C3E50")  

def predict_button_click():
    subprocess.Popen(['python','selectPlayers.py'])

welcome_label = tk.Label(
    root, 
    text="The Bullpen Predictive Analytics for Pitching", 
    font=("MoolBoran", 16, "bold"), 
    fg="white",  
    bg="#2C3E50"  
)
welcome_label.pack(pady=40)  

button_frame = tk.Frame(root, bg="#2C3E50")
button_frame.pack(pady=20)

predict_button = tk.Button(
    button_frame, 
    text="Predict", 
    font=("MoolBoran", 14, "bold"), 
    bg="#3498DB",  
    fg="white",  
    activebackground="#2980B9",  
    activeforeground="white",  
    width=10,
    height=2,
    command=predict_button_click
)
predict_button.pack()

footer_label1 = tk.Label(
    root, 
    text="Software Engineering 2024 - Professor Jason Jenkins", 
    font=("MoolBoran", 9), 
    fg="lightgray", 
    bg="#2C3E50"
)
footer_label2 = tk.Label(
    root, 
    text="Built by - Hudson Fuller, Cole Drumheller, Samuel Kampshoff", 
    font=("MoolBoran", 12), 
    fg="lightgray", 
    bg="#2C3E50"
)
footer_label1.pack(side="bottom", pady=0)
footer_label2.pack(side="bottom", pady=20)


root.mainloop()
