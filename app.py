from flask import Flask,Response,send_file
import requests
from bs4 import BeautifulSoup
import urllib.request
import ssl
import easyocr
import cv2
import re
import pandas as pd


app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/api/<state>/<distict>/<block>/", methods=['GET'])
def home(state,distict,block):

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
    main_links = []
    names = []
    address = []
    phone_no = []
    pre_process = []
    url = "https://www.csclocator.com/csc/{0}/{1}/{2}/".format(state,distict,block)
    
    r = requests.get(url)
    htmlContent = r.content
    #print(htmlContent)
    soup = BeautifulSoup(htmlContent,'html.parser')
    #print(soup.prettify)


    #Main
    tag_class = soup.find_all('tbody')
    #print(tag_class)
    for link in tag_class:
    # print(link.get('td'))
        a_tag_class = link.find_all("a")
    for i in a_tag_class:
        main_links.append(i.get('href'))
    #print(main_links)

    tag_class = soup.find_all('tbody')
    #print(tag_class)
    for link in tag_class:
    # print(link.get('td'))
        a_tag_class = link.find_all("td")
    for i in a_tag_class:
        if i.text == " View ":
            pass
        else:
            pre_process.append(i.text)
    #print(len(pre_process))

    for data_find in range(1,len(pre_process)+1):
        if data_find % 2 ==0:
            address.append(pre_process[data_find-1])
        else:
            names.append(pre_process[data_find-1])
    print(names)
    print(address)    

    for links in main_links:
        
        r = requests.get(links)
        htmlContent = r.content
        #print(htmlContent)
        soup = BeautifulSoup(htmlContent,'html.parser')
        #print(soup.prettify)
        img_tag = soup.find_all('img')
        img_url = img_tag[1].get('src')
        urllib.request.urlretrieve(img_url,'phone.png')
        img = cv2.imread('phone.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        reader=easyocr.Reader(['en'])
        result=reader.readtext(img,detail=0)
        capdata = result[0]
        numeric_string = re.sub("[^0-9]", "", capdata)
        phone_no.append(numeric_string)
    df = pd.DataFrame({'Name':names,'Address':address,'Phone_Number':phone_no})

    data = df.to_csv()
    
    return Response(df.to_csv(), mimetype='text/csv', headers={"Content-disposition":
                 "attachment; filename={0}-{1}-{2}.csv".format(state,distict,block)})
   

app.run()