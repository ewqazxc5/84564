import numpy as np
import requests

def json_track_calculator(track_details_dict, multi_stop_journey = False, previous_sample_elevation = 0): #accepts one track only in dict form

    flat_fuel_consumption = 0.054
    road_consumption_factors = {"r": [30,1.4], "l": [80,1], "m":[120,1.25]} #speed,factor
    terrain_consumption_factors = {"d": 2.5, "g": 1.25, "p": 1}
    elevation_consumption_factors = { "-10": 0.16, "-9": 0.16, "-8":0.16, "-7":0.16, "-6":0.16,     "-5":0.45, "-4":0.45, "-3":0.45, "-2":0.45,     "-1":1, "0":1, "1":1, "2":1,      "3":1.3, "4":1.3, "5":1.3, "6":1.3,       "7":2.35,"8":2.35,"9":2.35,"10":2.35,       "11":2.9,"12":2.9,"13":2.9,"14":2.9}

    full_stepped_route = []
    sum_of_emissions = []
    sum_of_times = []
    chain_code = str(track_details_dict.get("cc"))
    elevation = track_details_dict.get("elevation")
    elevation_0 = int(elevation[0])
    elevation = elevation[1:]
    road = track_details_dict.get("road")
    terrain = track_details_dict.get("terrain")

    full_stepped_route.append([ [ chain_code[step], elevation[step], road[step], terrain[step] ] for step in range(0,len(chain_code)) ])
    full_stepped_route = np.array(full_stepped_route).reshape(-1,4)

    for i,step in enumerate(full_stepped_route):
        distance = float(step[0])

        delta_elevation = elevation_0 if i == 0 else int(step[1])-int(full_stepped_route[i-1][1])
        if multi_stop_journey == True:
            delta_elevation = previous_sample_elevation 

        net_distance = np.sqrt((distance*distance)+(delta_elevation*delta_elevation))
        elevation_factor = elevation_consumption_factors.get(str(delta_elevation)) if delta_elevation < 12 else 2.9
        road_factor_emission = road_consumption_factors.get(step[2])[1]
        terrain_factor = terrain_consumption_factors.get(step[3])
        time_contribution_seconds = 60*60*distance/road_consumption_factors.get(step[2])[0]
        sum_of_emissions.append(float(flat_fuel_consumption)*float(net_distance)*float(elevation_factor)*float(road_factor_emission)*float(terrain_factor))
        sum_of_times.append(time_contribution_seconds)

        #print("Assesing segment:", step);print("horizontal distance contribution", distance);print("elevation contribution:", delta_elevation);print("net distance contribution:", net_distance, "from root (", delta_elevation, "^2 +", distance, "^2)");print("road contribution:", road_factor_emission, "road travel speed", road_consumption_factors.get(step[2])[0]);print("terrain contribution:", terrain_factor);print("total emission from this step", float(flat_fuel_consumption)*float(net_distance)*float(elevation_factor)*float(road_factor_emission)*float(terrain_factor));print("time contribution from this step", time_contribution_seconds, "seconds");print("--------------------")

    #print("overall emission from this route", sum(sum_of_emissions), "overall time from this route", sum(sum_of_times), "seconds")
    return [sum(sum_of_emissions),sum(sum_of_times)]

def request_track(start = (0,0), end = (299,299), min_steps_straight = 1, max_steps_straight = -99, n_tracks = 300):
    start_x = start[0]; start_y=start[1]; end_x = end[0]; end_y=end[1];
    max_steps_straight = int(min_steps_straight + 5) if max_steps_straight == -99 else max_steps_straight
    base_url = "http://ucl-rse-with-python.herokuapp.com/road-tracks/tracks/?"
    user_inputs_url = ["start_point_x=",start_x,"&start_point_y=",start_y,"&end_point_x=",int(end_x),"&end_point_y=",int(end_y),"&min_steps_straight=",min_steps_straight,"&max_steps_straight=",max_steps_straight,"&n_tracks=",n_tracks]
    user_inputs_url = str(user_inputs_url).replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","")
    request = str(base_url + user_inputs_url)
    returned_request = requests.get(request).json()
    print("Fewer routes available than requested") if returned_request.get("metadata").get("n_tracks") != int(n_tracks) else None
    return returned_request

def sort_results(returned_request, route_criterion = "fast"):
    results_from_tracks = []
    results_from_tracks = [json_track_calculator(track) for track in returned_request]
    # Results are retruned as [time,emission] within a list of lists. 
    # Sorted method sorts by the first element in a 2d array element, the "key = " is required to sort by the second element.
    fastest_route= sorted(results_from_tracks)[0]; lowest_emission_route = sorted(results_from_tracks,key=lambda x: x[1])[0]
    print("Lowest emission route", lowest_emission_route)
    print("Fastest route", fastest_route)
    eco_route_time = lowest_emission_route[0]; eco_route_emission = lowest_emission_route[1];
    fast_route_time = fastest_route[0]; fast_route_emission = fastest_route[1]
    print("Fastest route is also the lowest emission route") if fast_route_time == sorted(results_from_tracks,key=lambda x: x[1])[0][0] else None
    find_winning_track = np.array(results_from_tracks); i_fast,j_fast = np.where(find_winning_track == fast_route_time); i_eco,j_eco = np.where(find_winning_track == eco_route_emission)
    return ("Lowest emission route: ", lowest_emission_route, "track number", i_eco[0]) if "eco" in route_criterion else ("Fastest route", fastest_route, "track number", i_fast[0])

returned_request = request_track(end=(133,150), n_tracks = 10).get("tracks")
print(sort_results(returned_request))