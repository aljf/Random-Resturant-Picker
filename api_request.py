# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function
from flask import Flask
from flask import render_template, make_response

import argparse
import json
import pprint
import requests
import sys
import urllib
import os
import random


from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode



API_KEY = os.environ.get('YELP_API_KEY')


API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/' 

SEARCH_MAX = 20

selected_business_json = None


def api_request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location, price, miles, search_limit):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    radius = int(miles)*1609
    url_params = {
        'term': term,
        'latitude': location[0],
        'longitude': location[1],
        'limit': search_limit,
        'price': price,
        'radius': radius,
        'open_now': True
    }
    return api_request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def query_api(search_term, location, price, radius):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """

    if '+' in search_term:
        businesses = []
        plus_count = search_term.count('+')
        search_limit = round(SEARCH_MAX/(plus_count+1))
        # create a list of all terms separated by their '+'
        term_list = search_term.split('+')
        for count in range(plus_count+1):
            print(count)
            response = search(API_KEY, term_list[count], location, price, radius, search_limit)
            businesses = businesses + response.get('businesses')
    else:
        response = search(API_KEY, search_term, location, price, radius, SEARCH_MAX)
        businesses = response.get('businesses')
    business_id_arr = []
    if businesses:
        for i, b in enumerate(businesses):
            business_id_arr.append(businesses[i]['id'])

        selected_business = random.choices(business_id_arr)[0]
        
        selected_business_json = json.dumps(businesses[business_id_arr.index(selected_business)])
        return selected_business_json
    else:
        return {'error': 'no_resturant'}


def main(jsresponse):
    try:
        price = jsresponse.json['price']
    except KeyError:
        return {'error': 'price'}
    try:
        search_term = jsresponse.json['search']
    except KeyError:
        return {'error': 'search'}
    try:
        location = jsresponse.json['location']
    except KeyError:
        return {'error': 'location'}
    try:
        radius = jsresponse.json['radius']
    except KeyError:
        return {'error': 'radius'}

    return query_api(search_term, location, price, radius)


from flask import request
app = Flask(__name__, static_url_path='/static')
@app.route('/')
def home_page(name=None):
    return render_template('index.html', name=name)


@app.route('/postmethod', methods=['POST'])
def get_post_javascript_data():
    return main(request)
