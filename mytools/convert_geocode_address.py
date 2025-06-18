import requests
import json
import re
import os
from typing import Optional, Dict, Tuple

def geocode(address: str) -> Optional[Dict[str, float]]:
    """
    地址转坐标
    :param address: 需要转换的地址
    :param AK: 百度地图API的AK
    :return: 返回一个字典，包含经度(lng)和纬度(lat)
    """
    AK = os.environ.get('BAIDU_MAP_API_KEY')
    AK = '修改为自己的key'
    url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&callback=showLocation'.format(address, AK)
    res = requests.get(url)
    
    # 解析返回的数据
    match = re.search(r'\((.*?)\)', res.text)
    if match:
        content = match.group(1)
        location = json.loads(content)['result']['location']
        return {'lng': location['lng'], 'lat': location['lat']}
    else:
        print("Error: Cannot parse the response.")
        return None

def reverse_geocode(coord: Dict[str, float]) -> Optional[Tuple[str, str]]:
    """
    坐标转地址
    :param lng: 经度
    :param lat: 纬度
    :param AK: 百度地图API的AK
    :return: 返回解析后的地址信息或兴趣点名称
    """
    AK = os.environ.get('BAIDU_MAP_API_KEY')
    AK = '修改为自己的key'
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&coordtype=bd09ll&location={},{}&extensions_poi=1&radius=50'.format(AK, coord['lat'], coord['lng'])
    res = requests.get(url)
    
    address_info = json.loads(res.text)
    if 'result' in address_info:
        formatted_address = address_info['result']['formatted_address']
        pois = address_info['result'].get('pois', [])
        
        # 如果存在兴趣点，则返回第一个兴趣点的信息，否则仅返回解析后的地址
        if pois:
            first_poi = pois[0]
            return formatted_address, first_poi['addr'] + " " + first_poi['name']
        else:
            return formatted_address, ""
    else:
        print("Error: No result found.")
        return None

def main():
    # 示例调用
    address='文化佳园'
    # 地址转坐标
    location = geocode(address)
    if location:
        print('Coordinates:', location)

    # 坐标转地址（使用上一步获取的经纬度）
    formatted_address, poi_name = reverse_geocode(location['lng'], location['lat'])
    print('Formatted Address:', formatted_address)
    print('POI Name:', poi_name)


if __name__ == '__main__':
    main()
