import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

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
#def getDiseaseBySymptoms(symptoms):
    symptoms_list = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
    symptoms_data_lower = symptoms_data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
   
    symptoms_data_lower["match_count"] = symptoms_data_lower.iloc[:, 1:].apply(
        lambda row: sum(sym in row.values for sym in symptoms_list), axis=1
    )
   
    best_match = symptoms_data_lower.sort_values(by="match_count", ascending=False).iloc[0]
    return best_match["Disease"] if best_match["match_count"] > 0 else "No matching disease found."

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


# Function to get input from user and display results
def get_input():
    disease = entry_disease.get().strip()
    if not disease:
        messagebox.showwarning("Input Error", "Please enter a disease name.")
        return

    description = getDiseaseDetails(disease)
    precautions = getPrecautions(disease)
   
    result_textbox.config(state=tk.NORMAL)
    result_textbox.delete("1.0", tk.END)
    result_textbox.insert(tk.END, f"Disease Description:\n{description}\n\nPrecautions:\n{precautions}")
    result_textbox.config(state=tk.DISABLED)

# Function to predict disease from symptoms
def predict_disease():
    symptoms = entry_symptoms.get().strip()
    if not symptoms:
        messagebox.showwarning("Input Error", "Please enter symptoms separated by commas.")
        return

    predicted_disease = getDiseaseBySymptoms(symptoms)
   
    prediction_textbox.config(state=tk.NORMAL)
    prediction_textbox.delete("1.0", tk.END)
    prediction_textbox.insert(tk.END, f"Predicted Disease: {predicted_disease}")
    prediction_textbox.config(state=tk.DISABLED)

# Creating the main UI window
root = tk.Tk()
root.title("Medical Diagnosis Chatbot")
root.geometry("600x600")
root.configure(bg="#f0f0f0")

# Title Label
title_label = tk.Label(root, text="Medical Diagnosis Chatbot", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333")
title_label.pack(pady=10)

# Disease Input Section
frame_disease = tk.Frame(root, bg="#f0f0f0")
frame_disease.pack(pady=5, padx=20, fill="x")

tk.Label(frame_disease, text="Enter Disease Name:", font=("Arial", 12), bg="#f0f0f0").pack(side="left", padx=5)
entry_disease = tk.Entry(frame_disease, width=40, font=("Arial", 12))
entry_disease.pack(side="left", padx=5)
tk.Button(frame_disease, text="Get Details", command=get_input, font=("Arial", 12), bg="#4CAF50", fg="white").pack(side="left", padx=5)

# Disease Details Output
result_textbox = scrolledtext.ScrolledText(root, width=60, height=6, wrap=tk.WORD, font=("Arial", 12))
result_textbox.pack(pady=10, padx=20)
result_textbox.config(state=tk.DISABLED)

# Symptoms Input Section
frame_symptoms = tk.Frame(root, bg="#f0f0f0")
frame_symptoms.pack(pady=5, padx=20, fill="x")

tk.Label(frame_symptoms, text="Enter Symptoms (comma-separated):", font=("Arial", 12), bg="#f0f0f0").pack(side="left", padx=5)
entry_symptoms = tk.Entry(frame_symptoms, width=40, font=("Arial", 12))
entry_symptoms.pack(side="left", padx=5)
tk.Button(frame_symptoms, text="Predict Disease", command=predict_disease, font=("Arial", 12), bg="#2196F3", fg="white").pack(side="left", padx=5)

# Predicted Disease Output
prediction_textbox = scrolledtext.ScrolledText(root, width=60, height=4, wrap=tk.WORD, font=("Arial", 12))
prediction_textbox.pack(pady=10, padx=20)
prediction_textbox.config(state=tk.DISABLED)

# Run the GUI
root.mainloop()
