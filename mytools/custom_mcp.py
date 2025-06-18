from typing import Dict, Tuple, List, Optional
from mcp.server.fastmcp import FastMCP
import get_image_files
import convert_coord
import create_map_html
import read_image_coord
import convert_geocode_address
import logging
from logging.handlers import RotatingFileHandler
import os
import time

mcp = FastMCP("travel plan mcp")
# mcp.add_tool(create_map_html.create_map_html)
# mcp.add_tool(get_image_files.get_image_files)
# mcp.add_tool(coord_convert.wgs84_to_bd09)
# mcp.add_tool(read_image_coord.read_image_coord)
# mcp.add_tool(convert_geocode_address.geocode)
# mcp.add_tool(convert_geocode_address.reverse_geocode)

# 初始化日志系统
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 避免重复添加 handler
if not logger.handlers:
    # 文件日志处理器
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "image_to_address.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # 日志格式
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

@mcp.tool()
def image_to_address(directory: str) -> Tuple[Dict[str, Tuple[float, float]], Dict[str, Tuple[str, str]]]:
    """
    从指定目录下的图片中读取地理坐标，转换为百度 BD09 坐标系后，通过逆地理编码获取地址和兴趣点信息。

    :param directory: 包含图片的目录路径
    :return: 字典，键为图片路径，值为 (地址, 兴趣点) 的元组
    :raises ValueError: 如果目录不存在或不合法
    """
    # 检查目录是否存在
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        raise ValueError(f"Invalid directory path: {directory}")

    logger.info(f"Reading image files from directory: {directory}")

    # 获取图像文件列表
    image_files = get_image_files.get_image_files(directory)
    if not image_files:
        logger.warning(f"No image files found in directory: {directory}")
        return {}

    logger.info(f"Found {len(image_files)} image files.")

    # 提取图像坐标
    wgs84_coords = read_image_coord.read_image_coord(image_files)
    if not wgs84_coords:
        logger.warning("No valid GPS coordinates found in the images.")
        return {}

    logger.info("Successfully extracted GPS coordinates.")

    # 初始化结果字典
    bd09_coords: Dict[str, Tuple[float, float]] = {}
    address_results: Dict[str, Tuple[str, str]] = {}

    # 转换坐标并进行逆地理编码
    for path in image_files:
        # 检查是否有有效坐标
        if path not in wgs84_coords:
            logger.warning(f"Missing GPS data for image: {path}")
            continue

        try:
            # 转换 WGS84 -> BD09
            bd09_coords[path] = convert_coord.wgs84_to_bd09(wgs84_coords[path])
        except Exception as e:
            logger.error(f"Coordinate conversion failed for {path}: {e}")
            continue

        # 逆地理编码
        try:
            address, poi = convert_geocode_address.reverse_geocode(bd09_coords[path])
            address_results[path] = (address or "未知地址", poi or "")
            time.sleep(0.25)  # 控制请求频率，避免超限
        except Exception as e:
            logger.error(f"Reverse geocoding failed for {path}: {e}")
            address_results[path] = ("未知地址", "")

    logger.info(f"Successfully processed {len(address_results)} images.")
    return bd09_coords, address_results


@mcp.tool()
def create_map_html(points: List[Dict[str, float]], output_path: str = './map.html') -> str:

    """
    生成带自定义标记的百度地图HTML文件
    :param points: 坐标点列表，格式[{"lng": ..., "lat": ...}, {"lng": ..., "lat": ...}]
    :param output_path: 输出文件路径（默认当前目录map.html），请使用英文路径
    """
    logger.info(f'开始生成地图，坐标点数量: {len(points)}')
    logger.info(f'输出路径: {output_path}')
    
    ak = '修改为自己的key'
    if not points:
        raise ValueError("坐标点列表不能为空")
    
    center = points[0]['lng'], points[0]['lat']
    logger.info(f'地图中心点坐标: {center}')
    
    points_js = ','.join([f'{{lng: {p["lng"]}, lat: {p["lat"]}}}' for p in points])
        
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <style type="text/css">
        body, html,#allmap {{width: 100%;height: 100%;overflow: hidden;margin:0;font-family:"微软雅黑";}}
        </style>    
        <script type="text/javascript" src="http://api.map.baidu.com/api?type=webgl&v=1.0&ak={ak}"></script>
        <script type="text/javascript" src="http://api.map.baidu.com/library/TrackAnimation/src/TrackAnimation_min.js"></script>

        <title>绘制轨迹</title>
    </head>
    <body>
        <div id="allmap"></div>
    </body>
    </html>
    <script type="text/javascript">
        // GL版命名空间为BMapGL
        // 按住鼠标右键，修改倾斜角和角度
        var bmap = new BMapGL.Map("allmap");    // 创建Map实例
        bmap.centerAndZoom(new BMapGL.Point({center[0]}, {center[1]}), 16);
        bmap.enableScrollWheelZoom(true);     // 开启鼠标滚轮缩放
        bmap.setTilt(50);      // 设置地图初始倾斜角

        var path = [{points_js}];

        var point = [];
        for (var i = 0; i < path.length; i++) {{
            var poi = new BMapGL.Point(path[i].lng, path[i].lat);
            point.push(poi);
            var marker = new BMapGL.Marker(poi); //创建标注
            bmap.addOverlay(marker); //将标注添加到地图中
        }}


        var pl = new BMapGL.Polyline(point,{{strokeColor:"blue", strokeWeight:6, strokeOpacity:0.5}});

        var trackAni = new BMapGLLib.TrackAnimation(bmap, pl, {{
            overallView: true, // 动画完成后自动调整视野到总览
            tilt: 30,          // 轨迹播放的角度，默认为55
            duration: 20000,   // 动画持续时长，默认为10000，单位ms
            delay: 3000        // 动画开始的延迟，默认0，单位ms
        }});

        trackAni.start();
    </script>
    '''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template.strip())
        
    logger.info('地图生成成功')

    return "Successfully write output html file in " + output_path


def main():
    logger.info("MCP 服务已启动")
    mcp.run("stdio")
    # image_path = "D:\\beijing_images"
    # image_path = "c:\\Users\\huayi\\Desktop\\智能计算与空间优化\\2025-04-24 Qwen-Agent\\images"
    # address_poi = image_to_address(image_path)
    # print(address_poi)

if __name__ == "__main__":
    main()
