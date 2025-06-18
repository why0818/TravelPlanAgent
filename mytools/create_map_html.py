# create_map_html.py
from typing import List, Dict, Optional
import logging

def create_map_html(points: List[Dict[str, float]], output_path: str = './map.html') -> str:
    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        encoding='utf-8',
                        filename='C:/Users/huayi/Desktop/智能计算与空间优化/2025-04-24 Qwen-Agent/mytools/logs/map_generation.log')

    """
    生成带自定义标记的百度地图HTML文件
    :param points: 坐标点列表，格式[{"lng": ..., "lat": ...}, {"lng": ..., "lat": ...}]
    :param output_path: 输出文件路径（默认当前目录map.html），请使用英文路径
    """
    logging.info(f'开始生成地图，坐标点数量: {len(points)}')
    logging.info(f'输出路径: {output_path}')
    
    ak = '修改为自己的key'
    if not points:
        raise ValueError("坐标点列表不能为空")
    
    center = points[0]['lng'], points[0]['lat']
    logging.info(f'地图中心点坐标: {center}')
    
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
        
    logging.info('地图生成成功')

    return "Successfully write output html file in " + output_path

