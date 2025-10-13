from . import bp
from flask import render_template
import requests
import random
from flask import jsonify

@bp.get("/")
def home():
    # ex: GET /countries
    return render_template("index_countries.html")

@bp.get("/get_countries")
def get_countries():
    response = requests.get("https://restcountries.com/v3.1/all?fields=name,capital,population,flags,region")
    all_countries = response.json()

    # Sort countries with a capital
    valid_countries = [country for country in all_countries if 'capital' in country and country['capital']]
    
    selected = random.sample(valid_countries, 5)

    countries_info = []
    for country in selected:
        countries_info.append({
            "name": country.get("name", {}).get("common", "N/A"),
            "capital": country.get("capital", ["N/A"])[0],
            "region": country.get("region", "N/A"),
            "population": country.get("population", "N/A"),
            "flag": country.get("flags", {}).get("png", "")
        }) 
    
    return jsonify(countries_info)