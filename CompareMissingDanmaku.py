import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom


def extract_raw_keys(xml_file):
    """
    提取弹幕出现时间与弹幕内容并记录出现次数

    Args:
        xml_file (str): XML文件路径

    Returns:
        defaultdict: 键为元组（原始时间字符串，原始内容字符串），值为出现次数的计数器
    """
    try:
        # 解析XML文件
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # 使用默认字典记录每个键的出现次数
        key_counter = defaultdict(int)

        # 遍历所有<d>标签元素
        for elem in root.findall('d'):
            # 获取p属性和弹幕内容
            p_attr = elem.get('p')
            content = elem.text

            # 跳过无效条目
            if not p_attr or not content:
                continue

            # 分割属性值，提取原始时间戳（保留所有小数位）
            # 示例p属性格式："123.45600,1,25,16777215,1683871200,0,9d7a5b7,123456789,10"
            raw_time = p_attr.split(',')[0].strip()  # 第一个元素是时间戳

            # 保留原始内容格式（包括大小写和空格）
            raw_content = content.strip()  # 仅去除首尾空格

            # 创建组合键并计数
            key = (raw_time, raw_content)
            key_counter[key] += 1  # 相同键的计数器递增

        return key_counter

    except Exception as e:
        print(f"解析错误: {e}")
        return defaultdict(int)  # 返回空计数器


def compare_and_save_missing_danmaku(file1, file2, output_file):
    """
    以时间与内容作为参考依据对比弹幕出现次数并生成缺失文件

    Args:
        file1 (str): 原始文件
        file2 (str): 对比文件
        output_file (str): 生成缺失弹幕文件

    Returns:
        int: 缺失的弹幕数量
    """
    # 提取两个文件的计数器
    file1_counter = extract_raw_keys(file1)
    file2_counter = extract_raw_keys(file2)

    # 计算需要补充的弹幕（file1中存在但file2缺失的部分）
    missing_records = []
    for key, count1 in file1_counter.items():
        count2 = file2_counter.get(key, 0)
        missing_count = count1 - count2
        if missing_count > 0:
            # 将缺失的弹幕按出现次数展开成列表
            missing_records.extend([key] * missing_count)

    # 重新遍历原始文件以保持原始顺序
    tree = ET.parse(file1)
    root = tree.getroot()

    # 创建新的XML结构
    new_root = ET.Element("i")
    new_root.set("maxlimit", "1000")  # 保留原始根节点属性
    missing_count = 0

    # 遍历原始文件的所有弹幕
    for elem in root.findall('d'):
        p_attr = elem.get('p')
        content = elem.text
        if not p_attr or not content:
            continue

        # 生成当前弹幕的键
        current_time = p_attr.split(',')[0].strip()
        current_content = content.strip()
        current_key = (current_time, current_content)

        # 检查是否属于缺失弹幕
        if current_key in missing_records:
            # 复制原始节点到新XML
            new_d = ET.SubElement(new_root, "d")
            new_d.set("p", p_attr)  # 保留原始p属性
            new_d.text = content  # 保留原始内容

            missing_count += 1
            # 移除已处理的键（避免重复匹配）
            missing_records.remove(current_key)

    # 生成美化后的XML格式
    rough_xml = ET.tostring(new_root, encoding="utf-8")
    reparsed = minidom.parseString(rough_xml)
    # 设置缩进和换行格式
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    # 写入输出文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    return missing_count


if __name__ == "__main__":
    file1 = r"7+8.xml" #file1路径
    file2 =  r"user_f4065ed9.xml" #file2路径
    output_file = r"1.xml" #output_file文件名
    try:
        result = compare_and_save_missing_danmaku(file1, file2, output_file)
        print(f"缺失弹幕数: {result}")
        print(f"缺失弹幕已保存至文件: {output_file}")
    except Exception as e:
        print(f"运行出错:{str(e)}")
        print("请检查:")
        print("1.文件路径/文件名是否正确")
        print("2.文件是否为有效的XML格式")
        print("3.文件编码是否为UTF-8")