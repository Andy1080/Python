#-------------------------------------------------------------------------------
# Name:        Strava API
# Purpose:
#
# Author:      Andrew Mellor
#
# Created:     11/08/2014
# Copyright:   (c) Andrew Mellor 2014
# Licence:     The MIT License (MIT)
#-------------------------------------------------------------------------------
import requests as rq
import pandas as pd

token = 'e2ce375f9642d036ff9362e829d26c273a2522a4'

payload = {'access_token': token}
headers = {'content-type': 'application/json'}#, 'login': token}


# Segments
# Farnley Line Full - 2314277

r = rq.get('https://www.strava.com/api/v3/segments/2314277/leaderboard', headers=headers, params=payload)

#print r.text
df = pd.read_json(r.text)
print df.head()

def main():
    pass

if __name__ == '__main__':
    main()
