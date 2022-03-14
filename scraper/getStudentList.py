from pydoc import source_synopsis
from markupsafe import string
import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from recordHandler import splitClasses
from recordHandler import addNewStudents
from recordHandler import removeDropouts

url ="http://doece.pcampus.edu.np/index.php/students-bachelor-in-computer-engineering/"
headers = {"Accept-Language":"en-US,en;q=0.5"}
results = requests.get(url,headers=headers)

soup = BeautifulSoup(results.text,"html.parser")

#initiliate data storage
rollNo =[]
name =[]
temp=[]

#find the specific batch roll number and name
matched_tags = soup.find_all(lambda tag:len(tag.find_all()) == 0 and "PUL075" in tag.text)      #change year as needed batch

############################extracting the name and roll number into sparate lists###############################

#converting bs4.element.tag into string list
for matched_tag in matched_tags:
    temp.append(str(matched_tag))

#temporary lists for removing the <p> and </p> tags
z1=[]
z2=[]

#split the roll number and name
for x in temp:
    y = x.split(" ",1) 
    z1.append(y[0])
    z2.append(y[1])

#Get name list
for x in z2:
    x1= x.split("<",1)
    name.append(x1[0])

#Get roll number list
for x in z1:
    x1= x.split(">",1)
    rollNo.append(x1[1])
#################################### END extracting name and roll number #####################################

#remove the weird unicode character
for index, element in enumerate(rollNo):
    rollNo[index] = element.replace('\xa0',' ')

for index, element in enumerate(name):
    name[index] = element.replace('\xa0',' ')

for index in range(len(rollNo)):
    rollNo[index] = rollNo[index].replace(" ","")

#print(rollNo)    

#pandas dataframe
records = pd.DataFrame({
    'RollNo': rollNo,
    'Name': name,
})

#convert pandas dataframe to csv file
records.to_csv('PUL075BCT.csv')
print("Records retrived and save as PUL075BCT.csv")

try:
    removeDropouts()
    splitClasses()
    addNewStudents()
except:
    print("\n SOME ERROR OCCURED\n")