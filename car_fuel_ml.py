# -*- coding: utf-8 -*-
"""Car_fuel_ml.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o7514LY2lFR6Me_JvcvZJ4YIoAwPKpdQ

# import libraries
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsClassifier

"""#read data"""

car_features=pd.read_json(r"/content/car.json")

car_features

car_features.isnull().sum()

"""* there is no null values

# feature description

1.**mpg**:
Miles Per Gallon. This column represents the fuel efficiency of the car, indicating how many miles the car can travel on one gallon of fuel.

2.**cyl**:
Cylinders. This indicates the number of cylinders in the car's engine. More cylinders typically imply more power, but may also lead to higher fuel consumption.

3.**disp:**
Displacement. This refers to the total volume of all the cylinders in the engine, usually measured in cubic inches (cu in) or liters. It gives an indication of the engine's size and power.

4.**hp:**
Horsepower. This column represents the power output of the car's engine. It measures how much work the engine can perform over time.

5.**wt:**
Weight. This refers to the weight of the car, typically measured in pounds (lbs). Heavier cars may have different performance characteristics compared to lighter ones.

6.**acc:**
Acceleration. This generally measures the time it takes for the car to go from 0 to 60 miles per hour. It is often expressed in seconds.

7.**yr:**
Year. This indicates the model year of the car, usually represented in the last two digits (e.g., '70' corresponds to 1970).

8.**origin:**
Origin. This column typically indicates the origin of the car, often represented by numerical codes:
1: American-made
2: European-made
3: Asian-

9.**car name**

#### Data concatenation
"""

car_names = pd.read_csv('/content/Car name.csv', header=None, names=["Car Name"])

# Remove the first element from car names (which it was car_name)
car_names = car_names.drop(0).reset_index(drop=True)
# Reset the index for the car features to match the modified car names
car_features = car_features.reset_index(drop=True)
merged_data = pd.concat([car_names, car_features], axis=1)

merged_data.head()

(merged_data == '?').sum()

merged_data.replace('?', np.nan, inplace=True)
merged_data['hp'] = pd.to_numeric(merged_data['hp'], errors='coerce')
merged_data['hp'].fillna(merged_data['hp'].median(), inplace=True)

(merged_data == '?').sum()

merged_data['power_to_weight'] = merged_data['hp'] / merged_data['wt']

"""* Power-to-weight is a well-known metric in automotive engineering
* using hp (horsepower) and wt (weight) separately may not fully capture their combined impact on fuel consumption. By creating the power-to-weight ratio, we create a new feature that might highlight how these two factors work together to influence fuel efficiency
* Instead of feeding both hp and wt into the model, combining them into one feature reduces the complexity and can make the model more interpretable while retaining the most relevant information

"""

numerical_features = [
    'disp',
    'power_to_weight',
    'hp',
    'wt',
]
categorical_features = [
'cyl',
'origin'
]

scaler = StandardScaler()
# Apply standardization
merged_data[numerical_features] = scaler.fit_transform(merged_data[numerical_features])

merged_data

"""# EDA"""

sns.pairplot(merged_data[['mpg', 'disp', 'hp', 'wt', 'power_to_weight','acc']])

"""* hp is direcly propotional relationship with wt,power_to_weight,disp and inversily propotional relationship with mpg which means the more hp vecheils the less mpg consmuption
* dsip is directly propotional relationship with wt, hp and inversly with mpg
* mpg is inversly propotional with all features
* mpg only directly proption with acc which mean when acc increases the mpg increases
"""

sns.heatmap(merged_data[['mpg', 'disp', 'hp', 'wt', 'power_to_weight']].corr(), annot=True)

"""# KMean cluster"""

kmeans = KMeans(n_clusters=3, random_state=42)
merged_data['cluster'] = kmeans.fit_predict(merged_data[numerical_features])

merged_data

"""* the cars are clustered in 3 groups"""

sns.scatterplot(x='hp', y='mpg', hue='cluster', data=merged_data, palette='Set1')

sns.scatterplot(x='wt', y='mpg', hue='cluster', data=merged_data, palette='Set1')

sns.scatterplot(x='power_to_weight', y='mpg', hue='cluster', data=merged_data, palette='Set1')

sns.scatterplot(x='acc', y='mpg', hue='cluster', data=merged_data, palette='Set1')

sns.scatterplot(x='disp', y='mpg', hue='cluster', data=merged_data, palette='Set1')

"""# Superivised prediction"""

X = merged_data[['disp', 'hp', 'wt', 'power_to_weight']]
y = merged_data['mpg']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""# Prediction on linear regression"""

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Visualize the regression results
plt.scatter(y_test, y_pred)
plt.xlabel('True MPG')
plt.ylabel('Predicted MPG')
plt.title('True vs Predicted MPG')
plt.show()

"""# Evaluation"""

def evaluate_model(predictions, y_test):
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, predictions, average='macro')
    return precision, recall, f1

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(random_state=42),
    "Support Vector Regressor (SVR)": SVR()
}

def evaluate_model(name, model, X_test, y_test, y_pred):
    mse = mean_squared_error(y_test, y_pred)
    print(f"{name} Results:")
    print(f"Mean Squared Error: {mse}")
    # Plot True vs Predicted values
    plt.scatter(y_test, y_pred)
    plt.xlabel('True MPG')
    plt.ylabel('Predicted MPG')
    plt.title(f'{name}: True vs Predicted MPG')
    plt.show()

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    evaluate_model(name, model, X_test, y_test, y_pred)

