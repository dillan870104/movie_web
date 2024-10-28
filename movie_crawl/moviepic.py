# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 23:18:55 2024

@author: dillan
"""

import requests
import json
def get_pic():
    url = 'https://capi.showtimes.com.tw/1/app/bootstrap'
    request = requests.get(url)
    movielist = request.json()
    movie_dict = {}
    for movie in movielist['payload']['programs']:
        #print(movie['name'],movie['coverImagePortrait']['url'])
        movie_dict[movie['name']]=movie['coverImagePortrait']['url']
    return movie_dict

data = get_pic()
print(data)
    
