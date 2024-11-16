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

# Reading data
DATA_PATH = "D:\\Python\\chatbotpro\\Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)
precaution_data = pd.read_csv('D:\\Python\\chatbotpro\\symptom_precaution.csv')
description_data = pd.read_csv('D:\\Python\\chatbotpro\\symptom_Description.csv')

# Encoding target value
encoder = LabelEncoder()
data["prognosis"] = encoder.fit_transform(data["prognosis"])

# Splitting data
X = data.iloc[:, :-1]
y = data.iloc[:, -1]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=24)

# Training models
final_svm_model = SVC()
final_nb_model = GaussianNB()
final_rf_model = RandomForestClassifier(random_state=18)
final_svm_model.fit(X_train, y_train)
final_nb_model.fit(X_train, y_train)
final_rf_model.fit(X_train, y_train)

# Creating symptom index
symptoms = X.columns.values
symptom_index = { " ".join([i.capitalize() for i in value.split("_")]): index for index, value in enumerate(symptoms)}

data_dict = {
    "symptom_index": symptom_index,
    "predictions_classes": encoder.classes_
}

# Define prediction function
def predictDisease(symptoms):
    symptoms = symptoms.split(", ")
    input_data = [0] * len(data_dict["symptom_index"])

    for symptom in symptoms:
        formatted_symptom = " ".join([i.capitalize() for i in symptom.split("_")])
        if formatted_symptom in data_dict["symptom_index"]:
            index = data_dict["symptom_index"][formatted_symptom]
            input_data[index] = 1
        else:
            messagebox.showerror("Error", f"Symptom '{symptom}' not found in the dataset.")
            return None

    input_data = np.array(input_data).reshape(1, -1)
    input_data_df = pd.DataFrame(input_data, columns=X.columns)

    rf_prediction = final_rf_model.predict(input_data_df)[0]
    nb_prediction = final_nb_model.predict(input_data_df)[0]
    svm_prediction = final_svm_model.predict(input_data_df)[0]

    rf_prediction_disease = data_dict["predictions_classes"][rf_prediction]
    nb_prediction_disease = data_dict["predictions_classes"][nb_prediction]
    svm_prediction_disease = data_dict["predictions_classes"][svm_prediction]

    final_prediction = statistics.mode([rf_prediction_disease, nb_prediction_disease, svm_prediction_disease])

    precautions = precaution_data[precaution_data["prognosis"] == final_prediction].iloc[0, 1:].dropna().values
    description = description_data[description_data["prognosis"] == final_prediction]["Description"].values[0]

    return {
        "final_prediction": final_prediction,
        "precautions": precautions,
        "description": description
    }

# GUI
def get_input():
    if option_var.get() == "Symptom-Based Prediction":
        symptoms = input_entry.get()
        if symptoms:
            result = predictDisease(symptoms)
            if result:
                result_label.config(text=f"Prediction: {result['final_prediction']}\n"
                                         f"Description: {result['description']}\n"
                                         f"Precautions: {', '.join(result['precautions'])}")
        else:
            messagebox.showerror("Input Error", "Please enter symptoms.")
    elif option_var.get() == "Disease Details":
        # Fetch and display disease details logic here
        pass

# Main GUI
root = tk.Tk()
root.title("Disease Prediction System")
tk.Label(root, text="Welcome to the Disease Prediction System!", font=("Arial", 16)).pack(pady=20)

option_var = tk.StringVar(value="Symptom-Based Prediction")
tk.Label(root, text="Choose an option:").pack()
option_menu = tk.OptionMenu(root, option_var, "Symptom-Based Prediction", "Disease Details")
option_menu.pack()

tk.Label(root, text="Enter Symptoms (comma-separated):").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()

submit_button = tk.Button(root, text="Submit", command=get_input)
submit_button.pack()

result_label = tk.Label(root, text="", wraplength=400)
result_label.pack()

root.mainloop()
