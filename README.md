# 语言选择
* **[简体中文](https://github.com/AEBC08/IMCLK/blob/main/README.md)**
* **[English](https://github.com/AEBC08/IMCLK/blob/main/README_English.md)**

# IMCLK (IKun Minecraft Launcher Kernel)
**这是一个基于 _Python_ 的 _Minecraft Java_ 版本启动器内核，属于 _RATE studio_ 团队。**  
<img src="https://github.com/AEBC08/IMCLK/blob/main/RATEstudio_logio/RATEstudio.png" width="30%" height="30%">

## 开发者
* **[AEBC08](https://github.com/AEBC08)** - _主开发者_
* **[XiaoShuaiYo](https://github.com/xiaoshuaiyo)** - _次开发者，启动器GUI的主开发者_
* **[RATE](https://github.com/e2662020)** - _次开发者，工作室创始人_

### 鸣谢
* **[Xphost](https://github.com/xphost008)** - _为启动器内核的基础开发提供帮助_

### 引用的库
**Python 标准库:**
* **[json](https://docs.python.org/3/library/json.html)** - _解析 Minecraft JSON 配置_
* **[platform](https://docs.python.org/3/library/platform.html)** - _获取系统信息_
* **[os](https://docs.python.org/3/library/os.html)** - _文件操作_
* **[subprocess](https://docs.python.org/3/library/subprocess.html)** - _运行 Minecraft_
* **[uuid](https://docs.python.org/3/library/uuid.html)** - _生成 Minecraft 离线账户 UUID_
* **[hashlib](https://docs.python.org/3/library/hashlib.html)** - _用于密码学散列函数_
* **[re](https://docs.python.org/3/library/re.html)** - _正则表达式_
* **[zipfile](https://docs.python.org/3/library/zipfile.html)** - _解压 Natives_

### 引用本项目示例
**本项目支持被直接引用并调用函数启动 Minecraft。以下是调用示例：**

```python
import IMCLK

log_list = []

class Return(IMCLK.IMCLKReturn):
    @staticmethod
    def return_log(log: str):
        log_list.append(log)
        print(log)

IMCLK.launch_minecraft("Your Java path", "Your .minecraft dir path", "Minecraft version name", 1024, "Player name", return_methods=Return)
```

**示例解释:**
1. 引入本项目
2. 创建 `log_list` 变量
3. 继承 `IMCLKReturn` 类并重写 `return_log` 函数
4. 调用 `launch_minecraft` 函数启动 Minecraft

**`launch_minecraft` 函数参数:**
* **java_path** - _Java 可执行文件路径_
* **game_path** - _.minecraft 文件夹路径_
* **version_name** - _Minecraft 版本名称_
* **max_use_ram** - _最大内存分配 (MB)_
* **player_name** - _玩家名称_
* **user_type** - _用户类型 (默认 Legacy)_
* **auth_uuid** - _登录 UUID (可选)_
* **access_token** - _登录令牌 (可选)_
* **first_options_lang** - _首次启动语言 (默认 zh_CN)_
* **options_lang** - _启动语言 (可选)_
* **launcher_name** - _启动器名称 (默认 IMCLK)_
* **launcher_version** - _启动器版本 (默认 0.1145)_
* **return_methods** - _输出方式 (可重写)_
* **out_jvm_params** - _输出 JVM 参数 (可选)_

### 示意图 (部分)
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram.png" width="50%" height="50%">
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram1.png" width="50%" height="50%">

### 更新日志
* **2024.6.9** - _支持 Forge Loader、NeoForged Loader、Quilt Loader，兼容新旧 Minecraft 版本_
* **2024.?** - _支持 Fabric Loader，启动新版本_
* **2024.?** - _编写启动器基础部分，启动新版本_
