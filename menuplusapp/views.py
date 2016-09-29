#from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from flask import render_template, request
from menuplusapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import pandas as pd
import psycopg2
from a_Model import ModelIt
from django.utils.encoding import smart_str, smart_unicode
from collections import Counter
from importlib import import_module
from dbmodels import *
import flask_whooshalchemy
import json

user = 'andylane' #add your username here        
host = 'localhost'
dbname = 'restaurants'
engine = create_engine('postgres://%s@%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

### Set up whooshalchemy search of Restaurant names
Session = sessionmaker(bind=engine)
session = Session()

# set the location for the whoosh index
from whooshalchemy import IndexService
config = {"WHOOSH_BASE": "./whoosh_index"}
index_service = IndexService(config=config, session=session)
index_service.register_class(Restaurant)



@app.route('/')
@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/restaurants')
def restaurants():
    restaurant = request.args.get('restaurant_search_entry')
    found_restaurants = list(Restaurant.search_query(restaurant).all())
    found_restaurants_decoded = []
    for item in found_restaurants:
        address = json.loads(item.address)["locality"]
        found_restaurants_decoded.append({"name": item.name, "address": address, "id": item.id})
    return render_template("restaurants.html", found_restaurants = found_restaurants_decoded)

@app.route('/restaurants/<int:id>')
def show_menu_items(id=id):
    menuitems = list(session.query(MenuItem).filter(MenuItem.restaurant_id == id).all())
    for item in menuitems:
        address = json.loads(item.address)["locality"]
        found_restaurants_decoded.append({"name": item.name, "address": address, "id": item.id})

    print menuitems
    return 'Menuitems from %d' % id
    #return render_template("menuitems.html", menuitems=menuitems)

@app.route('/output')
def cesareans_output():
  #pull 'menu_item_name' from input field and store it

  query = "SELECT * FROM recipes WHERE name LIKE \'%s\'" % str("%" + menu_item_name + "%")
  print query
  query_results=pd.read_sql_query(query,con)
  print query_results
  matching_recipes = []
  for i in range(0,query_results.shape[0]):
      ingredient_query = "SELECT ingredients.ingredient FROM ingredients WHERE recipe_id = \'%s\'" % query_results.iloc[i]['id']
      matching_recipes.append(dict(index=query_results.iloc[i]['id'],
                                   recipe_name = query_results.iloc[i]['name'].decode('utf-8', 'ignore'),
                                   recipe_calories=query_results.iloc[i]['calories'],
                                   recipe_ingredients=list(pd.read_sql_query(ingredient_query, con)["ingredient"])
                                   ))
      print matching_recipes[-1]["recipe_ingredients"]
  the_result = ModelIt(menu_item_name,matching_recipes)["calories"]
  the_histogram = str(ModelIt(menu_item_name,matching_recipes)["ingredients"])
  print the_histogram
  return render_template("output.html", matching_recipes = matching_recipes, the_result = the_result)