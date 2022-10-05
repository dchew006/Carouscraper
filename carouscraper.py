# time how long code takes to run in s
import time
start_time = time.time()

import os
import requests
import json
import pandas as pd
from datetime import datetime

#################### SCRAPER ####################
TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']
query = "Prism PG400"

class CarousellScraper:
    def __init__(self):
        self.query = query
        self.url = "https://www.carousell.sg/api-service/filter/cf/4.0/search/"
        self.sortby = "Price"

    #page 1 query
    def page1query(self):
        url = self.url
        query = self.query

        payload = {
            "bestMatchEnabled": True,
            "canChangeKeyword": True,
            "count": 99,
            "countryCode": "SG",
            "countryId": "1880251",
            "filters": [],
            "includeEducationBanner": True,
            "includeSuggestions": True,
            "locale": "en",
            "prefill": {},
            "query": query
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.carousell.sg",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
            "Content-Length": "215",
            "Connection": "keep-alive",
            "Cookie": "siv_2=fae03f40-6c3d-4ee0-9d11-2c629161aa16; latra=1656892800000; _t=a%3DcnCBt_K2Rj%26t%3D1656854322299; _t2=j0-0GyrCgJ; _csrf=gir89q_VPdOzg8WyuX1EGJSd",
            "Host": "www.carousell.sg",
            "csrf-token": "kigB2KzW-uPYbnAtOHRP62xNyulvxxeTl3GE",
            "y-platform": "web",
            "y-x-request-id": "zZZB7HRK4HnexXQQ",
            "y-build-no": "2"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        datajson = json.loads(response.text)['data']['results']

        #variables for pagination page 2
        search_contextpage2 = json.loads(response.text)[
            'data']['searchContext']
        sessionpage2 = json.loads(response.text)['data']['session']

        results1 = []
        for i in datajson:
            title = i['listingCard']['title']
            # price = i['listingCard']['price']
            price = float(i['listingCard']['price'].replace(
                'S$', '').replace(',', '').strip())
            description = i['listingCard']['belowFold'][2]['stringContent']
            try:
                photo = i['listingCard']['media'][0]['photoItem']['url']
            except:
                photo = '0'
            try:
                likes = i['listingCard']['likesCount']
            except:
                likes = int(0)
            bumpstatus = i['listingCard']['aboveFold'][0]['component']
            timestamp = datetime.fromtimestamp(
                i['listingCard']['aboveFold'][0]['timestampContent']['seconds']['low']).strftime('%d-%m-%Y %H:%M')
            status = i['listingCard']['belowFold'][3]['stringContent']
            link = "https://www.carousell.sg/p/{}/".format(
                i['listingCard']['id'])

            data = {
                'Title': title,
                'Price': price,
                "Description": description,
                'Status': status,
                'Photo': photo,
                'Likes': likes,
                "BumpStatus": bumpstatus,
                "Link": link,
                "Time": timestamp
            }
            results1.append(data)

        return results1, search_contextpage2, sessionpage2

    #pagination page 2
    def page2query(self):
        url = "https://www.carousell.sg/api-service/search/cf/4.0/search/"
        query = self.query

        search_contextpage2 = self.page1query()[1]
        sessionpage2 = self.page1query()[2]

        payload = {
            "bestMatchEnabled": True,
            "canChangeKeyword": True,
            "count": 40,
            "countryCode": "SG",
            "countryId": "1880251",
            "filters": [],
            "includeEducationBanner": True,
            "includeSuggestions": True,
            "locale": "en",
            "prefill": {},
            "query": query,
            "searchContext": search_contextpage2,
            "session": sessionpage2
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.carousell.sg",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
            "Content-Length": "1357",
            "Connection": "keep-alive",
            "Cookie": "siv_2=012e8dde-bb0c-4c69-ab5b-f23fac52b217; latra=1656892800000; _t=a%3DcnCBt_K2Rj%26t%3D1656854322299; _t2=j0-0GyrCgJ; _csrf=gir89q_VPdOzg8WyuX1EGJSd",
            "Host": "www.carousell.sg",
            "csrf-token": "k9zOJbX7-1yviTdCuPHmtQq9iHHeraFU4_1I",
            "y-platform": "web",
            "y-x-request-id": "y1eFCkpT9uPBgUCH",
            "y-build-no": "2"
        }

        responsepagination = requests.request(
            "POST", url, json=payload, headers=headers)
        nextpageraw = json.loads(responsepagination.text)[
            'data']['results'][1:]

        results2 = self.page1query()[0]

        for i in nextpageraw:
            title = i['listingCard']['title']
            price = float(i['listingCard']['price'].replace(
                'S$', '').replace(',', '').strip())
            description = i['listingCard']['belowFold'][2]['stringContent']
            try:
                photo = i['listingCard']['media'][0]['photoItem']['url']
                likes = i['listingCard']['likesCount']
            except:
                likes = int(0)
                photo = int(0)
            bumpstatus = i['listingCard']['aboveFold'][0]['component']
            timestamp = datetime.fromtimestamp(
                i['listingCard']['aboveFold'][0]['timestampContent']['seconds']['low']).strftime('%d-%m-%Y %H:%M')
            status = i['listingCard']['belowFold'][3]['stringContent']
            link = "https://www.carousell.sg/p/{}/".format(
                i['listingCard']['id'])

            data = {
                'Title': title,
                'Price': price,
                "Description": description,
                'Status': status,
                'Photo': photo,
                'Likes': likes,
                "BumpStatus": bumpstatus,
                "Link": link,
                "Time": timestamp}
            results2.append(data)

        #variables for pagination page 3
        search_contextpage3 = json.loads(responsepagination.text)[
            'data']['searchContext']
        sessionpg3 = json.loads(responsepagination.text)['data']['session']

        return results2, search_contextpage3, sessionpg3

    #pagination page 3
    def page3query(self):
        url = "https://www.carousell.sg/api-service/search/cf/4.0/search/"
        query = self.query

        search_contextpage3 = self.page2query()[1]
        sessionpg3 = self.page2query()[2]

        payload = {
            "bestMatchEnabled": True,
            "canChangeKeyword": True,
            "ccid": 1643,
            "count": 40,
            "countryCode": "SG",
            "countryId": "1880251",
            "filters": [
                {
                    "enforce": False,
                    "fieldName": "collections",
                    "idsOrKeywords": {"value": ["1241"]}
                }
            ],
            "includeEducationBanner": True,
            "includeSuggestions": True,
            "locale": "en",
            "prefill": {},
            "query": query,
            "searchContext": search_contextpage3,
            "session": sessionpg3
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.carousell.sg",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
            "Referer": "https://www.carousell.sg/categories/mobile-phones-gadgets-215/tablets-1241/?addRecent=true&canChangeKeyword=true&includeSuggestions=true&search=ipad%20mini&searchId=ebL9hY",
            "Content-Length": "3647",
            "Connection": "keep-alive",
            "Cookie": "siv_2=82747098-60f0-4421-a51f-abd5b5418d35; latra=1656892800000; _t=a%3DcnCBt_K2Rj%26t%3D1656854322299; _t2=j0-0GyrCgJ; _csrf=gir89q_VPdOzg8WyuX1EGJSd",
            "Host": "www.carousell.sg",
            "csrf-token": "7Aug2mnn-MsXW00ZmQnaxU3gdkKrzm0LbEIg",
            "y-platform": "web",
            "y-x-request-id": "bjg3DfcJy_LK6ZB8",
            "y-build-no": "2"
        }

        responsepaginationpg3 = requests.request(
            "POST", url, json=payload, headers=headers)
        lastpageraw = json.loads(responsepaginationpg3.text)[
            'data']['results'][1:]

        results3 = self.page2query()[0]

        for i in lastpageraw:
            title = i['listingCard']['title']
            price = float(i['listingCard']['price'].replace(
                'S$', '').replace(',', '').strip())
            description = i['listingCard']['belowFold'][2]['stringContent']
            try:
                photo = i['listingCard']['media'][0]['photoItem']['url']
                likes = i['listingCard']['likesCount']
            except:
                likes = int(0)
                photo = int(0)
            bumpstatus = i['listingCard']['aboveFold'][0]['component']
            timestamp = datetime.fromtimestamp(
                i['listingCard']['aboveFold'][0]['timestampContent']['seconds']['low']).strftime('%d-%m-%Y %H:%M')
            status = i['listingCard']['belowFold'][3]['stringContent']
            link = "https://www.carousell.sg/p/{}/".format(
                i['listingCard']['id'])

            data = {
                'Title': title,
                'Price': price,
                "Description": description,
                'Status': status,
                'Photo': photo,
                'Likes': likes,
                "BumpStatus": bumpstatus,
                "Link": link,
                "Time": timestamp}
            results3.append(data)

        return results3

    #Make dataframe
    def make_df(self):
        results = self.page3query()
        #remove the bottom 3% of data by price because they are most likely scams
        df = pd.DataFrame(results).sort_values(
            by=[self.sortby], ascending=True)
        df = df[df['Price'] >= df['Price'].quantile(
            0.03)].reset_index(drop=True)
        return df

class newitems(CarousellScraper):
        
    df = CarousellScraper().make_df()
    today = datetime.today().strftime('%d-%m-%Y')
        
    def todayitems():
        df_index = []
        for index, row in newitems.df.iterrows():
            if row['Time'].split(' ')[0] == newitems.today:
                df_index.append(index)
        return newitems.df.iloc[df_index]

#################### LOGIC ####################

#Grabs content
def main():
    if newitems.todayitems().empty == True:
        message = "No new items today"
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}'
        requests.get(url)
    else:
        sendmessage()

#################### SEND MSG ####################
def sendmessage():
    df = newitems.todayitems()
    for rows in df.iterrows():
        message = f'{rows[1]["Title"]} at ${rows[1]["Price"]}.\n\nLink: {rows[1]["Link"]}\n\n ------------------------------'
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}'
        requests.get(url)
        
if __name__ == '__main__':
    main()

print("--- %s seconds ---" % (time.time() - start_time))