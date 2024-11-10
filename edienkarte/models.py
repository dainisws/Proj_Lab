from sqlalchemy import Column, String, Integer, Text, Float, create_engine
import os
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def init_db():
    engine = create_engine("sqlite:///{}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")))
    Base.metadata.create_all(engine)

# User food preferences should be implemented after profile management is created
class Input():
    max_cooking_time = 0
    min_calories = 0
    max_calories = 0
    min_fat = 0
    max_fat = 0
    min_protein = 0
    max_protein = 0
    min_carbs = 0
    max_carbs = 0
    price_weight = 0.5
    taste_weight = 0.5

class Food(Base):

    __tablename__ = "Food"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store = Column(String(20), nullable=False)
    link = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    main_category = Column(String(80), nullable=False)
    last_category = Column(String(80), nullable=False)
    info = Column(Text, nullable=True)
    amount = Column(Integer, nullable=True)
    pricePerKg = Column(Float, nullable=True)
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)

    def __init__(self, store, link, name, mainCategory, lastCategory, info, amount, pricePerKg, calories, protein, fat, carbs):
        self.store = store
        self.link = link
        self.name = name
        self.main_category = mainCategory
        self.last_category = lastCategory
        self.info = info
        self.amount = amount
        self.pricePerKg = pricePerKg
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbs = carbs

class Recipe(Base):

    __tablename__ = "Recipe"

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(Text, nullable=False, unique=True)
    info = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    time_s = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)

class RecipesIngredients(Base):

    __tablename__ = "RecipesIngredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    proportion = Column(Integer, nullable=True)