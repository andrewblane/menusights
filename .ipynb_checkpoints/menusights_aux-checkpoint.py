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



def recipes_and_ingredients_to_vector(names=names, categories = True):
    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = SnowballStemmer("english")

    def tokenize_and_stem(title, is_ingredient = False):
        stemmer = SnowballStemmer("english")
        stemmed_titles = []
        new_title=[]
        for word in nltk.word_tokenize(title):
            new_title.append(stemmer.stem(word))
        stemmed_titles.extend(new_title)
        return " ".join([i for i in stemmed_titles])

    def clean_up_ingredient(ingredient_line):
        ingredient_line = re.sub("\[u\'", "", ingredient_line)
        ingredient_line = re.sub("\']", "", ingredient_line)
        return find_measurement_words(ingredient_line)

#    def get_ingredientslist_for_recipeid(i):
#        return [clean_up_ingredient(item.ingredient)\
#                for item in names.filter(Recipe.id == i).all()[0].ingredients]

    def make_ingredient_list_string(ingredientdictlist):
        return " ".join((str(j["ingredient"]) for j in ingredientdictlist))
    
#    tokenized_ingredients = [tokenize_and_stem(make_ingredient_list_string(get_ingredientslist_for_recipeid(i))) for i in (recipes["id"])]
    tokenized_names = [tokenize_and_stem(i) for i in (recipes["name"])]
#    tokenized_name_ing = zip(tokenized_names, tokenized_ingredients)
#    tokenized_name_ing = map(lambda a: " ".join(a), tokenized_name_ing)
#    print(tokenized_name_ing[:5])
    vectorizer = CountVectorizer(ngram_range=(1,3), min_df=0.0003)
    #vectorized_name_ing = vectorizer.fit_transform(tokenized_name_ing)
    vectorized_name_ing = vectorizer.fit_transform(tokenized_names)
    
    # For discretized strategy, uncomment:
    def chol_to_percentile(vector, operate_on):
        v = [i for i in vector if i != 0]
        pctvector = []
        pct75 = np.percentile(v, 75)
        pct50 = np.percentile(v, 50)
        pct25 = np.percentile(v, 25)
        for index, i in enumerate(operate_on):
            if i > pct75:
                pctvector.append("vhigh")
            elif i > pct50:
                pctvector.append("high")
            elif i > pct25: # changed from 20 8/18/17
                pctvector.append("med")
            else:
                pctvector.append("low")
        return pctvector

    if categories == True:
        y = chol_to_percentile(recipes["cholesterol"], recipes["cholesterol"])
        y = np.array(y)
    else:
        ## For continuous strategy:
        y = recipes["cholesterol"]

    # produces an array with mutual information between individual words/n-grams 
    # in recipe names and cholesterol information
    mi = mutual_info_classif(vectorized_name_ing, y)    
    mi /= np.max(mi)

    # Returns indices of columns with MI value greater than e.g. 0.01. Can be used for re
    informative_words = np.array([(index) for index, i in enumerate(mi) if i>0.002])
    # return word vector array with uninformative words removed
    vni = copy.deepcopy(vectorized_name_ing)
    culled_array = vni.toarray()[:,informative_words]
    '''
    Process ground truth data. 
    Steps:
    1. Extract from NutritionIX pkl
    2. Tokenize and stem the ground truth data `tokenized_names_ground_truth`
    3. Vectorize it into the same format vector as the training data `ground_truth_vectorized`
    4. Filter that vector such that it only contains the terms above an MI cutoff `ground_truth_vectorized_culled_array`
    5. Remove any ground truth data that has no cholesterol information or a zero cholesterol:
        masked_ground_truth: a vector of continuous cholesterol data 
        masked_ground_truth_vectnames: the array of one-hot encoded word data
    '''
    
    # Get the ground truth restaurants dataset
    ground_truth_x =[]
    ground_truth_y =[]
    def extract_from_ground_truth_pkls():
        '''
        Gets name, description and cholesterol from NutritionIX ground truth
        '''
        for item in pkl.load(open("groundtruth.pkl", "rb")):
            ground_truth_x.append(str(unicode(item["item_name"]).encode("utf-8") + " " + str(item['item_description']).encode("utf-8")))
            ground_truth_y.append(item["nf_cholesterol"])

        for item in pkl.load(open("groundtruth2.pkl", "rb")):
            ground_truth_x.append(str(unicode(item["item_name"]).encode("utf-8") + " " + str(item['item_description']).encode("utf-8")))
            ground_truth_y.append(item["nf_cholesterol"])

        for item in pkl.load(open("groundtruth3.pkl", "rb")):
            ground_truth_x.append(str(unicode(item["item_name"]).encode("utf-8") + " " + str(item['item_description']).encode("utf-8")))
            ground_truth_y.append(item["nf_cholesterol"])
        return ground_truth_x, ground_truth_y
    
    ground_truth_x, ground_truth_y = extract_from_ground_truth_pkls()
    
    tokenized_names_ground_truth = [tokenize_and_stem(i.decode("utf-8")) for i in (ground_truth_x)]
    # Puts words from new ground truth set into matrix from training set
    ground_truth_vectorized = vectorizer.transform(tokenized_names_ground_truth)
    # Reduces the array back down to the MI threshold
    ground_truth_vectorized_culled_array = ground_truth_vectorized.toarray()[:,informative_words] 
    
    # Exclude ground truth if None or zero 
    mask = [index for (index, item) in enumerate(ground_truth_y) if item !=0 and item!=None ]
    print(mask)
    masked_ground_truth_y = []
    for i,j in enumerate(ground_truth_y):
        if i in mask:
            masked_ground_truth_y.append(j)
    
    # Get the term vector that is indexed same as one-hot encoded term
    masked_ground_truth_vectorized = []
    for i,j in enumerate(ground_truth_vectorized_culled_array):
        if i in mask:
            masked_ground_truth_vectorized.append(j)
    
    # Same for item names and descriptions
    masked_ground_truth_x = []
    for i,j in enumerate(ground_truth_x):
        if i in mask:
            masked_ground_truth_x.append(j)    
    
    # Discretizes ground_truth_y to categories.
    # Do you want to scale this by the scaling coefficient?
    #masked_ground_truth_y = map(lambda a: a*0.0578 + 49.83,masked_ground_truth_y) #scales by fit of linear model against recipes
    if categories == True:
        masked_ground_truth_y = chol_to_percentile(recipes["cholesterol"], masked_ground_truth_y)
    
    # Need to put tokenize_and_stem before this
    tokenized_names_ground_truth = [tokenize_and_stem(i.decode("utf-8")) for i in (ground_truth_x)]
    # Puts words from new ground truth set into matrix from training set
    ground_truth_vectorized = vectorizer.transform(tokenized_names_ground_truth)
    
    '''
    End processing of ground truth data
    '''
    
    return vni, tokenized_names, vectorizer, vectorized_name_ing, culled_array, y, masked_ground_truth_vectorized, masked_ground_truth_y, masked_ground_truth_x, mi, informative_words





