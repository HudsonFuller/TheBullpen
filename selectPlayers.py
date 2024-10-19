import tkinter as tk

root = tk.Tk()
root.title("Select Players")
root.geometry("500x400")
root.config(bg="#2C3E50")  


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

footer_label1 = tk.Label(
    root, 
    text="Software Engineering 2024 - Professor Jason Jenkins", 
    font=("MoolBoran", 9), 
    fg="lightgray", 
    bg="#2C3E50"
)
footer_label1.pack(side="bottom", pady=0)


root.mainloop()
