import os
from typing import Optional

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI


# 读取环境变量，需要提前进行配置
qwen_api_key = os.environ.get('QWEN_API_KEY')
baidu_api_key = os.environ.get('BAIDU_MAP_API_KEY')
amap_api_key = os.environ.get('AMAP_API_KEY')

def init_agent_service():
    llm_cfg = {'model': 'qwen-plus','model_server':'dashscope','api_key':qwen_api_key}
    system = ('\
                ## [角色设定]\
                接下来，你需要扮演一个旅游规划智能助手。\
                ## [处理流程]\
                ### 第一步，调用[image_to_address]工具，你需要将指定图片路径转化为坐标及地址。\
                ### 第二步，调用[map_directions]工具，使用百度地图进行路线规划，输出具体的旅游行程和建议的交通工具，需要按时间顺序包含所有景点。\
                ### 第三步，调用[create_map_html]工具，生成地图可视化界面。 \
                ## [相关要求]\
                请根据上述指令操作，一步一步执行，并以中文回答，语言风格活泼生动。\
                ## [案例提示]\
                ### 输入：请你根据文件夹里图片所在的位置，帮我规划一个具体的旅游行程\
                ### 输出：\
                #### 第一天：中轴线文化核心\
                1. 天安门广场（6:00-7:30）\
                1.1. 观看升旗仪式（提前1-9天预约，查当日升旗时间）\
                1.2. 参观毛主席纪念堂（免费，需存包，周一闭馆）\
                2. 故宫博物院（8:30-13:00）\
                步行前往故宫博物院，5min\
                2.1. 提前7-10天官网预约，推荐路线：午门→太和殿→珍宝馆→神武门\
                3. 景山公园（13:30-14:30）\
                乘坐地铁前往，从XX号线XX站到XXX站，预计XXmin，3元\
                4. 什刹海夜游（18:00后）\
                4.1. 逛烟袋斜街，后海酒吧听现场音乐，晚餐推荐“南门涮肉”\
                #### 第二天：长城雄姿 + 奥运地标\
                1. 八达岭/慕田峪长城（7:00-13:00）\
                1.1. 八达岭：高铁30分钟（北京北站→八达岭），适合首次体验\
                1.2. 慕田峪：赞巴士直通车（往返80元），人少景美适合拍照\
                2. 鸟巢 & 水立方（17:00-20:00）\
                2.1. 傍晚灯光秀最佳，推荐登鸟巢顶美（门票50元），外部免费拍照\
                2.2. 晚餐选新奥购物中心“小吊梨汤”京菜\
                #### 第三天……\
              ')
    tools = [
        {
            "mcpServers": {
                # "amap-maps": {
                #     "command": "npx",
                #     "args": ["-y", "@amap/amap-maps-mcp-server"],
                #     "env": {
                #         "AMAP_MAPS_API_KEY": amap_api_key
                #     }
                # },
                "baidu-map": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@baidumap/mcp-server-baidu-map"
                    ],
                    "env": {
                        "BAIDU_MAP_API_KEY": baidu_api_key
                    }
                },
                "travel-plan-mcp": {
                    "command": "C:/Users/huayi/.conda/envs/openai_env/python.exe",
                    "args": [
                        "C:\\Users\\huayi\\Desktop\\智能计算与空间优化\\2025-04-24 Qwen-Agent\\mytools\\custom_mcp.py"
                    ]
                },
            }
        },
        # 'code_interpreter',
    ]
    file_root_path = 'C:\\Users\\huayi\\Desktop\\智能计算与空间优化\\2025-04-24 MCP案例'
    bot = Assistant(
        llm = llm_cfg,
        name = '旅游路线规划助手',
        description = '可以从文本和图片中提取信息，进行旅游规划的小助手',
        system_message = system,
        function_list = tools,
        # files= [os.path.join(file_root_path, 'readEXIF.pdf'),
        #         os.path.join(file_root_path, 'mapTools.py'),
        #         os.path.join(file_root_path, 'py_test.py'),
        #         os.path.join(file_root_path, 'getFilenames.py'),
        #         os.path.join(file_root_path, 'geoCoding.py')],
    )

    return bot

def app_gui():  
    # Define the agent
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            'D:\\images',
            'D:\\beijing_images',
        ]
    }
    WebUI(
        bot,
        chatbot_config=chatbot_config,
    ).run()


if __name__ == '__main__':
    app_gui()