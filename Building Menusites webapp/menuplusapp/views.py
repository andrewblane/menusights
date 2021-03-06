# -*- coding: utf-8 -*-
from flask import render_template, request
from menuplusapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import pandas as pd
import psycopg2
from model import *
from collections import Counter
from importlib import import_module
from menusights_aux import *
import flask_whooshalchemy
import json
import commands
import os, pwd
from collections import Counter

user = pwd.getpwuid(os.getuid()).pw_name    
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

@app.route('/restaurants/')
def restaurants():
    restaurant = request.args.get('restaurant_search_entry')
    found_restaurants = list(Restaurant.search_query(restaurant).all())
    found_restaurants_decoded = []
    for item in found_restaurants:
        address = json.loads(item.address)["locality"]
        if len(list(session.query(MenuItem).filter(MenuItem.restaurant_id == item.id).all())) > 0:
            found_restaurants_decoded.append({"name": item.name, "address": address, "id": item.id})
    return render_template("restaurants.html", found_restaurants = found_restaurants_decoded)

@app.route('/restaurants/<int:id>/')
def show_menu_items(id):
    menuitems = list(session.query(MenuItem).filter(MenuItem.restaurant_id == id).all())
    restaurant = list(session.query(Restaurant).filter(Restaurant.id == id).all())[0]
    matching_menu_items = []
    
    outline_code =   "text-shadow: -1px -1px 0 #000,  1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000; " #Provides bullet black outline
    
    for item in menuitems:
        name = item.menuitem.encode("ascii", 'ignore')
        classification, probability, explaindict, high_chol_word = report_score_and_why(name)

        #Set bullet color
        if classification == "vhigh":
            color = "#d96459" #"#ff6f69"
            classification = "very high"
        elif classification == "high":
            color = "#f2ae72" #"#ffcc5c"
        elif classification == "med":
            color = "#f2e394" #"#ffeead"
            classification = "moderate"
        elif classification == "low":
            color =  "#588c7e"#"#96ceb4"
        else:
            color = "gray"

        current_dict = {"name": name, 
                                    "description": item.description.encode("ascii", 'ignore'), 
                                    "price": item.price.encode("ascii", 'ignore'),
                                    "classification": classification,
                                    "probability": str(str(int(round(probability*100))) + "  %"),
                                    "high_chol_word": str("\"" + str(high_chol_word) + "\"") }
        
        if classification != "high" and classification != "very high": #Only output high-cholesterol-words if it's high or very high chol
            current_dict["high_chol_word"] = " "

        current_dict["classification_bull"] = "<span style=\"" + outline_code + "color: " + color + str(";\"> ● ").decode("utf-8") + "</span>"
        
        # Don't output "unknown"
        if classification == "unknown":
            current_dict["classification_bull"] = " "
            current_dict["probability"] = " "
            current_dict["classification"] = " "
        matching_menu_items.append(current_dict) 
    
    summary = list(Counter([j["classification"] for j in matching_menu_items]).items()) #Calculates the summary at the top of each menu page
    total_scored = sum([j for i,j in summary if i != " "]) #If not equal space (because space is unknown now)
    summary = {
    "vhigh_pct" : sum([j for i,j in summary if i == "very high"])*100/total_scored,
    "high_pct" : sum([j for i,j in summary if i == "high"])*100/total_scored,
    "med_pct" : sum([j for i,j in summary if i == "moderate"])*100/total_scored,
    "low_pct" :  sum([j for i,j in summary if i == "low"])*100/total_scored }
    
    
    return render_template("menuitems.html", menuitems = matching_menu_items, restaurant = restaurant, summary=summary)

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