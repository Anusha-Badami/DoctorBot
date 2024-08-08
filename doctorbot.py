# -*- coding: utf-8 -*-
"""Doctorbot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nztasZIW9HmJ4xLhQLzDDOgfs_JM6hy_
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import csv  # Corrected the import statement for CSV
from nltk.corpus import wordnet as wn  # Corrected the import statement for WordNet
import json
import io

# Creating an empty dictionary with "users" key
data = {"users": []}

# Writing the empty dictionary to a JSON file named 'DATA.json'
with open('DATA.json', 'w') as outfile:
    json.dump(data, outfile)

# Function to write new data to a JSON file
def write_json(new_data, filename="DATA.json"):
    with open(filename, 'r+') as file:
        file_data = json.load(file)  # Loading existing data from the file
        file_data["users"].append(new_data)  # Appending new data to the "users" key
        file.seek(0)  # Setting the file's current position at the beginning
        json.dump(file_data, file, indent=4)  # Writing back the updated data to the file

# Function to split a dataset into training and testing sets
def split_train_test(data, test_ratio):
    np.random.seed(42)  # Fixing the random seed for reproducibility
    shuffled_indices = np.random.permutation(len(data))
    test_set_size = int(len(data) * test_ratio)
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    return data.iloc[train_indices], data.loc[test_indices]



# Use the file upload widget to upload the file
from google.colab import files
uploaded = files.upload()

# Read the CSV file
dataset = pd.read_csv('doctorbot_test.csv')

# Splitting the dataset into training and testing sets using the previously defined function
df_tr, df_tt = split_train_test(dataset, 0.2)

# Displaying the first 10 rows of the training set
df_tr.head(10)

df_tr.shape

"""## **GET ALL SYMPTOMS**"""

# Getting all symptom columns from the training set
all_symp_col = list(df_tr.columns[:-1])

# Cleaning function to process individual symptoms
def clean_symp(sym):
    return sym.replace('', '').replace('.1', '').replace('(typhos)', '').replace('yellowish', 'yellow').replace('yellowing', 'yellow')

# Cleaning all symptoms using the clean_symp function
all_symp = [clean_symp(sym) for sym in all_symp_col]

import nltk
nltk.download('wordnet')

import nltk
from nltk.corpus import wordnet as wn


nltk.download('wordnet')

# Separating symptoms into two lists based on the presence of synsets in WordNet
ohne_syns = []
mit_syns = []

for sym in all_symp:
    if not wn.synsets(sym):
        ohne_syns.append(sym)  # Adding symptoms without synsets to ohne_syns list
    else:
        mit_syns.append(sym)   # Adding symptoms with synsets to mit_syns list

len(mit_syns)

len(ohne_syns)

"""## **PREPROCESS TEXT - ||**"""

# Importing necessary libraries
from spacy.lang.en.stop_words import STOP_WORDS
import spacy

# Loading spaCy English model
nlp = spacy.load('en_core_web_sm')

# Function for general text preprocessing
def preprocess(doc):
    nlp_doc = nlp(doc)
    d = []
    for token in nlp_doc:
        if (not token.text.lower() in STOP_WORDS and token.text.isalpha()):
            d.append(token.lemma_.lower())
    return ' '.join(d)

# Function for symptom-specific text preprocessing
def preprocess_sym(doc):
    nlp_doc = nlp(doc)
    d = []
    for token in nlp_doc:
        if (not token.text.lower() in STOP_WORDS and token.text.isalpha()):
            d.append(token.lemma_.lower())
    return '_'.join(d)

# Example of general text preprocessing
preprocess("skin peeling")

# Preprocessing all symptoms and creating a mapping between preprocessed and original symptoms
all_symp_pr = [preprocess_sym(sym) for sym in all_symp]
symptom_mapping = dict(zip(all_symp_pr, all_symp))

"""## **PREDICTION MODEL**"""

# Importing necessary libraries for classifiers and metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score

# Extracting features (X) and target labels (y) for training and testing sets
X_train = df_tr.iloc[:, :-1]
X_test = df_tt.iloc[:, :-1]
y_train = df_tr.iloc[:, -1]
y_test = df_tt.iloc[:, -1]

# Creating and training a k-Nearest Neighbors (KNN) classifier
knn_clf = KNeighborsClassifier()
knn_clf.fit(X_train, y_train)

# Making predictions on the test set using the trained KNN classifier
y_pred_knn = knn_clf.predict(X_test)

# Creating and training a Decision Tree classifier
dt_clf = DecisionTreeClassifier()
dt_clf.fit(X_train, y_train)

import random
import json

# Define the intents directly in the code
intents = {
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["Hi", "Hello", "Hey", "Greetings", "Good morning", "Good afternoon", "Good evening"],
      "responses": ["Hello! How can I assist you today?", "Hi there! How can I help you?"],
      "context": []
    },
    {
      "tag": "goodbye",
      "patterns": ["Goodbye", "Bye", "See you later", "Take care", "Farewell"],
      "responses": ["Goodbye! Have a great day.", "Bye! Take care."],
      "context": []
    },
    {
      "tag": "thanks",
      "patterns": ["Thank you", "Thanks a lot", "Appreciate it", "Thanks so much", "Thank you very much"],
      "responses": ["You're welcome!", "Happy to help!"],
      "context": []
    },
    {
      "tag": "health_issue",
      "patterns": ["I'm not feeling well", "I have a health issue", "I'm feeling sick", "I feel unwell", "I'm under the weather"],
      "responses": ["I'm sorry to hear that. Could you please provide more details about your symptoms?"],
      "context": []
    },
    {
      "tag": "symptom",
      "patterns": ["headache", "dizziness", "nausea", "mood changes", "fatigue", "blurred vision"],
      "responses": ["It sounds like you might be experiencing a migraine. It's best to consult a healthcare professional for advice."],
      "context": []
    },
    {
      "tag": "medication",
      "patterns": ["What medication should I take?", "recommend medication", "give prescription"],
      "responses": ["Bonine", "Benadryl"],
      "context": []
    },
    {
        "tag": "severe symptoms",
        "patterns": ["coldsweat", "chestpain"],
        "responses": ["It sounds like something severe. I would recommend you consult a doctor immediately."],
        "context": []
    }
  ]
}

# Function to get a response based on the input message
def get_response(message):
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            if pattern.lower() in message.lower():
                return random.choice(intent['responses'])
    return "I'm sorry, I don't understand. Could you please rephrase?"

# Main interaction loop
def chatbot():
    print("Chatbot: Hi! How can I help you today? (type 'exit' to end the conversation)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! Have a great day.")
            break
        response = get_response(user_input)
        print(f"Chatbot: {response}")

# Run the chatbot
chatbot()

