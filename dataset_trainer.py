import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

data_path = r"D:\yoga-main\HeartRate_SpO2_Dataset_15_25.xlsx"
df = pd.read_excel(data_path)

df = df.rename(columns={
    'Age Range': 'Age',
    'Heart Rate (bpm)': 'HeartRate',
    'SpO2 (%)': 'SpO2',
    'Health Status': 'Label' 
})

age_mapping = {
    '15-20 years': 17.5,  
    '21-25 years': 23    
}
df['Age'] = df['Age'].map(age_mapping)

if df.isnull().values.any():
    print("Warning: Missing values detected! Check the dataset.")
    df = df.dropna()  

X = df[['Age', 'HeartRate', 'SpO2']]
y = df['Label']

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "yoga_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("Model trained and saved successfully!")
