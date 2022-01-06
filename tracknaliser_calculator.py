import numpy as np
import requests

def json_track_calculator(track_details_dict, multi_stop_journey = False, previous_sample_elevation = 0): #accepts one track only in dict form

    flat_fuel_consumption = 0.054
    road_consumption_factors = {"r": [30,1.4], "l": [80,1], "m":[120,1.25]} #speed,factor
    terrain_consumption_factors = {"d": 2.5, "g": 1.25, "p": 1}
    elevation_consumption_factors = { "-10": 0.16, "-9": 0.16, "-8":0.16, "-7":0.16, "-6":0.16,     "-5":0.45, "-4":0.45, "-3":0.45, "-2":0.45,     "-1":1, "0":1, "1":1, "2":1,      "3":1.3, "4":1.3, "5":1.3, "6":1.3,       "7":2.35,"8":2.35,"9":2.35,"10":2.35,       "11":2.9,"12":2.9,"13":2.9,"14":2.9}
    return None