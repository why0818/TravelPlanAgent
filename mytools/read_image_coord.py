# Huayi Wang
# 2025-06-11
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Optional, Dict, Tuple

def get_exif_data(image_path: str) -> Optional[Dict]:
    """Extract EXIF data from images"""
    # 添加异常捕获和详细日志
    print(f'Parsing: {image_path}')
    try:
        image = Image.open(image_path)
        # print('Successfully opened file.')
    except Exception as e:
        print(f'Failed opening file: {str(e)}')
    exif_data = image._getexif()
    if not exif_data:
        print("Missing EXIF data")
        return None
    # 将数字标签转换为人类可读的标签名称
    readable_exif_data = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    # print("conplete EXIF data：")
    # print(readable_exif_data)
    return readable_exif_data

def get_gps_info(exif_data: Dict) -> Tuple[float, float]:
    """从EXIF数据中提取GPS信息"""
    if "GPSInfo" not in exif_data:
        print("未找到GPS信息")
        return None
    
    gps_info = exif_data["GPSInfo"]
    gps_data = {GPSTAGS.get(tag, tag): value for tag, value in gps_info.items()}
    
    # 提取纬度和经度
    if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
        latitude = convert_to_degrees(gps_data["GPSLatitude"])
        longitude = convert_to_degrees(gps_data["GPSLongitude"])
        
        # 判断南北纬、东西经
        latitude_ref = gps_data.get("GPSLatitudeRef", "N")
        longitude_ref = gps_data.get("GPSLongitudeRef", "E")
        if latitude_ref == "S":
            latitude = -latitude
        if longitude_ref == "W":
            longitude = -longitude
        
        return latitude, longitude
    else:
        print("未找到完整的GPS坐标")
        return None

def convert_to_degrees(value: Tuple) -> float:
    """
    将GPS坐标转换为十进制度数格式
    :param value: GPSLatitude 或 GPSLongitude 的值（IFDRational 类型）
    :return: 十进制度数
    """
    degrees = float(value[0])
    minutes = float(value[1])
    seconds = float(value[2])
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

# read image coord
def read_image_coord(image_path: str) -> Dict:
    """
    例如："images/IMG_20250422_151849.jpg"  # 替换为你的照片路径
    也支持传入图片路径列表，例如：["images/IMG_20250422_151849.jpg", "images/IMG_20250423_161950.jpg"]
    """
    if isinstance(image_path, str):
        image_path = [image_path]
    results = {}
    for path in image_path:
        exif_data = get_exif_data(path)
        if exif_data:
            gps_info = get_gps_info(exif_data)
            if gps_info:
                latitude, longitude = gps_info
                # print(f"照片 {path} 的地理坐标：纬度={latitude}, 经度={longitude}")

                results[path] = {'lat': latitude, 'lng': longitude}
            else:
                print(f"未能从照片 {path} 中提取到有效的地理坐标。")
                results[path] = None
                return None
        else:
            print(f"未能从照片 {path} 中获取到EXIF数据，无法提取地理坐标。")
            results[path] = None
    if len(results) == 1:
        return list(results.values())[0]
    return results

# main function
def main():
    image_path = "D:\images\IMG_20250422_151849.jpg"
    read_image_coord(image_path)


if __name__ == "__main__":
    main()