import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import requests 

all_buttons = []



def button_press(button, row, col):
    for item in all_buttons:
        item.config(bg = "lightblue")
    button.config(bg="red")
#Logic for zone selection
def zoneChoice():
    for k in range(0,len(all_buttons)):
        if(all_buttons[k].cget("bg") == "red"):
            if k<4:
                return k+11
            elif k>=4:
                return k-3
            else:
                return 0
    
def create_buttons(canvas, grid_size, offset=(0, 0), button_size=20, gap=5, color="lightblue"):
    buttons = []
    for row in range(grid_size[0]):
        row_buttons = []
        for col in range(grid_size[1]):
            x0 = offset[0] + col * (button_size + gap)
            y0 = offset[1] + row * (button_size + gap)

            button = tk.Button(canvas, bg=color, text="")
            button.config(command=lambda b=button, r=row, c=col: button_press(b, r, c))        
            button.place(x=x0, y=y0, width=button_size, height=button_size)

            row_buttons.append(button)
            all_buttons.append(button)
        buttons.append(row_buttons)
    return buttons

def post_request():
    data = {
        "pitcherHandedness" : input_fields["Pitcher Hand"].get(),
        "batterHandedness" : input_fields["Batter Hand"].get(),
        "pitchType" : input_fields["Pitch Type"].get(),
        "velocity" : input_fields["Velocity"].get(),
        "horizontalBreak" : input_fields["Horizontal Break"].get(),
        "verticalBreak" : input_fields["Vertical Break"].get(),
        "zone" : zoneChoice(),
        "balls" : input_fields["Balls"].get(),
        "strikes" : input_fields["Strikes"].get(),
    }
    try:
        response = requests.post('http://flask-pab.azurewebsites.net/add_pitch_entry', json=data)
        response_data = response.json()
        print(response_data)
        display_information(response_data)
        response = requests.get('http://flask-pab.azurewebsites.net/get_history')
        dataList = response.json()
        update_history(dataList)
    except requests.exceptions.RequestException as e:
        print(e)

def display_information(response_data):
    data = response_data["prediction"]

    pitch_result_box.config(state= tk.NORMAL)
    pitch_result_box.delete(0, 10000)
    pitch_result_box.insert(0, data['result'])
    pitch_result_box.config(state= tk.DISABLED)


    
    probability_data = data['probabilities']
    probability_entries["Contact"].config(state= tk.NORMAL)
    probability_entries["Contact"].delete(0,10000)
    probability_entries["Contact"].insert(0, probability_data['contact'])
    probability_entries["Contact"].config(state= tk.DISABLED)

    probability_entries["Ball"].config(state= tk.NORMAL)
    probability_entries["Ball"].delete(0,10000)
    probability_entries["Ball"].insert(0, probability_data['ball'])
    probability_entries["Ball"].config(state= tk.DISABLED)
                                       
    probability_entries["Strike"].config(state= tk.NORMAL)
    probability_entries["Strike"].delete(0,10000)
    probability_entries["Strike"].insert(0, probability_data['strike'])
    probability_entries["Strike"].config(state= tk.DISABLED)

def filterJson(data, filter):
    return sorted(data, key=lambda x: x[filter])

def on_combobox_select(event, data):
    selected = filter_option.get()
    history_items = filterJson(data, selected)
    update_history(history_items)

def on_listbox_select(event):
    selected_indices = history_listbox.curselection()
    if selected_indices:  # Check if something is selected
        selected_index = selected_indices[0]
        # Display the selected item in a message box
        messagebox.showinfo(f"Pitch Entry ID: {history_items[selected_index]['pitchEntryID']}",
                            f"Time Stamp: {history_items[selected_index]['timestamp']}",
                            f"Pitch Result: {history_items[selected_index]['result']}",
                            f"Contact Probability: {history_items[selected_index]['contactprob']}",
                            f"Ball Probability: {history_items[selected_index]['ballprob']}",
                            f"Strike Probability: {history_items[selected_index]['strikeprob']}",
                            f"Pitcher Handedness: {history_items[selected_index]['pitcherHandedness']}",
                            f"Batter Handedness: {history_items[selected_index]['batterHandedness']}",
                            f"Time Stamp: {history_items[selected_index]['timestamp']}",
                            f"Pitch Type: {history_items[selected_index]['pitchType']}",
                            f"Velocity: {history_items[selected_index]['velocity']}",
                            f"Horizontal Break: {history_items[selected_index]['horizontalBreak']}",
                            f"Vertical Break: {history_items[selected_index]['verticalBreak']}",
                            f"Location: {history_items[selected_index]['zone']}",
                            f"Count: {history_items[selected_index]['balls']}-{history_items[selected_index]['strikes']}")


