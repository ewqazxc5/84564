import numpy as np
import requests
import time
from math import *
from random import *

def json_track_calculator(track_details_dict, multi_stop_journey = False, previous_sample_elevation = 0): #accepts one track only in dict form

    flat_fuel_consumption = 0.054
    road_consumption_factors = {"r": [30,1.4], "l": [80,1], "m":[120,1.25]} #speed,factor
    terrain_consumption_factors = {"d": 2.5, "g": 1.25, "p": 1}
    elevation_consumption_factors = {  "-8":0.16,  "-4":0.45,  "0":1,  "4":1.3, "8":2.35,"12":2.9}

    full_stepped_route = []
    sum_of_emissions = []
    sum_of_times = []
    sum_of_distance = []
    chain_code = str(track_details_dict.get("cc"))
    elevation = track_details_dict.get("elevation")
    elevation_0 = int(elevation[0])
    elevation = elevation[1:]
    road = track_details_dict.get("road")
    terrain = track_details_dict.get("terrain")

    full_stepped_route.append([ [ chain_code[step], elevation[step], road[step], terrain[step] ] for step in range(0,len(chain_code)) ])
    full_stepped_route = np.array(full_stepped_route).reshape(-1,4)

    for i,step in enumerate(full_stepped_route):
        distance = 1

        delta_elevation = elevation_0 if i == 0 else int(step[1])-int(full_stepped_route[i-1][1])
        if multi_stop_journey == True:
            delta_elevation = previous_sample_elevation 

        net_distance = np.sqrt((distance*distance)+(delta_elevation*delta_elevation/1000000))

        if delta_elevation/10>10:
            delta_elevation=12
        elif 6<delta_elevation/10<=10:
            delta_elevation=8
        elif 2<delta_elevation/10<=6:
            delta_elevation=4
        elif -2<=delta_elevation/10<=2:
            delta_elevation=0
        elif -6<=delta_elevation/10<-2:
            delta_elevation=-4
        else:
            delta_elevation=-8
        elevation_factor = elevation_consumption_factors.get(str(delta_elevation))

        road_factor_emission = road_consumption_factors.get(step[2])[1]
        terrain_factor = terrain_consumption_factors.get(step[3])
        time_contribution_seconds = 60*60*net_distance/road_consumption_factors.get(step[2])[0]
        sum_of_emissions.append(2.6391*float(flat_fuel_consumption)*float(net_distance)*float(elevation_factor)*float(road_factor_emission)*float(terrain_factor))
        sum_of_times.append(time_contribution_seconds)
        sum_of_distance.append(net_distance)

        #print("Assesing segment:", step);print("horizontal distance contribution", distance);print("elevation contribution:", delta_elevation);print("net distance contribution:", net_distance, "from root (", delta_elevation, "^2 +", distance, "^2)");print("road contribution:", road_factor_emission, "road travel speed", road_consumption_factors.get(step[2])[0]);print("terrain contribution:", terrain_factor);print("total emission from this step", float(flat_fuel_consumption)*float(net_distance)*float(elevation_factor)*float(road_factor_emission)*float(terrain_factor));print("time contribution from this step", time_contribution_seconds, "seconds");print("--------------------")

    #print("overall emission from this route", sum(sum_of_emissions), "overall time from this route", sum(sum_of_times), "seconds")
    return [sum(sum_of_emissions),sum(sum_of_times),sum(sum_of_distance)]

def request_track(start = (0,0), end = (299,299), min_steps_straight = 1, max_steps_straight = -99, n_tracks = 300):
    start_x = start[0]; start_y=start[1]; end_x = end[0]; end_y=end[1]; 
    if max_steps_straight == -99 or max_steps_straight<min_steps_straight:
        max_steps_straight = int(min_steps_straight + 5) 
    else:
        max_steps_straight=max_steps_straight
    base_url = "http://ucl-rse-with-python.herokuapp.com/road-tracks/tracks/?"
    user_inputs_url = ["start_point_x=",start_x,"&start_point_y=",start_y,"&end_point_x=",int(end_x),"&end_point_y=",int(end_y),"&min_steps_straight=",min_steps_straight,"&max_steps_straight=",max_steps_straight,"&n_tracks=",n_tracks]
    user_inputs_url = str(user_inputs_url).replace(",","").replace("[","").replace("]","").replace(" ","").replace("'","")
    request = str(base_url + user_inputs_url)
    returned_request = requests.get(request).json()
    print("Fewer routes available than requested") if returned_request.get("metadata").get("n_tracks") != int(n_tracks) else None
    return returned_request