#def report_score_and_why(menuitem, vectorizer=vectorizer, model=clf1):
    #input_vectorized = vectorizer.transform([tokenize_and_stem(menuitem)])
    #if input_vectorized.nnz > 0:
        #print(tokenize_and_stem(menuitem))
        #print(input_vectorized.shape)
        ##Need to change this to inputting model
        #p = model.predict_proba(input_vectorized)[0]
        #q = zip(model.classes_, list(p))
        #classification = model.predict(input_vectorized)[0]
        #probability = dict(q)[classification]
        ## Figure out why: list individual score contribution of each word
        #matchwords = [i for i in input_vectorized.todok().keys()] #todok = to dict of keys
        #explaindict = {}
        #ranklist = []
        #for i in matchwords:
            #w = vectorizer.get_feature_names()[i[1]] #gets actual word of feature, by matrix index
            #coef = zip(model.classes_, model.coef_[:,i[1]])
            #ranklist.append((w, dict(coef)["vhigh"]))
            #explaindict[w] = dict(coef)
        ## Figure out the biggest contributor:
        #ranklist = sorted(ranklist, key=lambda a: a[1])
    #else:
        #classification = "unknown"
        #probability = 0
        #explaindict = {"unscorable": "yes"}
        #ranklist = ["unscorable", "unscorable"]
        
    #return classification, probability, explaindict, ranklist[-1][0]


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