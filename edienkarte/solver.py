# Modelis nav pielāgots/testēts uz īstas datu kopas

from scipy.optimize import minimize
import numpy as np
from functools import partial

class SolverModel():
    minCalories = 2000
    maxCalories = 4000
    minFat = 0
    maxFat = 1000
    minProtein = 0
    maxProtein = 1000
    minCarbs = 0
    maxCarbs = 1000
    weightTaste = 0.5
    weightPrice = 0.5
    size = 3

    id = np.array([1, 2, 3])
    prices = np.array([5.29, 2.69, 7.99]) / 1000 # price per gram
    tastes = np.array([5, 7, 10]) # iespējams, ka vajadzētu normalizēt starp cenām (1 - zemākā cena, 10 - augstākā cena)
    calories = np.array([200, 300, 300]) / 100 # calories per gram
    fat = np.array([5.2, 11.1, 11.1]) / 100
    protein = np.array([5.2, 11.1, 11.1]) / 100
    carbs = np.array([5.2, 11.1, 11.1]) / 100
    names = np.array(["1", "2", "3"])
    links = np.array(["#", "#", "#"])

    def __init__(self, minCalories, maxCalories, minFat, maxFat, minProtein, maxProtein, minCarbs, maxCarbs, weightTaste, weightPrice, arr, totalCalories, totalFat, totalProtein, totalCarbs):
        self.minCalories = float(max(0.0, minCalories - totalCalories))
        self.maxCalories = float(max(0.0, maxCalories - totalCalories))
        self.minFat = float(max(0.0, minFat - totalFat))
        self.maxFat = float(max(0.0, maxFat - totalFat))
        self.minProtein = float(max(0.0, minProtein - totalProtein))
        self.maxProtein = float(max(0.0, maxProtein - totalProtein))
        self.minCarbs = float(max(0.0, minCarbs - totalCarbs))
        self.maxCarbs = float(max(0.0, maxCarbs - totalCarbs))
        self.weightTaste = float(weightTaste)
        self.weightPrice = float(weightPrice)
        self.id = np.array([item[0] for item in arr])
        self.prices = np.array([item[1] for item in arr]) / 1000
        self.tastes = np.array([item[2] for item in arr])

        # Garšas normalizācija pret cenu
        min_taste = np.min(self.tastes)
        max_taste = np.max(self.tastes)
        if (max_taste - min_taste) != 0:
            min_price = np.min(self.prices) * 1000
            max_price = np.max(self.prices) * 1000
            self.tastes = min_price + ((self.tastes - min_taste) / (max_taste - min_taste)) * (max_price - min_price)
        else:
            self.tastes = np.full_like(self.tastes, np.average(self.prices) * 1000)

        self.calories = np.array([item[3] for item in arr]) / 100
        self.fat = np.array([item[4] for item in arr]) / 100
        self.protein = np.array([item[5] for item in arr]) / 100
        self.carbs = np.array([item[6] for item in arr]) / 100
        self.names = np.array([item[7] for item in arr])
        self.links = np.array([item[8] for item in arr])
        self.size = len(self.carbs)
        #print(self.minCalories, self.maxCalories, self.minFat, self.maxFat, self.minProtein, self.maxProtein, self.minCarbs, self.maxCarbs,
        #      self.weightTaste, self.weightPrice, totalCalories, totalFat, totalProtein, totalCarbs, self.calories, self.size)

    def objective_function(self, variables):
        totalPrice = np.sum(variables*self.prices)
        totalTaste = np.sum(variables*self.tastes)
        return totalPrice*self.weightPrice-totalTaste*self.weightTaste

    def constraint_min_calories(self, variables):
        totalCalories = np.sum(variables*self.calories)
        #print("totalCalories: ", totalCalories)
        return totalCalories - self.minCalories

    def constraint_max_calories(self, variables):
        totalCalories = np.sum(variables*self.calories)
        #print("totalCalories: ", totalCalories)
        return self.maxCalories - totalCalories

    def constraint_min_fat(self, variables):
        totalFat = np.sum(variables*self.fat)
        #print("totalFat: ", totalFat)
        return totalFat - self.minFat

    def constraint_max_fat(self, variables):
        totalFat = np.sum(variables*self.fat)
        #print("totalFat: ", totalFat)
        return self.maxFat - totalFat

    def constraint_min_protein(self, variables):
        totalProtein = np.sum(variables*self.protein)
        #print("totalProtein: ", totalProtein)
        return totalProtein - self.minProtein

    def constraint_max_protein(self, variables):
        totalProtein = np.sum(variables*self.protein)
        #print("totalProtein: ", totalProtein)
        return self.maxProtein - totalProtein

    def constraint_min_carbs(self, variables):
        totalCarbs = np.sum(variables*self.carbs)
        #print("totalCarbs: ", totalCarbs)
        return totalCarbs - self.minCarbs

    def constraint_max_carbs(self, variables):
        totalCarbs = np.sum(variables*self.carbs)
        #print("totalCarbs: ", totalCarbs)
        return self.maxCarbs - totalCarbs

    def solve(self):

        constraints = (
            {'type': 'ineq', 'fun': partial(self.constraint_min_calories)},
            {'type': 'ineq', 'fun': partial(self.constraint_max_calories)},
            {'type': 'ineq', 'fun': partial(self.constraint_min_fat)},
            {'type': 'ineq', 'fun': partial(self.constraint_max_fat)},
            {'type': 'ineq', 'fun': partial(self.constraint_min_protein)},
            {'type': 'ineq', 'fun': partial(self.constraint_max_protein)},
            {'type': 'ineq', 'fun': partial(self.constraint_min_carbs)},
            {'type': 'ineq', 'fun': partial(self.constraint_max_carbs)}
        )

        initial_guess = [0] * self.size
        bounds = [(0, None)] * self.size
        result = minimize(self.objective_function, initial_guess, constraints=constraints, bounds=bounds, method = "SLSQP")
        combined = np.vstack([
            self.prices,
            self.tastes,
            self.calories,
            self.fat,
            self.protein,
            self.carbs,
            self.names,
            self.links,
            [round(x, 1) for x in result.x]
        ]).T
        return combined