import re

import streamlit as st
import pandas as pd

from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit


def replace_unit_with_percent(column_name):
    return re.sub(r"\((.*)\)", "(%)", column_name)

st.title("Optimal diet (for 1939)")

# new data table from https://github.com/google/or-tools/blob/82750ac12f1ee5354e1c7869894d9af3508778f2/examples/contrib/stigler_contrib.py

commodities = [["Wheat Flour (Enriched)", "10 lb."], ["Macaroni", "1 lb."],
                 ["Wheat Cereal (Enriched)",
                  "28 oz."], ["Corn Flakes", "8 oz."], ["Corn Meal", "1 lb."],
                 ["Hominy Grits", "24 oz."], ["Rice", "1 lb."],
                 ["Rolled Oats", "1 lb."], ["White Bread (Enriched)", "1 lb."],
                 ["Whole Wheat Bread", "1 lb."], ["Rye Bread", "1 lb."],
                 ["Pound Cake", "1 lb."], ["Soda Crackers", "1 lb."],
                 ["Milk", "1 qt."], ["Evaporated Milk (can)", "14.5 oz."],
                 ["Butter", "1 lb."], ["Oleomargarine", "1 lb."],
                 ["Eggs", "1 doz."], ["Cheese (Cheddar)", "1 lb."],
                 ["Cream", "1/2 pt."], ["Peanut Butter", "1 lb."],
                 ["Mayonnaise", "1/2 pt."], ["Crisco", "1 lb."],
                 ["Lard", "1 lb."], ["Sirloin Steak", "1 lb."],
                 ["Round Steak", "1 lb."], ["Rib Roast", "1 lb."],
                 ["Chuck Roast", "1 lb."], ["Plate", "1 lb."],
                 ["Liver (Beef)", "1 lb."], ["Leg of Lamb", "1 lb."],
                 ["Lamb Chops (Rib)", "1 lb."], ["Pork Chops", "1 lb."],
                 ["Pork Loin Roast", "1 lb."], ["Bacon", "1 lb."],
                 ["Ham - smoked", "1 lb."], ["Salt Pork", "1 lb."],
                 ["Roasting Chicken", "1 lb."], ["Veal Cutlets", "1 lb."],
                 ["Salmon, Pink (can)", "16 oz."], ["Apples", "1 lb."],
                 ["Bananas", "1 lb."], ["Lemons", "1 doz."],
                 ["Oranges", "1 doz."], ["Green Beans", "1 lb."],
                 ["Cabbage", "1 lb."], ["Carrots", "1 bunch"],
                 ["Celery", "1 stalk"], ["Lettuce", "1 head"],
                 ["Onions", "1 lb."], ["Potatoes", "15 lb."],
                 ["Spinach", "1 lb."], ["Sweet Potatoes", "1 lb."],
                 ["Peaches (can)", "No. 2 1/2"], ["Pears (can)", "No. 2 1/2,"],
                 ["Pineapple (can)", "No. 2 1/2"], ["Asparagus (can)", "No. 2"],
                 ["Grean Beans (can)", "No. 2"],
                 ["Pork and Beans (can)", "16 oz."], ["Corn (can)", "No. 2"],
                 ["Peas (can)", "No. 2"], ["Tomatoes (can)", "No. 2"],
                 ["Tomato Soup (can)", "10 1/2 oz."],
                 ["Peaches, Dried", "1 lb."], ["Prunes, Dried", "1 lb."],
                 ["Raisins, Dried", "15 oz."], ["Peas, Dried", "1 lb."],
                 ["Lima Beans, Dried", "1 lb."], ["Navy Beans, Dried", "1 lb."],
                 ["Coffee", "1 lb."], ["Tea", "1/4 lb."], ["Cocoa", "8 oz."],
                 ["Chocolate", "8 oz."], ["Sugar", "10 lb."],
                 ["Corn Sirup", "24 oz."], ["Molasses", "18 oz."],
                 ["Strawberry Preserve", "1 lb."]]

