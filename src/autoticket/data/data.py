import json
import os
from autoticket.data.route import route
from autoticket.data.config import DATA_FILE

class sys_data:
    def __init__(self):
        self.routes = []      # 存放 route 对象列表
        self.passengers = []  # 存放乘客信息
    
    def to_dict(self):
        """递归地将对象及其属性转换为字典"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                # 对列表中的每个元素尝试调用 to_dict，如果是基础类型则保持不变
                data[key] = [i.to_dict() if hasattr(i, 'to_dict') else i for i in value]
            elif hasattr(value, 'to_dict'):
                data[key] = value.to_dict()
            else:
                data[key] = value
        return data

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    def saveToFile(self, filename=DATA_FILE):
        """将当前数据保存为 JSON 文件"""
        try:
            parent_dir = os.path.dirname(filename)
            if parent_dir and not os.path.exists(parent_dir):
                # exist_ok=True 防止多线程环境下并发创建导致的错误
                os.makedirs(parent_dir, exist_ok=True)
                print(f"创建目录: {parent_dir}")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
            print(f"数据已成功保存至: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")

    def loadFromFile(filename=DATA_FILE):
        """从 JSON 文件加载数据并还原为对象结构"""
        sysdata = sys_data()
        if not os.path.exists(filename):
            print(f"文件 {filename} 不存在")
            return sysdata

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print("json.load:",type(data), data)
                sysdata.passengers = data.get("passengers", [])
                
                print("将字典列表还原为 route 对象列表")
                raw_routes = data.get("routes", [])
                for r_data in raw_routes:
                    new_route = route()
                    new_route.__dict__.update(r_data)
                    sysdata.routes.append(new_route)
            print(f"数据已成功从 {filename} 加载")
        except Exception as e:
            print(f"加载文件失败: {e}")

        return sysdata

         
