import xml.etree.ElementTree as ET
from collections import defaultdict
from bisect import bisect_left, bisect_right
import logging
import sys

# ————————————————————用户配置区————————————————————
USER_CONFIG = {
    # 输入文件配置
    "INPUT_FILES":{
        "BASE_PATH": r"path\to\the\base_file.xml", # 基准文件路径及名称
        "COMPARE_PATH": r"path\to\the\compare_file.xml", # 对比文件路径及名称
    },

    # 输出文件配置
    "OUTPUT_PATH": r"path\to\the\output_file.xml", # 输出路径及名称

    # 对比配置
    "TIME_TOLERANCE": 0.000, # 时间容差（单位：秒）

    # 日志配置
    "LOG_LEVEL": logging.DEBUG, # 日志等级
}
# ————————————————————初始化日志————————————————————
logging.basicConfig(
    level=USER_CONFIG["LOG_LEVEL"],
    format="[%(asctime)s][%(levelname)s]%(message)s (Lines:%(lineno)d)",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
# —————————————————————————————————————————————

def parse_xml(xml_path: str) -> ET.ElementTree:
    """解析XML"""
    try:
        return ET.parse(xml_path)
    except ET.ParseError as e:
        logging.error(f"XML解析错误：{e}（文件：{xml_path}）")
        raise
    except FileNotFoundError:
        logging.error(f"文件不存在：{xml_path}")
        raise

def build_contrast_index() -> dict:
    """构建用于数据对比的索引结构"""
    compare_file = USER_CONFIG["INPUT_FILES"]["COMPARE_PATH"]

    index = defaultdict(lambda: {"times": [], "counts": defaultdict(int)})
    try:
        for elem in parse_xml(compare_file).getroot().iterfind("d"):
            p_attr = elem.get("p")
            content = elem.text.strip()

            time_str, *_ = p_attr.split(",")
            raw_time = float(time_str)
            data = index[content]

            # 二分法插入
            idx = bisect_left(data["times"], raw_time)
            if idx >= len(data["times"]) or data["times"][idx] != raw_time:
                data["times"].insert(idx, raw_time)
            data["counts"][raw_time] += 1
    except Exception as e:
        logging.error(f"构建索引失败：{str(e)}")
    return index

def compare_danmaku() -> dict:
    """弹幕对比 可带时间容差"""
    src_counts = defaultdict(int)
    contrast = build_contrast_index()

    base_file = USER_CONFIG["INPUT_FILES"]["BASE_PATH"]
    try:
        for elem in parse_xml(base_file).getroot().iterfind('d'):
            p_attr = elem.get("p")
            content = elem.text.strip()

            time_str, *_ = p_attr.split(",", 1)
            src_counts[(time_str.strip(), content)] +=1
    except Exception as e:
        logging.error(f"原始文件处理失败：{str(e)}")
        return {}

    missing = defaultdict(int)
    tolerance = float(USER_CONFIG["TIME_TOLERANCE"])

    for (t_str, content), count in src_counts.items():
        try:
            t = float(t_str)
            data = contrast.get(content, {"times": [], "counts": defaultdict(int)})

            # 计算匹配区间
            left = bisect_left(data["times"], t - tolerance)
            right = bisect_right(data["times"], t + tolerance + 1e-9)

            matched = sum(data["counts"][t] for t in data["times"][left:right])
            if (diff := count - matched) > 0:
                missing[(t_str, content)] = diff
        except ValueError:
            continue

    return missing

def generate_diff_xml(missing: dict) -> int:
    """生成差异XML文件"""
    try:
        new_root = ET.Element("i")
        counter = 0

        base_file = USER_CONFIG["INPUT_FILES"]["BASE_PATH"]
        for elem in parse_xml(base_file).getroot().iterfind('d'):
            p_attr = elem.get("p")
            content = elem.text.strip()

            t_str = p_attr.split(",")[0].strip()
            key = (t_str, content)
            if missing.get(key, 0) > 0:
                new_elem = ET.Element("d", attrib=elem.attrib)
                new_elem.text = content
                new_root.append(new_elem)
                missing[key] -= 1
                counter += 1

        tree = ET.ElementTree(new_root)
        ET.indent(tree, space="  ")
        tree.write(USER_CONFIG["OUTPUT_PATH"],
                   encoding="utf-8",
                   xml_declaration=True)
        return counter

    except Exception as e:
        logging.error(f"XML生成失败：{str(e)}")
        return 0

if __name__ == "__main__":
    try:
        missing_danmaku = compare_danmaku()
        result = generate_diff_xml(missing_danmaku)
        logging.info(f"生成Diff弹幕数：{result}")
        logging.info(f"文件输出路径：{USER_CONFIG['OUTPUT_PATH']}")
    except Exception as e:
        logging.error(f"处理失败{str(e)}")
        sys.exit(1)