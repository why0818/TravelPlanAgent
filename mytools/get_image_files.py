import os

def get_image_files(directory, extensions=('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
    """
    示例调用
    directory = 'C:\\Users\\huayi\\Desktop\\智能计算与空间优化\\2025-04-24 MCP案例\\images'
    images = get_image_files(directory)
    print(images)
    """
    image_files = []
    for f in os.listdir(directory):
        if f.lower().endswith(extensions):
            # 获取完整路径并添加到列表中
            full_path = os.path.join(directory, f)
            image_files.append(full_path)
    return image_files