def validate_inputs():
    # Dictionary to store regex patterns for each input field
    regex_patterns = {
        "Pitcher Hand": r"^(left|right)|(Left|Right)$",  
        "Batter Hand": r"^(left|right)|(Left|Right)$",  
        "Pitch Type": r"^.+$", #non empty
        "Velocity": r"^\d+(\.\d{1,2})?$", #number
        "Horizontal Break": r"^-?\d+(\.\d{1,2})?$",  #number
        "Vertical Break": r"^-?\d+(\.\d{1,2})?$",  #number
        "Balls": r"^\d+$",  #whole number
        "Strikes": r"^\d+$",  #whole number
    }
    for label_text, input_field in input_fields.items():
        user_input = input_field.get()  
        pattern = regex_patterns.get(label_text)  

        # If there is a regex pattern, apply it
        if pattern and not re.match(pattern, user_input):
            response_label.config(text=f"Invalid input for '{label_text}'")  
            return  # Stop if there's an invalid input
        #check velo
        if label_text == "Velocity":
            try:
                velocity_value = float(user_input)
                min_velocity = 30
                max_velocity = 110
                if velocity_value < min_velocity or velocity_value > max_velocity:
                    response_label.config(text=f"Velocity must be between {min_velocity} and {max_velocity}")
                    return  # Stop if velocity is out of range
            except ValueError:
                response_label.config(text="Velocity must be a valid number")
                return
        #check breaks
        if label_text == "Horizontal Break":
            break_value = float(user_input)
            if break_value <-3 or break_value > 3:
                response_label.config(text=f"Horizontal Break must be between -3 and 3")
                return
        if label_text == "Vertical Break":
            break_value = float(user_input)
            if break_value <-3 or break_value > 2:
                response_label.config(text=f"Vertical Break must be between -3 and 2")
                return
        #checks count
        if label_text == "Balls":
            ball_count = int(user_input)
            if ball_count < 0 or ball_count > 4:
                response_label.config(text=f"Balls must be between 0 and 4")
                return
        if label_text == "Strikes":
            strike_count = int(user_input)
            if strike_count < 0 or strike_count > 2:
                response_label.config(text=f"Strikes must be between 0 and 2")
                return
    #checks zone
    if zoneChoice() == 0:
        response_label.config(text="Please select a zone")
        return
    post_request()

    response_label.config(text="All inputs are valid, Sending to Server")

def update_history(dataList):
    history_items = dataList
    history_listbox.delete(0, tk.END)
    for i in len(history_items):
        history_listbox.insert(tk.END, f"Entry {i['pitchEntryID']}")
        history_listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Initialize the main window
root = tk.Tk()
root.attributes("-fullscreen", True)  # Full screen mode
root.title("Prediction Input")

# Add escape key binding to exit full screen
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

frame_left = tk.Frame(root, bd=2, relief="groove")  # Left side 
frame_left.place(relwidth=0.7, relheight=1.0, x=0, y=0) 

frame_history = tk.Frame(root, bd=2, relief="groove")  # Right side 
frame_history.place(relx=0.7, relwidth=0.3, relheight=1.0, y=0)  

# Container Frame to stack top and bottom frames vertically on the left
frame_input_container = tk.Frame(frame_left)
frame_input_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

frame_input_container.grid_columnconfigure(0, weight=1)  # Regex
frame_input_container.grid_columnconfigure(0, weight=1)  # Pitch Information
frame_input_container.grid_columnconfigure(1, weight=1)  # Strike Zone

# Pitch Information 
pitch_info_title_label = tk.Label(frame_input_container, text="Pitch Information", font=("Helvetica", 14, "bold"))
pitch_info_title_label.grid(row=0, column=0, columnspan=3, pady=(10, 10))

# Validation
frame_input_top = tk.Frame(frame_input_container)
frame_input_top.grid(row=1, column=0, sticky="nsew", padx=5, pady=(5, 5))
validation_label = tk.Label(frame_input_top, text="Validation", font=("Helvetica", 12, "bold"))
validation_label.grid(row=0, column=0, columnspan=2, pady=5)
response_label = tk.Label(frame_input_top, text="", font=("Helvetica", 12))
response_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)

# Pitch Information 
frame_input_bottom = tk.Frame(frame_input_container)
frame_input_bottom.grid(row=1, column=1, sticky="nsew", padx=5, pady=(5, 5))
pitch_info_label = tk.Label(frame_input_bottom, text="Input Pitch Information", font=("Helvetica", 14, "bold"))
pitch_info_label.grid(row=0, column=0, columnspan=2, pady=(5, 10))


