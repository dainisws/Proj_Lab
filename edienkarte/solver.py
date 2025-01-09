# Modelis nav pielāgots/testēts uz īstas datu kopas

from scipy.optimize import minimize
import numpy as np

prices = np.array([5.29, 2.69, 7.99]) / 1000 # price per gram
tastes = np.array([5, 7, 10]) # iespējams, ka vajadzētu normalizēt starp cenām (1 - zemākā cena, 10 - augstākā cena)
times = np.array([0, 30, 30])
calories = np.array([200, 300, 300]) / 100 # calories per gram
fat = np.array([5.2, 11.1, 11.1]) / 100
protein = np.array([5.2, 11.1, 11.1]) / 100
carbs = np.array([5.2, 11.1, 11.1]) / 100

def objective_function(variables):
    totalPrice = np.sum(variables*prices)
    totalTaste = np.sum(variables*tastes)
    w1 = 0
    w2 = 1
    return totalPrice*w1-totalTaste*w2

def constraint_min_time(variables):
    return np.where(variables > times, times, 0).sum()

def constraint_max_time(variables):
    maxTime = 180
    return maxTime - np.where(variables > times, times, 0).sum()

def constraint_min_calories(variables):
    minCalories = 2000
    totalCalories = np.sum(variables*calories)
    return totalCalories - minCalories

def constraint_max_calories(variables):
    maxCalories = 2700
    totalCalories = np.sum(variables*calories)
    return maxCalories - totalCalories

def constraint_min_fat(variables):
    minFat = 40
    totalFat = np.sum(variables*fat)
    return totalFat - minFat

def constraint_max_fat(variables):
    maxFat = 100
    totalFat = np.sum(variables*fat)
    return maxFat - totalFat

def constraint_min_protein(variables):
    minProtein = 100
    totalProtein = np.sum(variables*protein)
    return totalProtein - minProtein

def constraint_max_protein(variables):
    maxProtein = 200
    totalProtein = np.sum(variables*protein)
    return maxProtein - totalProtein

def constraint_min_carbs(variables):
    minCarbs = 100
    totalCarbs = np.sum(variables*carbs)
    return totalCarbs - minCarbs

def constraint_max_carbs(variables):
    maxCarbs = 300
    totalCarbs = np.sum(variables*carbs)
    return maxCarbs - totalCarbs

constraints = (
    {'type': 'ineq', 'fun': constraint_min_time},
    {'type': 'ineq', 'fun': constraint_max_time},
    {'type': 'ineq', 'fun': constraint_min_calories},
    {'type': 'ineq', 'fun': constraint_max_calories},
    {'type': 'ineq', 'fun': constraint_min_fat},
    {'type': 'ineq', 'fun': constraint_max_fat},
    {'type': 'ineq', 'fun': constraint_min_protein},
    {'type': 'ineq', 'fun': constraint_max_protein},
    {'type': 'ineq', 'fun': constraint_min_carbs},
    {'type': 'ineq', 'fun': constraint_max_carbs}
)

def solve(arr):
    initial_guess = [1] * 3 # 3 ir produktu skaits
    bounds = [(0, None)] * 3 # 3 ir produktu skaits
    result = minimize(objective_function, initial_guess, constraints=constraints, bounds=bounds, method = "SLSQP")
    # return input array and append results at the end
    # result.x // grams