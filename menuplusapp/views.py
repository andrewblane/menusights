#from __future__ import unicode_literals
from flask import render_template, request
from menuplusapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt
from django.utils.encoding import smart_str, smart_unicode
from collections import Counter

user = 'andylane' #add your username here (same as previous postgreSQL)            
host = 'localhost'
dbname = 'restaurants'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
  #pull 'menu_item_name' from input field and store it
  menu_item_name = request.args.get('menu_item_name')
    #just select the Cesareans  from the birth dtabase for the month that the user inputs
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