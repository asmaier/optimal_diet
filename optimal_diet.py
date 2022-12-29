import re

import streamlit as st
import pandas as pd

from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit

# https://stackoverflow.com/questions/18172851/deleting-dataframe-row-in-pandas-based-on-column-value
def filter_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]

def replace_unit_with_percent(column_name):
    return re.sub(r"\((.*)\)", "(%)", column_name)

# st.set_page_config(layout="wide")
st.title("Optimal diet")

df_foods=pd.read_csv("ciqual_2020.csv")

# remove certain foods

remove_foods = ["Acerola. pulp. raw. sampled in the island of La Martiniqu", 
                "Egg. powder", 
                "Milk. powder. semi-skimmed", 
                "Decaffeinated coffee. powder. instant",
                "Decaffeinated not instant coffee. without sugar. ready-to-drink",
                "Espresso coffee. not instant coffee. without sugar. ready-to-drink",
                "Not instant coffee. without sugar. ready-to-drink",
                "Tea. brewed. without sugar",
                "Royal jelly", 
                "Cocoa powder for baby beverage", 
                "Egg white. powder", 
                "Milk. powder. skimmed", 
                "Instant cereal (powder to be reconstituted) for baby from 4/6 month",
                "Milk. powder. whole",
                "Instant cereal (powder to be reconstituted) for baby from 6 months",
                "Egg yolk. powder", 
                "Gelatine. dried", 
                "Baby milk. first age. powd",
                "Baby milk. second age. powd",
                "Soya flour", 
                "Sea belt (Saccharina latissima). dried or dehydrated", 
                "Veal stock for sauce and cooking. dehydrated", 
                "Broth. stock or bouillon. meat and vegetables. with fat. dehydrated", 
                "Broth. stock or bouillon. meat and vegetables. defatted. dehydrated",
                "Broth. stock or bouillon. beef. dehydrated",
                "Madeira wine aspic. dehydrated", 
                "Nutritional yeast", 
                "Chewing gum. without sug", 
                "Chewing gum. sugar level unknown (average)",
                "Baking powder or raising agen", 
                "Prepared mixed meat/fish canned. salad", 
                "Stevia sweeten"]

df_foods_filtered = filter_rows_by_values(df_foods, "Name", remove_foods)

commodities = list(df_foods_filtered["Name"])

data = df_foods_filtered.drop(["Group", "Subgroup", "Subsubgroup", "Name"], axis=1).values.tolist()

# Nutrient minimums.
df_nutrients = pd.read_csv("rdi.csv")
nut_default = [[key,value] for key,value in df_nutrients.to_dict("records")[0].items()]

nut_user = []
with st.sidebar:
    st.subheader("Nutrient minimums")
    for nutrient in nut_default:
        nut_user.append(st.text_input(nutrient[0],nutrient[1]))

nutrients = [[nutrient[0], float(nut_user[i])] for i, nutrient in enumerate(nut_default)]

st.subheader("Minimization goal")
goal_options = {1:"mass (gramm)", 2:"calories (kcal)"}
goal = st.radio(label="Minimize", options=[1,2], format_func=lambda x: goal_options.get(x))

if goal == 2:
    # ignore calories restriction
    nutrients[0] = ["Energy (kcal/d)", 0.0]

    # remove foods with no calories
    df_foods_filtered2 = df_foods_filtered[df_foods_filtered["Energy (kcal/100g)"] > 0.0]
    commodities = list(df_foods_filtered2["Name"])
    data = df_foods_filtered2.drop("Name", axis=1).values.tolist()


# Create the linear solver with the GLOP (the Google Linear Optimization Package) backend (advanced simplex)
# see https://en.wikipedia.org/wiki/GLOP
solver = pywraplp.Solver.CreateSolver('GLOP')

# Declare an array to hold our variables. 
foods = [solver.NumVar(0.0, solver.infinity(), item) for item in commodities]

#print('Number of variables =', solver.NumVariables())

# Create the constraints, one per nutrient. (data = nutrients_per_dollar)
constraints = []
for i, nutrient in enumerate(nutrients):
    constraints.append(solver.Constraint(nutrient[1], solver.infinity(), nutrient[0]))
    for j, item in enumerate(data):
        constraints[i].SetCoefficient(foods[j], item[i])

# print('Number of constraints =', solver.NumConstraints())

# Objective function: Minimize the sum of goals per foods.
objective = solver.Objective()
for i, food in enumerate(foods):
    # default value for prize optimization
    nutrient_per_goal = 1  
    if goal > 1:
        nutrient_per_goal = data[i][0]    
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
        # default value for weight optimization
        nutrient_per_goal = 100  
        if goal > 1:
            nutrient_per_goal = data[i][0]

        food_per_day.append((commodities[i], food.solution_value() * nutrient_per_goal))
        # st.write('{}: ${} {} gr'.format(commodities[i][0], food.solution_value(), food.solution_value() * data[i][1]))
        for j, _ in enumerate(nutrients):
            nutrients_result[j] += data[i][j] * food.solution_value()

df_food_per_day = pd.DataFrame(food_per_day, columns=("food", goal_options.get(goal))) 
st.table(df_food_per_day.style.format("{:.4f}", subset=df_food_per_day.select_dtypes(float).columns))  

minimum = objective.Value() * 100
if goal > 1:
    minimum = objective.Value()
st.write('\nTotal minimum daily {}: {:.4f}'.format(goal_options.get(goal), minimum))  

st.subheader('Nutrients per day')

nut_per_day=[]

for i, nutrient in enumerate(nutrients):
    nut_per_day.append((nutrient[0], nutrient[1], nutrients_result[i], nutrients_result[i]/nutrient[1]*100 if nutrient[1] else float("nan") ))

df_nut_per_day = pd.DataFrame(nut_per_day, columns=("nutrient", "min", "total", "%"))
st.table(df_nut_per_day.style.format("{:.2f}", subset=df_nut_per_day.select_dtypes(float).columns))

#st.write('{}: {:.2f} (min {})'.format(nutrient[0], nutrients_result[i],nutrient[1]))

st.subheader('Nutrients per food in percent')
nutrient_per_food = {}

for i, food in enumerate(foods):
    if food.solution_value() > 0.0:      
        for j, nutrient in enumerate(nutrients):
            if food in nutrient_per_food:
                nutrient_per_food[food].append(data[i][j] * food.solution_value())
            else:
                nutrient_per_food[food]=[data[i][j] * food.solution_value()]

columns = [replace_unit_with_percent(n[0]) for n in nutrients]

foods_df = pd.DataFrame.from_dict(nutrient_per_food, orient='index', columns=columns)

for i, column in enumerate(columns):
    foods_df[column]=foods_df[column]/nutrients_result[i]*100

st.table(foods_df.style.format("{:.2f}"))                                       