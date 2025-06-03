# BiliDanmakuDiff Bilibili弹幕比对工具

项目本身可独立使用，但最初设计是和[BiliDMProtobufDownloader](https://github.com/Mikuoso/ProtobufCSV2XML)、[ProtobufCSV2XML](https://github.com/Mikuoso/ProtobufCSV2XML)搭配使用。

## 功能描述
本工具基于Python 3.10，用于比较两个B站标准XML格式的弹幕文件，找出基准文件中存在但对比文件中缺失的弹幕，并生成包含这些差异弹幕的新XML文件。

### 📌 功能特性 
- **时间容差**：支持时间容差设置（单位：秒）
- **内容对比**：结合时间+内容的双重校验机制
- **弹幕处理**：采用二分查找算法优化对比效率

### ⚙️ 配置说明
编辑脚本中的用户配置区：
```python
USER_CONFIG = {
    # 输入文件配置
    "INPUT_FILES":{
        "BASE_PATH": r"base.xml",       # 基准文件（原始弹幕）
        "COMPARE_PATH": r"compare.xml", # 对比文件（待比较弹幕）
    },
    
    "OUTPUT_PATH": r"diff_output.xml",  # 差异文件输出路径
    
    "TIME_TOLERANCE": 0.000,            # 时间匹配容差（秒）
    
    "LOG_LEVEL": logging.INFO,          # 日志级别(DEBUG/INFO/WARNING/ERROR)
}
```
## 未来计划
本项目最初是为《【高清修复】东方幻想万华镜全集》补档工作而设计，尽管现已结束补档工作，但本项目将继续作为练手作继续练习开发、维护。
