from create_map_html import create_map_html

# 示例坐标点（经度, 纬度）
points = [
    {"lng":121.520805, "lat":31.291379},
    {"lng":121.521234, "lat":31.290123},
    {"lng":121.519876, "lat":31.292345}
]

# 生成地图文件（中心点自动取第一个坐标）
# 自定义中心点和缩放级别
create_map_html(points,'output.html')