# price and weight are the two first columns
data = [
  [36.0, 12600.0, 44.7, 1411.0, 2.0, 365.0, 0.0, 55.4, 33.3, 441.0, 0.0],
  [14.1, 3217.0, 11.6, 418.0, 0.7, 54.0, 0.0, 3.2, 1.9, 68.0, 0.0],
  [24.2, 3280.0, 11.8, 377.0, 14.4, 175.0, 0.0, 14.4, 8.8, 114.0, 0.0],
  [7.1, 3194.0, 11.4, 252.0, 0.1, 56.0, 0.0, 13.5, 2.3, 68.0, 0.0],
  [4.6, 9861.0, 36.0, 897.0, 1.7, 99.0, 30.9, 17.4, 7.9, 106.0, 0.0],
  [8.5, 8005.0, 28.6, 680.0, 0.8, 80.0, 0.0, 10.6, 1.6, 110.0, 0.0],
  [7.5, 6048.0, 21.2, 460.0, 0.6, 41.0, 0.0, 2.0, 4.8, 60.0, 0.0],
  [7.1, 6389.0, 25.3, 907.0, 5.1, 341.0, 0.0, 37.1, 8.9, 64.0, 0.0],
  [7.9, 5742.0, 15.6, 488.0, 2.5, 115.0, 0.0, 13.8, 8.5, 126.0, 0.0],
  [9.1, 4985.0, 12.2, 484.0, 2.7, 125.0, 0.0, 13.9, 6.4, 160.0, 0.0],
  [9.2, 4930.0, 12.4, 439.0, 1.1, 82.0, 0.0, 9.9, 3.0, 66.0, 0.0],
  [24.8, 1829.0, 8.0, 130.0, 0.4, 31.0, 18.9, 2.8, 3.0, 17.0, 0.0],
  [15.1, 3004.0, 12.5, 288.0, 0.5, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [11.0, 8867.0, 6.1, 310.0, 10.5, 18.0, 16.8, 4.0, 16.0, 7.0, 177.0],
  [6.7, 6035.0, 8.4, 422.0, 15.1, 9.0, 26.0, 3.0, 23.5, 11.0, 60.0],
  [20.8, 1473.0, 10.8, 9.0, 0.2, 3.0, 44.2, 0.0, 0.2, 2.0, 0.0],
  [16.1, 2817.0, 20.6, 17.0, 0.6, 6.0, 55.8, 0.2, 0.0, 0.0, 0.0],
  [32.6, 1857.0, 2.9, 238.0, 1.0, 52.0, 18.6, 2.8, 6.5, 1.0, 0.0],
  [24.2, 1874.0, 7.4, 448.0, 16.4, 19.0, 28.1, 0.8, 10.3, 4.0, 0.0],
  [14.1, 1689.0, 3.5, 49.0, 1.7, 3.0, 16.9, 0.6, 2.5, 0.0, 17.0],
  [17.9, 2534.0, 15.7, 661.0, 1.0, 48.0, 0.0, 9.6, 8.1, 471.0, 0.0],
  [16.7, 1198.0, 8.6, 18.0, 0.2, 8.0, 2.7, 0.4, 0.5, 0.0, 0.0],
  [20.3, 2234.0, 20.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [9.8, 4628.0, 41.7, 0.0, 0.0, 0.0, 0.2, 0.0, 0.5, 5.0, 0.0],
  [39.6, 1145.0, 2.9, 166.0, 0.1, 34.0, 0.2, 2.1, 2.9, 69.0, 0.0],
  [36.4, 1246.0, 2.2, 214.0, 0.1, 32.0, 0.4, 2.5, 2.4, 87.0, 0.0],
  [29.2, 1553.0, 3.4, 213.0, 0.1, 33.0, 0.0, 0.0, 2.0, 0.0, 0.0],
  [22.6, 2007.0, 3.6, 309.0, 0.2, 46.0, 0.4, 1.0, 4.0, 120.0, 0.0],
  [14.6, 3107.0, 8.5, 404.0, 0.2, 62.0, 0.0, 0.9, 0.0, 0.0, 0.0],
  [26.8, 1692.0, 2.2, 333.0, 0.2, 139.0, 169.2, 6.4, 50.8, 316.0, 525.0],
  [27.6, 1643.0, 3.1, 245.0, 0.1, 20.0, 0.0, 2.8, 3.0, 86.0, 0.0],
  [36.6, 1239.0, 3.3, 140.0, 0.1, 15.0, 0.0, 1.7, 2.7, 54.0, 0.0],
  [30.7, 1477.0, 3.5, 196.0, 0.2, 80.0, 0.0, 17.4, 2.7, 60.0, 0.0],
  [24.2, 1874.0, 4.4, 249.0, 0.3, 37.0, 0.0, 18.2, 3.6, 79.0, 0.0],
  [25.6, 1772.0, 10.4, 152.0, 0.2, 23.0, 0.0, 1.8, 1.8, 71.0, 0.0],
  [27.4, 1655.0, 6.7, 212.0, 0.2, 31.0, 0.0, 9.9, 3.3, 50.0, 0.0],
  [16.0, 2835.0, 18.8, 164.0, 0.1, 26.0, 0.0, 1.4, 1.8, 0.0, 0.0],
  [30.3, 1497.0, 1.8, 184.0, 0.1, 30.0, 0.1, 0.9, 1.8, 68.0, 46.0],
  [42.3, 1072.0, 1.7, 156.0, 0.1, 24.0, 0.0, 1.4, 2.4, 57.0, 0.0],
  [13.0, 3489.0, 5.8, 705.0, 6.8, 45.0, 3.5, 1.0, 4.9, 209.0, 0.0],
  [4.4, 9072.0, 5.8, 27.0, 0.5, 36.0, 7.3, 3.6, 2.7, 5.0, 544.0],
  [6.1, 4982.0, 4.9, 60.0, 0.4, 30.0, 17.4, 2.5, 3.5, 28.0, 498.0],
  [26.0, 2380.0, 1.0, 21.0, 0.5, 14.0, 0.0, 0.5, 0.0, 4.0, 952.0],
  [30.9, 4439.0, 2.2, 40.0, 1.1, 18.0, 11.1, 3.6, 1.3, 10.0, 1993.0],
  [7.1, 5750.0, 2.4, 138.0, 3.7, 80.0, 69.0, 4.3, 5.8, 37.0, 862.0],
  [3.7, 8949.0, 2.6, 125.0, 4.0, 36.0, 7.2, 9.0, 4.5, 26.0, 5369.0],
  [4.7, 6080.0, 2.7, 73.0, 2.8, 43.0, 188.5, 6.1, 4.3, 89.0, 608.0],
  [7.3, 3915.0, 0.9, 51.0, 3.0, 23.0, 0.9, 1.4, 1.4, 9.0, 313.0],
  [8.2, 2247.0, 0.4, 27.0, 1.1, 22.0, 112.4, 1.8, 3.4, 11.0, 449.0],
  [3.6, 11844.0, 5.8, 166.0, 3.8, 59.0, 16.6, 4.7, 5.9, 21.0, 1184.0],
  [34.0, 16810.0, 14.3, 336.0, 1.8, 118.0, 6.7, 29.4, 7.1, 198.0, 2522.0],
  [8.1, 4592.0, 1.1, 106.0, 0.0, 138.0, 918.4, 5.7, 13.8, 33.0, 2755.0],
  [5.1, 7649.0, 9.6, 138.0, 2.7, 54.0, 290.7, 8.4, 5.4, 83.0, 1912.0],
  [16.8, 4894.0, 3.7, 20.0, 0.4, 10.0, 21.5, 0.5, 1.0, 31.0, 196.0],
  [20.4, 4030.0, 3.0, 8.0, 0.3, 8.0, 0.8, 0.8, 0.8, 5.0, 81.0],
  [21.3, 3993.0, 2.4, 16.0, 0.4, 8.0, 2.0, 2.8, 0.8, 7.0, 399.0],
  [27.7, 1945.0, 0.4, 33.0, 0.3, 12.0, 16.3, 1.4, 2.1, 17.0, 272.0],
  [10.0, 5386.0, 1.0, 54.0, 2.0, 65.0, 53.9, 1.6, 4.3, 32.0, 431.0],
  [7.1, 6389.0, 7.5, 364.0, 4.0, 134.0, 3.5, 8.3, 7.7, 56.0, 0.0],
  [10.4, 5452.0, 5.2, 136.0, 0.2, 16.0, 12.0, 1.6, 2.7, 42.0, 218.0],
  [13.8, 4109.0, 2.3, 136.0, 0.6, 45.0, 34.9, 4.9, 2.5, 37.0, 370.0],
  [8.6, 6263.0, 1.3, 63.0, 0.7, 38.0, 53.2, 3.4, 2.5, 36.0, 1253.0],
  [7.6, 3917.0, 1.6, 71.0, 0.6, 43.0, 57.9, 3.5, 2.4, 67.0, 862.0],
  [15.7, 2889.0, 8.5, 87.0, 1.7, 173.0, 86.8, 1.2, 4.3, 55.0, 57.0],
  [9.0, 4284.0, 12.8, 99.0, 2.5, 154.0, 85.7, 3.9, 4.3, 65.0, 257.0],
  [9.4, 4524.0, 13.5, 104.0, 2.5, 136.0, 4.5, 6.3, 1.4, 24.0, 136.0],
  [7.9, 5742.0, 20.0, 1367.0, 4.2, 345.0, 2.9, 28.7, 18.4, 162.0, 0.0],
  [8.9, 5097.0, 17.4, 1055.0, 3.7, 459.0, 5.1, 26.9, 38.2, 93.0, 0.0],
  [5.9, 7688.0, 26.9, 1691.0, 11.4, 792.0, 0.0, 38.4, 24.6, 217.0, 0.0],
  [22.4, 2025.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.1, 50.0, 0.0],
  [17.4, 652.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.3, 42.0, 0.0],
  [8.6, 2637.0, 8.7, 237.0, 3.0, 72.0, 0.0, 2.0, 11.9, 40.0, 0.0],
  [16.2, 1400.0, 8.0, 77.0, 1.3, 39.0, 0.0, 0.9, 3.4, 14.0, 0.0],
  [51.7, 8773.0, 34.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  [13.7, 4996.0, 14.7, 0.0, 0.5, 74.0, 0.0, 0.0, 0.0, 5.0, 0.0],
  [13.6, 3752.0, 9.0, 0.0, 10.3, 244.0, 0.0, 1.9, 7.5, 146.0, 0.0],
  [20.5, 2213.0, 6.4, 11.0, 0.4, 7.0, 0.2, 0.2, 0.4, 3.0, 0.0]
]



# Nutrient minimums.
nut_default = [['Calories (1000 kcal)', 3], ['Protein (g)', 70], [
    'Calcium (g)', 0.8
], ['Iron (mg)', 12], ['Vitamin A (KIU)', 5], ['Vitamin B1 (mg)', 1.8],
             ['Vitamin B2 (mg)', 2.7], ['Niacin (mg)',
                                        18], ['Vitamin C (mg)', 75]]
with st.sidebar:
    st.subheader("Nutrient minimums")
    calories = st.text_input(nut_default[0][0],nut_default[0][1])
    protein = st.text_input(nut_default[1][0],nut_default[1][1])
    calcium = st.text_input(nut_default[2][0],nut_default[2][1])
    iron = st.text_input(nut_default[3][0],nut_default[3][1])
    a = st.text_input(nut_default[4][0],nut_default[4][1])
    b1 = st.text_input(nut_default[5][0],nut_default[5][1])
    b2 = st.text_input(nut_default[6][0],nut_default[6][1])
    b3 = st.text_input(nut_default[7][0],nut_default[7][1])
    c = st.text_input(nut_default[8][0],nut_default[8][1])

nutrients = [['Calories (kcal)', float(calories)], 
['Protein (g)', float(protein)], 
['Calcium (g)', float(calcium)], 
['Iron (mg)', float(iron)], 
['Vitamin A (KIU)', float(a)], 
['Vitamin B1 (mg)', float(b1)],
['Vitamin B2 (mg)', float(b2)], 
['Niacin (mg)', float(b3)], 
['Vitamin C (mg)', float(c)]]

st.subheader("Minimization goal")
goal_options = {0:"prize ($)", 1:"mass (gramm)", 2:"calories (1000 kcal)"}
goal = st.radio(label="Minimize", options=[0,2,1], format_func=lambda x: goal_options.get(x))

# Create the linear solver with the GLOP (the Google Linear Optimization Package) backend (advanced simplex)
# see https://en.wikipedia.org/wiki/GLOP
solver = pywraplp.Solver.CreateSolver('GLOP')

# Declare an array to hold our variables. 
foods = [solver.NumVar(0.0, solver.infinity(), item[0]) for item in commodities]

#print('Number of variables =', solver.NumVariables())

# Create the constraints, one per nutrient. (data = nutrients_per_dollar)
constraints = []
for i, nutrient in enumerate(nutrients):
    constraints.append(solver.Constraint(nutrient[1], solver.infinity()))
    for j, item in enumerate(data):
        constraints[i].SetCoefficient(foods[j], item[i + 2])

# print('Number of constraints =', solver.NumConstraints())

# Objective function: Minimize the sum of goals per foods.
objective = solver.Objective()
for i, food in enumerate(foods):
    # default value for prize optimization
    nutrient_per_goal = 1  
    if goal > 0:
        nutrient_per_goal = data[i][goal]
    objective.SetCoefficient(food, nutrient_per_goal)
objective.SetMinimization()

status = solver.Solve()

# Check that the problem has an optimal solution.
if status != solver.OPTIMAL:
    print('The problem does not have an optimal solution!')
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')
        exit(1)

# Display the amounts (in dollars) to purchase of each food.
nutrients_result = [0] * len(nutrients)
st.subheader('Daily Foods:')

food_per_day=[]

for i, food in enumerate(foods):
    if food.solution_value() > 0.0:
        # default value for prize optimization
        nutrient_per_goal = 1  
        if goal > 0:
            nutrient_per_goal = data[i][goal]

        food_per_day.append((commodities[i][0], food.solution_value() * nutrient_per_goal))
        # st.write('{}: ${} {} gr'.format(commodities[i][0], food.solution_value(), food.solution_value() * data[i][1]))
        for j, _ in enumerate(nutrients):
            nutrients_result[j] += data[i][j + 2] * food.solution_value()

df_food_per_day = pd.DataFrame(food_per_day, columns=("food", goal_options.get(goal))) 
st.table(df_food_per_day)  

st.write('\nTotal minimum daily {}: {:.4f}'.format(goal_options.get(goal),objective.Value()))  

st.subheader('Nutrients per day')

nut_per_day=[]

for i, nutrient in enumerate(nutrients):
    nut_per_day.append((nutrient[0], nutrient[1], nutrients_result[i], nutrients_result[i]/nutrient[1]*100 if nutrient[1] else float("nan") ))

df_nut_per_day = pd.DataFrame(nut_per_day, columns=("nutrient", "min", "total", "%"))
st.table(df_nut_per_day)

#st.write('{}: {:.2f} (min {})'.format(nutrient[0], nutrients_result[i],nutrient[1]))

st.subheader('Nutrients per food in percent')
nutrient_per_food = {}

for i, food in enumerate(foods):
    if food.solution_value() > 0.0:      
        for j, nutrient in enumerate(nutrients):
            if food in nutrient_per_food:
                nutrient_per_food[food].append(data[i][j + 2] * food.solution_value())
            else:
                nutrient_per_food[food]=[data[i][j + 2] * food.solution_value()]

columns = [replace_unit_with_percent(n[0]) for n in nutrients]

df_foods = pd.DataFrame.from_dict(nutrient_per_food, orient='index', 
    columns=columns)

for i, column in enumerate(columns):
    df_foods[column]=(df_foods[column]/nutrients_result[i]*100).round(2)

st.table(df_foods)                                       