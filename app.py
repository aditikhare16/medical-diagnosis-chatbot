import pandas as pd
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Load CSV Files
try:
    description_data = pd.read_csv("disease_description.csv")
    precautions_data = pd.read_csv("disease_precautions.csv")
    symptoms_data = pd.read_csv("disease_symptoms.csv")

    # Strip spaces from column names
    description_data.columns = description_data.columns.str.strip()
    precautions_data.columns = precautions_data.columns.str.strip()
    symptoms_data.columns = symptoms_data.columns.str.strip()

except FileNotFoundError:
    messagebox.showerror("Error", "CSV files not found. Please check file names.")
    exit()

# Function to get disease description
def getDiseaseDetails(disease):
    result = description_data[description_data["Disease"].str.lower() == disease.lower()]["Description"]
    return result.values[0] if not result.empty else "Disease not found in database."

# Function to get precautions for a disease
def getPrecautions(disease):
    result = precautions_data[precautions_data["Disease"].str.lower() == disease.lower()]
    if result.empty:
        return "No precautions found."
    precautions = result.iloc[:, 1:].values.flatten()
    return "\n".join([p for p in precautions if pd.notna(p)])

# Function to get disease based on symptoms
def getDiseaseBySymptoms(symptoms):
    symptoms_list = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
    
    # Ensure all symptom values are properly formatted
    symptoms_data_cleaned = symptoms_data.copy()
    symptoms_data_cleaned.iloc[:, 1:] = symptoms_data_cleaned.iloc[:, 1:].applymap(
        lambda x: x.strip().lower() if isinstance(x, str) else x
    )

    # Count how many symptoms match per disease
    symptoms_data_cleaned["match_count"] = symptoms_data_cleaned.iloc[:, 1:].apply(
        lambda row: sum(sym in row.values for sym in symptoms_list), axis=1
    )
    
    # Get the best-matching disease
    best_match = symptoms_data_cleaned.loc[symptoms_data_cleaned["match_count"].idxmax()]

    # Check if there was at least one match
    return best_match["Disease"] if best_match["match_count"] > 0 else "No matching disease found."

# Function to update input label dynamically
def update_input_label(*args):
    selected_option = option_var.get()
    if selected_option == "Symptom-Based Prediction":
        input_label.config(text="Enter Symptoms (comma-separated):")
    else:
        input_label.config(text="Enter Disease Name:")

# Function to process user input
def get_input():
    user_input = input_entry.get().strip()
    
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter valid input.")
        return

    selected_option = option_var.get()

    if selected_option == "Symptom-Based Prediction":
        predicted_disease = getDiseaseBySymptoms(user_input)
        
        if predicted_disease == "No matching disease found.":
            result_textbox.config(state=tk.NORMAL)
            result_textbox.delete("1.0", tk.END)
            result_textbox.insert(tk.END, predicted_disease)
            result_textbox.config(state=tk.DISABLED)
            return

        description = getDiseaseDetails(predicted_disease)
        precautions = getPrecautions(predicted_disease)

        result_textbox.config(state=tk.NORMAL)
        result_textbox.delete("1.0", tk.END)
        result_textbox.insert(tk.END, f"Predicted Disease: {predicted_disease}\n\n")
        result_textbox.insert(tk.END, f"Disease Description:\n{description}\n\n")
        result_textbox.insert(tk.END, f"Precautions:\n{precautions}")
        result_textbox.config(state=tk.DISABLED)

    else:
        description = getDiseaseDetails(user_input)
        precautions = getPrecautions(user_input)

        result_textbox.config(state=tk.NORMAL)
        result_textbox.delete("1.0", tk.END)
        result_textbox.insert(tk.END, f"Disease Description:\n{description}\n\n")
        result_textbox.insert(tk.END, f"Precautions:\n{precautions}")
        result_textbox.config(state=tk.DISABLED)

# Setting up the GUI
root = tk.Tk()
root.title("Disease Prediction System")
root.geometry("700x600")
root.configure(bg="#f8f9fa")

# Wall-E Greeting
greeting_label = tk.Label(root, text="Hi! I'm Wall-E. How can I help you today?", font=("Arial", 16, "bold"), bg="#f8f9fa", fg="#333")
greeting_label.pack(pady=20)

# Option to select between symptom-based prediction or disease details
option_var = tk.StringVar(value="Symptom-Based Prediction")
option_var.trace("w", update_input_label)

tk.Label(root, text="Select an option:", font=("Arial", 12), bg="#f8f9fa").pack(pady=10)
option_menu = tk.OptionMenu(root, option_var, "Symptom-Based Prediction", "Disease Details")
option_menu.config(font=("Arial", 12), bg="#ffffff", fg="#333", width=25)
option_menu.pack(pady=5)

# Input label and entry field (dynamically changes based on option selected)
input_label = tk.Label(root, text="Enter Symptoms (comma-separated):", font=("Arial", 12), bg="#f8f9fa")
input_label.pack(pady=10)

input_entry = tk.Entry(root, width=50, font=("Arial", 12))
input_entry.pack(pady=5)

# Button to submit input
submit_button = tk.Button(root, text="Submit", command=get_input, font=("Arial", 12, "bold"), bg="#2196F3", fg="white", width=15)
submit_button.pack(pady=10)

# Result display area
result_textbox = scrolledtext.ScrolledText(root, width=70, height=10, wrap=tk.WORD, font=("Arial", 12))
result_textbox.pack(pady=10, padx=20)
result_textbox.config(state=tk.DISABLED)

# Start the Tkinter event loop
root.mainloop()