def sort_results(returned_request_track):
    dic_tracks={}
    for i,j in enumerate(returned_request_track):
        dic_tracks.update({i:j})
    results_from_tracks = [[index,json_track_calculator(track)] for index,track in enumerate(returned_request_track)]
    # Results are retruned as [time,emission] within a list of lists. 
    # Sorted method sorts by the first element in a 2d array element, the "key = " is required to sort by the second element.
    lowest_emission_route_index= sorted(results_from_tracks,key=lambda x: x[1])[0][0]
    fastest_route_index = sorted(results_from_tracks,key=lambda x: x[2])[0][0]
    shortest_route_index=sorted(results_from_tracks,key=lambda x: x[3])[0][0]
    lowest_emission_route=dic_tracks.get(lowest_emission_route_index)
    fastest_route=dic_tracks.get(fastest_route_index)
    shortest_route=dic_tracks.get(shortest_route_index)

    return [lowest_emission_route,fastest_route,shortest_route]

class Tracks():
    def __init__(self,x0,y0,x1,y1,n_tracks):
        self.n_tracks=n_tracks
        self.x0=x0
        self.y0=y0
        self.x1=x1
        self.y1=y1
        self.track_data=request_track(start=(self.x0,self.y0),end=(self.x1,self.y1),n_tracks=self.n_tracks).get("tracks")
        dic_tracks={}
        for i,j in enumerate(self.track_data):
            dic_tracks.update({i:j})
        self.dic_tracks=dic_tracks

    def __len__(self):
        return self.n_tracks

    def __str__(self):
        return '<Tracks: {%d} from (%d,%d) to (%d,%d)>'%(self.n_tracks,self.x0,self.y0,self.x1,self.y1)

    def kmeans(self,clusters=3,iterations=10):
        points_data=[]
        for i in range(self.n_tracks):
            points_data+=[tuple(json_track_calculator(self.dic_tracks(i)))]
        m=[]
        for i in range(clusters):
            m+=[points_data[randrange(len(points_data))]]

        alloc=[None]*len(points_data)
        n=0
        while n<iterations:
            for i in range(len(points_data)):
                p=points_data[i]
                d=[None] * 3
                d[0]=sqrt((p[0]-m[0][0])**2 + (p[1]-m[0][1])**2 + (p[2]-m[0][2])**2)
                d[1]=sqrt((p[0]-m[1][0])**2 + (p[1]-m[1][1])**2 + (p[2]-m[1][2])**2)
                d[2]=sqrt((p[0]-m[2][0])**2 + (p[1]-m[2][1])**2 + (p[2]-m[2][2])**2)
                alloc[i]=d.index(min(d))
            for i in range(3):
                alloc_ps=[p for j, p in enumerate(points_data) if alloc[j] == i]
                new_mean=(sum([a[0] for a in alloc_ps]) / len(alloc_ps), sum([a[1] for a in alloc_ps]) / len(alloc_ps), sum([a[2] for a in alloc_ps]) / len(alloc_ps))
                m[i]=new_mean
            n=n+1
        dic_clusters={}
        for i in range(clusters):
            alloc_ps=[p for j, p in enumerate(points_data) if alloc[j] == i]
            dic_clusters.update({i:alloc_ps})
        return dic_clusters

    def greenest(self):

        return 
    def fastest(self):

        return
    def shortest(self):

        return
    def get_track(self,x):
        return
    @property
    def start(self):
        return (self.x0,self.y0)
    @property
    def end(self):
        return (self.x1,self.y1)
    @property
    def map_size(self):
        return [300,300]
    @property
    def date(self):
        return

    


class SingleTrack():

    def __init__(self,):
        pass



def query_tracks(start = (0,0), end = (299,299), min_steps_straight = 1, max_steps_straight = -99, n_tracks = 300,save=True):
    import json
    returned_request=request_track(start=start,end=end,min_steps_straight=min_steps_straight,max_steps_straight=max_steps_straight,n_tracks=n_tracks)
    if save:
        str_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).replace(' ','T').replace('-','').replace(':','')
        str_details='_'+str(n_tracks)+'_'+str(start[0])+'_'+str(start[1])+'_'+str(end[0])+'_'+str(end[1])+'.json'
        file_name='tracks_'+str_time+str_details
        with open(file_name,'w') as file_obj:
            json.dump(returned_request,file_obj)
    tracks=Tracks(start[0],start[1],end[0],end[1],n_tracks)
    return tracks
    









returned_request_track = request_track(end=(133,150), n_tracks = 10).get("tracks")
print(sort_results(returned_request))
