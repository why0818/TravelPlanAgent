# coord_convert
# Huayi Wang
# 2025-06-11

import math
x_pi = (math.pi * 3000.0) / 180.0
pi = math.pi
a = 6378245.0
ee = 0.00669342162296594323

def out_of_china(lat, lng):
    if (lng < 72.004 or lng > 137.8347) and (lat < 0.8293 or lat > 55.8271):
        return True
    else:
        return False

def transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += ((20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0) / 3.0
    ret += ((20.0 * math.sin(y * pi) + 40.0 * math.sin((y / 3.0) * pi)) * 2.0) / 3.0
    ret += ((160.0 * math.sin((y / 12.0) * pi) + 320 * math.sin((y * pi) / 30.0)) * 2.0) / 3.0
    return ret

def transform_lng(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += ((20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0) / 3.0
    ret += ((20.0 * math.sin(x * pi) + 40.0 * math.sin((x / 3.0) * pi)) * 2.0) / 3.0
    ret += ((150.0 * math.sin((x / 12.0) * pi) + 300.0 * math.sin((x / 30.0) * pi)) * 2.0) / 3.0
    return ret

def delta(lat, lng):
    d_lat = transform_lat(lng - 105.0, lat - 35.0)
    d_lng = transform_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    d_lat = d_lat * 180.0 / (((a * (1 - ee)) / (magic * sqrt_magic)) * pi)
    d_lng = d_lng * 180.0 / ((a / sqrt_magic) * math.cos(rad_lat) * pi)
    return {"lat": d_lat, "lng": d_lng}

def wgs84_to_gcj02(wgs84_point: dict[str, float]) -> dict[str, float]:
    """
    eg: wgs84_point = {"lat": 32, "lng": 120}
    """
    # Input Initialization
    wgs_lat = wgs84_point["lat"]
    wgs_lng = wgs84_point["lng"]
    # Output Initialization
    gcj02_point = {"lng": 0, "lat": 0}

    # Judgement conditions
    if out_of_china(wgs_lat, wgs_lng):
        gcj02_point["lat"] = wgs_lat
        gcj02_point["lng"] = wgs_lng
    else:
        # Add deviation
        d = delta(wgs_lat, wgs_lng)
        gcj02_point["lat"] = wgs_lat + d["lat"]
        gcj02_point["lng"] = wgs_lng + d["lng"]
    return gcj02_point

def gcj02_to_wgs84(gcj02_point: dict[str, float]) -> dict[str, float]:
    """
    eg: gcj02_point = {"lat": 32, "lng": 120}
    """
    # Input Initialization
    gcj_lat = gcj02_point["lat"]
    gcj_lng = gcj02_point["lng"]
    # Output Initialization
    wgs84_point = {"lat": 0, "lng": 0}

    # Judgement conditions
    if out_of_china(gcj_lat, gcj_lng):
        wgs84_point["lat"] = gcj_lat
        wgs84_point["lng"] = gcj_lng
    else:
        # Add deviation
        d = delta(gcj_lat, gcj_lng)
        wgs84_point["lat"] = gcj_lat - d["lat"]
        wgs84_point["lng"] = gcj_lng - d["lng"]
    return wgs84_point

def bd09_to_gcj02(bd09_point: dict[str, float]) -> dict[str, float]:
    """
    eg: bd09_point = {"lat": 32, "lng": 120}
    """
    # Input Initialization
    bd_lat = bd09_point["lat"]
    bd_lng = bd09_point["lng"]
    # Output Initialization
    gcj02_point = {"lat": 0, "lng": 0}

    # Caculation
    y = bd_lat - 0.006
    x = bd_lng - 0.0065
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)

    gcj02_point["lat"] = z * math.sin(theta)
    gcj02_point["lng"] = z * math.cos(theta)
    return gcj02_point

def gcj02_to_bd09(gcj02_point: dict[str, float]) -> dict[str, float]:
    """
    eg: gcj02_point = {"lat": 32, "lng": 120}
    """
    # Output Initialization
    bd09_point = {"lat": 0, "lng": 0}

    # Caculation
    y = gcj02_point["lat"]
    x = gcj02_point["lng"]
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi)

    bd09_point["lat"] = z * math.sin(theta) + 0.006
    bd09_point["lng"] = z * math.cos(theta) + 0.0065
    return bd09_point


def wgs84_to_bd09(wgs84_point: dict[str, float]) -> dict[str, float]:
    """
    eg: wgs84_point = {"lat": 32, "lng": 120}
    """
    gcj02_point = wgs84_to_gcj02(wgs84_point)
    bd09_point = gcj02_to_bd09(gcj02_point)
    return bd09_point

def bd09_to_wgs84(bd09_point: dict[str, float]) -> dict[str, float]:
    """
    eg: bd09_point = {"lat": 32, "lng": 120}
    """
    gcj02_point = bd09_to_gcj02(bd09_point)
    wgs84_point = gcj02_to_wgs84(gcj02_point)

    return wgs84_point   

def main():
    wgs84_point = {"lat": 31.282972335555556, "lng": 121.50381469722223}
    bd09_point = wgs84_to_bd09(wgs84_point)
    print(bd09_point)
    return bd09_point

if __name__ == '__main__':
    main()