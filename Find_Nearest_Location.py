# -*- coding: utf-8 -*-
"""============================================================================
Find the nearest location to a given location from a given location list based
on baidu API.
============================================================================"""
#%%% import modules
import json, requests
from math import radians, cos, sin, atan, tan, acos, pi

#%%% inputs and outputs
input_file = 'Location_Parameter2.josn' # 修改本文件中的参数文件路径。

#%%% define functions
def read_json(file_path):
    '''从json中读取文件内容，并返回python字典对象'''
    infile = open(file_path, encoding='utf-8')
    tem = json.load(infile)
    infile.close()
    return tem


def locate_address(address, ak):
    '''根据地址获得其经纬度信息'''
    items = {'output': 'json', 'ak': ak, 'address': address}
    try:
        res = requests.get('http://api.map.baidu.com/geocoder/v2/',
                           params=items, timeout=5)
        result = res.json()
        result = result['result']['location']
    except:
        result = None
    return result


def calculate_distance(location1, location2):
    """近似计算地球上两点之间的直线(三角形斜边)距离距离(单位为：km)"""
    ra=6378.140 #赤道半径
    rb=6356.755 #极半径
    flatten=(ra-rb)/ra  #地球偏率
    lng1 = location1['lng']
    lat1 = location1['lat']
    lng2 = location2['lng']
    lat2 = location2['lat']
    rad_lat_A=radians(lat1)
    rad_lng_A=radians(lng1)
    rad_lat_B=radians(lat2)
    rad_lng_B=radians(lng2)
    pA=atan(rb/ra*tan(rad_lat_A))
    pB=atan(rb/ra*tan(rad_lat_B))
    xx=acos(sin(pA)*sin(pB)+cos(pA)*cos(pB)*cos(rad_lng_A-rad_lng_B))
    c1=(sin(xx)-xx)*(sin(pA)+sin(pB))**2/cos(xx/2)**2
    c2=(sin(xx)+xx)*(sin(pA)-sin(pB))**2/sin(xx/2)**2
    dr=flatten/8*(c1-c2)
    distance=ra*(xx+dr)
    return distance


def road_distance(location1, location2):
    """近似计算地球上两点之间的折线(三角形直角边之和)距离(单位为：km)"""
    lng1 = location1['lng']
    lat1 = location1['lat']
    lng2 = location2['lng']
    lat2 = location2['lat']
    longitude = 20037
    latitude = 40075.7
    long = longitude/180*abs(lat2-lat1)
    average_lat = latitude/360*cos((lat2+lat1)/2/180*pi)
    lati = average_lat*abs(lng1-lng2)
    return long+lati


#%%
infos = read_json(input_file)
ak = infos['baidu_ak']
given_place = infos['given_place']
place_list = infos['place_list']
given_lng_lat = locate_address(given_place, ak)
assert given_lng_lat != None, '不能定位给定地址的经纬度。'

place2lng_lat = {'get':{}, 'not':[]}
for place in place_list:
    tem_lng_lat = locate_address(place, ak)
    if tem_lng_lat is None:
        place2lng_lat['not'].append(place)
    else:
        place2lng_lat['get'][place] = tem_lng_lat

place2distance = {}
for place, lng_lat in place2lng_lat['get'].items():
    place2distance[place] = road_distance(given_lng_lat, lng_lat)
place2distance = sorted(place2distance.items(), key=lambda x:x[1])

for place in place2distance:
    place, distance = place
    print('距离为: %.3fkm 的地方是: %s' % (distance, place))
if place2lng_lat['not']:
    print('以下地址没有得到经纬度信息：')
    for place in place2lng_lat['not']:
        print('  ', place)
