# importing libraries
import requests
import json
from datetime import datetime
from dataclasses import dataclass
from dataclasses import asdict
import os

#################### scraper ####################
CHAT_ID = os.environ.get('CHAT_ID')
TOKEN = os.environ.get('TOKEN')
query = 'Prism PG400U'

class CarousellScraper:
    def __init__(self):
        self.query = query
        self.sortby = 'price'
        
    # defining the api-endpoint
    def rawjson(self):
        query = self.query
        
        url = "https://www.carousell.sg/api-service/filter/cf/4.0/search/"
        payload = {
            "bestMatchEnabled": True,
            "count": 1000,
            "query": query}
        headers = {
            "Cookie": "latra=1669852800000; _t=t%3D1669838065718%26u%3D1297429; jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyOTc0MjkiLCJpc3MiOiJjIiwiaXNzdWVkX2F0IjoxNjY5MTM5MzAwLCJzZWNyZXQiOiI3MzAzIiwidXNlciI6InNlbGxhdGNoZXcifQ.fbGWHDCcMIZg0mPHkxj2Oy2VxveBnzfOmupxgHDivHQ; siv_2=fe5f6971-b060-45f7-bfd4-b1767735606d; _t2=j0-0GyrCgJ; _csrf=gir89q_VPdOzg8WyuX1EGJSd",
            "csrf-token": "CtC6rZlx-c1P-WIqoPobaqlVk4gt0qZ9MzPI",}
        response = requests.request("POST", url, json=payload, headers=headers)
        datajson = json.loads(response.text)['data']['results']
        
        return datajson

    #cleaning json
    def cleanedjson(self):
        datajson = self.rawjson()
        
        cleanedjson = []
        for i in datajson:
            try:
                cleanedjson.append(i['listingCard'])
            except:
                pass
            
        return cleanedjson

    # define dataclass
    @dataclass
    class Listings:
        title: str
        description: str
        price: float
        photo: str
        likes: int
        timestamp: str
        link: str

    # return cleaned dataframe
    def get_dictionary(self):
        cleanedjson = self.cleanedjson()        
        results = []
        for i in cleanedjson:
            populate = self.Listings(
            title = i['title'],
            description = i['belowFold'][2]['stringContent'],
            price = i['price'].replace('S$','').replace(',','').strip(),
            photo = i['media'][0]['photoItem']['url'],
            timestamp = datetime.fromtimestamp(i['aboveFold'][0]['timestampContent']['seconds']['low']).strftime('%d-%m-%Y %H:%M'),
            likes= i.get('likesCount',0),
            link = "https://www.carousell.sg/p/{}/".format(i['id']),
            )
            results.append(asdict(populate))
            
        return results
    
    def sort_dictionary(self):
        dictionary = self.get_dictionary()
        # remove bottom 3 quantile of price outliers
        dictionary = [i for i in dictionary if float(
            i['price']) > (float(i['price']) * 0.03)]
        # sort by price
        dictionary = sorted(dictionary, key=lambda x: float(
            x['price']), reverse=False)

        return dictionary

# find today items
class newitems(CarousellScraper):
        
    def today_items(self):
        products = self.sort_dictionary()
        today = datetime.today().strftime('%d-%m-%Y')
        today_items = []
        for i in products:
            if i['timestamp'].startswith(today):
                today_items.append(i)
        return today_items

#################### LOGIC ####################

#Grabs content
def main():
    if newitems().today_items() == []:
        pass
    else:
        sendmessage()

#################### SEND MSG ####################

def sendmessage():
    items = newitems().today_items()
    for i in items:
        message = f"{i['title']} at ${i['price']}.\n\nLink: {i['link']}\n\n ------------------------------"
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}'
        requests.get(url)
        
if __name__ == '__main__':
    main()