import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import statistics
import tkinter as tk
from tkinter import messagebox

# ------ Reading the training data and removing empty columns ------ #
DATA_PATH = "Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

# ------ Reading precaution and description data from CSV files ------ #
precaution_data = pd.read_csv("symptom_precaution.csv")
description_data = pd.read_csv("symptom_Description.csv")

# ------ Encoding the target variable (disease) into numerical format ------ #
encoder = LabelEncoder()
data["Disease"] = encoder.fit_transform(data["Disease"])

# ------ Convert symptoms into binary format (1 for present, 0 for absent) ------ #
X = data.iloc[:, :-1]
X = pd.get_dummies(X)  # One-hot encoding for symptom names
y = np.array(data["Disease"])

# ------ Splitting data into training and testing sets ------ #
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=24)

# ------ Training models ------ #
final_svm_model = SVC()
final_nb_model = GaussianNB()
final_rf_model = RandomForestClassifier(random_state=18)
final_svm_model.fit(X, y)
final_nb_model.fit(X, y)
final_rf_model.fit(X, y)

# ------ Creating a dictionary for symptom lookup ------ #
symptoms = X.columns.values
symptom_index = {symptom.replace("_", " ").capitalize(): i for i, symptom in enumerate(symptoms)}

data_dict = {
    "symptom_index": symptom_index,
    "predictions_classes": encoder.classes_
}

# ------ Function to predict disease ------ #
def predictDisease(symptoms):
    symptoms = symptoms.split(", ")
    input_data = [0] * len(data_dict["symptom_index"])
    
    for symptom in symptoms:
        # Normalize the symptom by stripping extra spaces and capitalizing
        normalized_symptom = symptom.strip().lower().replace(" ", "_")
        
        print(f"Normalized symptom: {normalized_symptom}")  # Debugging line
        
        if normalized_symptom in data_dict["symptom_index"]:
            index = data_dict["symptom_index"][normalized_symptom]
            input_data[index] = 1
        else:
            messagebox.showerror("Error", f"Symptom '{symptom}' not found in the dataset.")
            return None
    
    input_data = np.array(input_data).reshape(1, -1)
    input_data_df = pd.DataFrame(input_data, columns=X.columns)

    rf_prediction = final_rf_model.predict(input_data_df)[0]
    nb_prediction = final_nb_model.predict(input_data_df)[0]
    svm_prediction = final_svm_model.predict(input_data_df)[0]

    final_prediction = statistics.mode([ 
        data_dict["predictions_classes"][rf_prediction],
        data_dict["predictions_classes"][nb_prediction],
        data_dict["predictions_classes"][svm_prediction]
    ])

    try:
        precautions = precaution_data[precaution_data["disease"] == final_prediction].iloc[0, 1:].dropna().values
    except IndexError:
        precautions = ["No precautions available for this disease."]
    
    try:
        description = description_data[description_data["disease"] == final_prediction]["Description"].values[0]
    except IndexError:
        description = "No description available for this disease."
    
    return {
        "final_prediction": final_prediction,
        "precautions": precautions,
        "description": description
    }

# ------ Function to fetch disease details ------ #
def getDiseaseDetails(disease):
    try:
        description = description_data[description_data["disease"] == disease]["Description"].values[0]
        precautions = precaution_data[precaution_data["disease"] == disease].iloc[0, 1:].dropna().values
    except IndexError:
        description = ["No description available for this disease."]
        precautions = ["No precautions available for this disease."]
    
    return {
        "description": description,
        "precautions": precautions
    }

# ------ Function to get input and make predictions ------ #
def get_input():
    if option_var.get() == "Symptom-Based Prediction":
        symptoms = input_entry.get()
        if symptoms:
            result = predictDisease(symptoms)
            if result:
                result_label.config(text=f"Final Prediction: {result['final_prediction']}\n"
                                       f"Description: {result['description']}\n"
                                       f"Precautions: {', '.join(result['precautions'])}")
            else:
                result_label.config(text="No valid prediction found.")
        else:
            messagebox.showerror("Input Error", "Please enter some symptoms.")
    
    elif option_var.get() == "Disease Details":
        disease = input_entry.get()
        if disease:
            result = getDiseaseDetails(disease)
            if result:
                result_label.config(text=f"Disease: {disease}\n"
                                       f"Description: {result['description']}\n"
                                       f"Precautions: {', '.join(result['precautions'])}")
            else:
                result_label.config(text="No valid details found for this disease.")
        else:
            messagebox.showerror("Input Error", "Please enter a disease name.")

# ------ Function to update input label based on user selection ------ #
def update_input_label(*args):
    input_label.config(text="Enter Symptoms (comma-separated):" if option_var.get() == "Symptom-Based Prediction" else "Enter Disease Name:")

# ------ Setting up GUI ------ #
root = tk.Tk()
root.title("Disease Prediction System")
tk.Label(root, text="Hi! I'm Wall-E. How can I help you today?", font=("Arial", 16)).pack(pady=20)

option_var = tk.StringVar(value="Symptom-Based Prediction")
option_var.trace("w", update_input_label)
tk.Label(root, text="Select an option:").pack(pady=10)
tk.OptionMenu(root, option_var, "Symptom-Based Prediction", "Disease Details").pack(pady=5)

input_label = tk.Label(root, text="Enter Symptoms (comma-separated):")
input_label.pack(pady=10)
input_entry = tk.Entry(root, width=50)
input_entry.pack(pady=5)

tk.Button(root, text="Submit", command=get_input).pack(pady=10)
result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=400)
result_label.pack(pady=10)

root.mainloop()