# Input fields for  Pitch Information (aligned to the left)
labels = ["Pitcher Hand", "Batter Hand","Pitch Type", "Velocity", "Horizontal Break", "Vertical Break", "Balls", "Strikes"]
input_fields = {}

for i, label_text in enumerate(labels, start=1):
    label = tk.Label(frame_input_bottom, text=label_text, font=("Helvetica", 12))
    label.grid(row=i, column=0, sticky="e", padx=5, pady=3)
    if label_text.__contains__("Hand"):
        input_field = ttk.Combobox(frame_input_bottom, values=["Left", "Right"], font=("Helvetica", 12))
    else:
        input_field = tk.Entry(frame_input_bottom, font=("Helvetica", 12))
    input_fields[label_text] = input_field
    input_field.grid(row=i, column=1, padx=5, pady=3)

# Zone Selection Section (Right Side of frame_left - Column 3)
frame_zone = tk.Frame(frame_input_container)
frame_zone.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
zone_label = tk.Label(frame_zone, text="Select Zone", font=("Helvetica", 14, "bold"))
zone_label.pack(pady=(10, 5))
zone_canvas = tk.Canvas(frame_zone, width=100, height=100, bg="white")
zone_canvas.pack(pady=5)

#button creation for zone
button_size_2x2 = 45
gap_2x2 = 5
offset_2x2 = (5, 5)  
create_buttons(zone_canvas, (2, 2), offset=offset_2x2, button_size=button_size_2x2, gap=gap_2x2, color="lightblue")
button_size_3x3 = 20
gap_3x3 = 3
offset_3x3 = (20, 20)  
create_buttons(zone_canvas, (3, 3), offset=offset_3x3, button_size=button_size_3x3, gap=gap_3x3, color="lightblue")


enter_button = tk.Button(frame_zone, text="Enter Prediction", bg="blue", fg="white", font=("Helvetica", 12), command=validate_inputs)
enter_button.pack(pady=10)

# Prediction Results Frame (Center of the Left Frame)
frame_results = tk.Frame(frame_left, bd=2, relief="groove")  
frame_results.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.5)  # Positioned to the left, 90% width of frame_left
results_label = tk.Label(frame_results, text="Prediction Results", font=("Helvetica", 20, "bold"))
results_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))

pitch_result_label = tk.Label(frame_results, text="Pitch Result", font=("Helvetica", 16, "bold"))
pitch_result_label.grid(row=1, column=0, padx=10, pady=10)
pitch_result_box = tk.Entry(frame_results, font=("Helvetica", 14), state=tk.DISABLED)
pitch_result_box.grid(row=2, column=0, padx=10, pady=15)

probabilities_label = tk.Label(frame_results, text="Probabilities", font=("Helvetica", 16, "bold"))
probabilities_label.grid(row=1, column=1, padx=10, pady=10)

probability_fields = ["Contact", "Strike", "Ball"]
probability_entries = {}
for i, field in enumerate(probability_fields, start=2):
    label = tk.Label(frame_results, text=field, font=("Helvetica", 14))
    label.grid(row=i, column=1, sticky="e", padx=10, pady=10)
    entry = tk.Entry(frame_results, font=("Helvetica", 14), state=tk.DISABLED)
    entry.grid(row=i, column=2, padx=10, pady=10)
    probability_entries[field] = entry

# History Frame (Right Side)
history_label = tk.Label(frame_history, text="History", font=("Helvetica", 20, "bold"))
history_label.pack(pady=(20, 20))

filter_label = tk.Label(frame_history, text="Filter by", font=("Helvetica", 16))
filter_label.pack(pady=10)
filter_option = ttk.Combobox(frame_history, values=["pitchEntryID", "timestamp","result", "contactprob", "ballprob", "strikeprob", "pitcherHandedness", "batterHandedness", "pitchType", "velocity", "horizontalBreak", "verticalBreak", "zone", "balls", "strikes"], font=("Helvetica", 14))
filter_option.bind("<<ComboboxSelected>>", on_combobox_select)
filter_option.pack(pady=10)

history_listbox = tk.Listbox(frame_history, font=("Helvetica", 14))
response = requests.get('http://flask-pab.azurewebsites.net/get_history')
history_items = response.json()
print(history_items)

for i in len(history_items):
    history_listbox.insert(tk.END, f"Entry {i['pitchEntryID']}")
    history_listbox.bind("<<ListboxSelect>>", on_listbox_select)

history_listbox.pack(fill="both", expand=True, padx=10, pady=10)

# Run the application
root.mainloop()
