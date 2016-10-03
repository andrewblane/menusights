from __future__ import print_function
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import re

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True)
    calories = Column(Integer)
    fat = Column(Float)
    carbs = Column(Float)
    protein = Column(Float)
    cholesterol = Column(Float)
    sodium = Column(Float)
    servings = Column(Integer)
    #ingredients = 
    #__table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return "<Recipe(name='%s', url='%s')>" % (
            self.name.encode('utf-8'), self.url.encode('utf-8'))
    
class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key = True)
    ingredient = Column(String, nullable = False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    
    recipe = relationship(Recipe, back_populates = 'ingredients')
    #__table_args__ = {'extend_existing': True}
    def __repr__(self):
        return "<Ingredient(ingredient='%s')>" % self.ingredient

Recipe.ingredients = relationship("Ingredient", order_by=Ingredient.id, back_populates="recipe")

class Restaurant(Base):
    __tablename__ = 'restaurants'
    __searchable__ = ['name', 'address']
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    zomatoID = Column(Integer, unique=True)
    costfortwo = Column(Float)
    featured_image = Column(String)
    photos = Column(String)
    menu_url = Column(String)
    price_range = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    
    def __repr__(self):
        return "<Restaurant(name='%s', url='%s')>" % (
            self.name, self.url)

class MenuItem(Base):
    __tablename__ = 'menuitems'
    id = Column(Integer, primary_key=True)
    menuitem = Column(String, nullable = False)
    description = Column(String)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    price = Column(String)
    
    restaurant = relationship(Restaurant, back_populates = 'menuitems')
    __table_args__ = {'extend_existing': True}
    def __repr__(self):
        return "<MenuItem(item='%s', desc='%s')>" % (
            self.menuitem.encode('utf-8'), self.description.encode('utf-8'))
    
Restaurant.menuitems = relationship("MenuItem", order_by=MenuItem.id, back_populates="restaurant")

'''
Next three blocks are functions to remove measurement words from ingredient lists.
'''

measurements = ("femtogram", "gigagram", "gram", "hectogram", "kilogram", \
                "long", "ton", "mcg", "megagram", "metric", "ton", "metric"\
                "tonne", "microgram", "milligram","nanogram", "ounce", \
                "lb", "oz", "each", "pound", "short", "Gram", "Ounce", "Pint", "Quart",\
                "Tablespoon", "Teaspoon", "Tablespoons", "Teaspoons", "Cups", "cup","Fluid Ounce", "fl oz", "Gallon", "Ounce", \
                "Pint", "Quart", "Tablespoon", "Teaspoon", "liter", "litre", "L", "ml", "fluid ounces", "can", "cans")

def find_measurement_words(i):
    ingredient_line = i
    for item in measurements:
        meas = str(" " + item.lower() + " ")
        a = re.search(meas, ingredient_line)
        if a > 0:
            unit = ingredient_line[a.start():a.end()].strip()
            quantity = ingredient_line[:a.start()].strip()
            ingredient = ingredient_line[a.end():].strip()
            break
        else:
            ilist = i.split(" ")
            quantity = ilist[0]
            unit = "each"
            ingredient = " ".join(ilist[1:])
    newitem = {"ingredient": ingredient,
    "unit": unit,
    "quantity":  quantity}
    try:
        fracsplit = ([float(k) for k in newitem["quantity"].split("/")])
        if len(fracsplit) >= 2:
            newitem["quantity"] = fracsplit[0] / fracsplit[1]
    except:
        None
    #print(newitem)
    return newitem

def clean_up_ingredient(ingredient_line):
    ingredient_line = re.sub("\[u\'", "", ingredient_line)
    ingredient_line = re.sub("\']", "", ingredient_line)
    return find_measurement_words(ingredient_line)