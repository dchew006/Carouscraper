# importing libraries
import pandas as pd
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
        self.sortby = 'likes'
        
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
    def dataframe(self):
        cleanedjson = self.cleanedjson()        
        results = []
        for i in cleanedjson:
            populate = self.Listings(
            title = i['title'],
            description = i['belowFold'][2]['stringContent'],
            price = i['price'].replace('S$',''),
            photo = i['media'][0]['photoItem']['url'],
            timestamp = datetime.fromtimestamp(i['aboveFold'][0]['timestampContent']['seconds']['low']).strftime('%d-%m-%Y %H:%M'),
            likes= i.get('likesCount',0),
            link = "https://www.carousell.sg/p/{}/".format(i['id']),
            )
            results.append(asdict(populate))
            
            #return dataframe
            df = pd.DataFrame(results)
            
        return df
    
    def sort_df(self):
        df = self.dataframe().sort_values(by=self.sortby, ascending=False)
        #remove the bottom 3% of price outliers
        df['price'] = df['price'].str.replace(',','')
        df['price'] = df['price'].str.strip()
        df['price'] = df['price'].astype(float)
        df = df[df['price'] > df['price'].quantile(0.03)]
    
        return df.reset_index(drop=True)

# find today items
class newitems(CarousellScraper):
        
    df = CarousellScraper().sort_df()
    today = datetime.today().strftime('%d-%m-%Y')
        
    def todayitems():
        df_index = []
        for index, row in newitems.df.iterrows():
            if row['timestamp'].split(' ')[0] == newitems.today:
                df_index.append(index)
        return newitems.df.iloc[df_index]

#################### LOGIC ####################

#Grabs content
def main():
    if newitems.todayitems().empty == True:
        pass
    else:
        sendmessage()

#################### SEND MSG ####################
def sendmessage():
    df = newitems.todayitems()
    for rows in df.iterrows():
        message = f'{rows[1]["title"]} at ${rows[1]["price"]}.\n\nLink: {rows[1]["link"]}\n\n ------------------------------'
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}'
        requests.get(url)
        
if __name__ == '__main__':
    main()