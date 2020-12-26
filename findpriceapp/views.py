from django.shortcuts import render

from . import views
import requests
from bs4 import BeautifulSoup
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer

def mlprice(request):
    nome = ""
    result = 'Here goes the price'
    if request.method == 'POST':
        
        nome = request.POST['nome'] #get the url
        re = requests.get(nome) #make a requisition to page
        soup = BeautifulSoup(re.text, 'html.parser')
        needed = ['0','1','2','3','4','5','6','7','8','9',','] #here is just an array to extract numbers and ',' from the requisition
        test_texts = [value 
                    for element in soup.find_all(class_=True) 
                    for value in element["class"]] #here we're getting all the classes name from the site structure
            
        possible_texts = [
        "game_purchase_price",
        "price",
        "catalog-detail-price-value",
        "preco_desconto",
        "preco",
        "preco_desconto_avista-cm",
        'css-ovezyj',
        "currency-value",
        "best-price"
        ]#possible price classes extracted from some websites
        negative_texts = [
        "container",
        "pop_up", 
        "menu", 
        "hr",
        "nav-menu-item"
        ] #menu, popups, etc.
        training_texts = possible_texts + negative_texts 
        training_labels = ["positive"] * len(negative_texts) + ["negative"] * len(possible_texts) 
        vectorizer = CountVectorizer() 
        vectorizer.fit(training_texts)
        training_vectors = vectorizer.transform(training_texts)
        testing_vectors = vectorizer.transform(test_texts) 
        classifier = tree.DecisionTreeClassifier()
        classifier.fit(training_vectors, training_labels)
        predictions = classifier.predict(testing_vectors)
        c = 0 #counter
        valuesInsideFoundit = []

        for i in predictions: #here's are passing throung the predictions
            if i == "positive": #if it's possible to be a price
                foundit = soup.find(class_=test_texts[c])      #we will get the text inside that class from test_text in the index of the variable 'c'
                valuesInsideFoundit.append(foundit.text)       #and we will append that value that we have just find
            c+=1 #counter increment
        
        firstValuesInsideIt = []
        #↓ Here we are filtering some values in text because in some pages we will find a lot of prices ou symbols that we have in our 'dictonary'(variable 'needed'), and probably
        #will see values like: ["R", "R", "$", "1", "3", "R", "$"].
        #So, we need to filter it to get an expected value like:"R$123,99".

        for k in filter(None,valuesInsideFoundit): #passing through the values without passing through empty indexes
            cc = 0 #counter
            for y in list(k):#passing through any index inside the filtered list.
                if y in needed or y == "R" and list(k)[cc+1] == "$" or y == "$" and list(k)[cc-1] == "R": #if y is inside needed variable or y is "R" and k in the next index of cc is "$"
                    #or y is "$" and k in the last index of cc is "R" it's probably a value in Reais.
                    firstValuesInsideIt.append(str(y).replace("\n", "").replace(' ', '')) #let's padding it and remove the spaces and the line jumps
                else: #if not, let's ignore it
                    pass 
                cc+=1 #cc increment
        ccc = 0
        whatWeWant = ""
        indexOf = 0
#more formating
        for b in firstValuesInsideIt:    
            if b == "R" and firstValuesInsideIt[ccc+1] == "$":        
                indexOf = firstValuesInsideIt.index(str(firstValuesInsideIt[ccc]))      
                break 
            ccc+=1


        lastFormatedValues = []
        cccc = 0
        for y in firstValuesInsideIt[indexOf:]:

            lastFormatedValues.append(y)
            try:
                if lastFormatedValues[cccc-2] == ",":
                    break
            except:
                pass
            cccc+=1
        ccccc = 0
        indexOf2 = 0
        for bb in lastFormatedValues:
            if lastFormatedValues[ccccc] == "R" and lastFormatedValues[ccccc+1] == "$" and lastFormatedValues[ccccc+2] in needed: 
                indexOf2 = lastFormatedValues.index(str(lastFormatedValues[ccccc]))
            ccccc+=1
        for z in lastFormatedValues[indexOf2-8:]:  
            whatWeWant = whatWeWant + z
        #our variable recives our value.
        result = whatWeWant
        
        
        
    #let's put it on page:
    return render(request, 'home/main.html', {'nome':nome, 'result':result})