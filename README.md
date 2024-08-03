# 语言选择
* **[`简体中文`](https://github.com/AEBC08/EMCLK/blob/main/README.md)**
* **[`English`](https://github.com/AEBC08/EMCLK/blob/main/README_English.md)**
  
**如果你需要 C# 的版本, 请前往: [_`AEBC08/EMCLK_For_CSharp`](https://github.com/AEBC08/EMCLK_For_CSharp)**

# EMCLK (Elegant Minecraft Launcher Kernel)
**这是一个基于 _Python_ 的 _Minecraft Java_ 版本启动器内核，隶属于 _RATE studio_ 团队。**  
<img src="https://github.com/AEBC08/EMCLK/blob/main/RATEstudio_logo/RATEstudio.png" width="30%" height="30%">

## 开发者
* **[`AEBC08`](https://github.com/AEBC08)** - _主开发者_
* **[`XiaoShuaiYo`](https://github.com/xiaoshuaiyo)** - _次开发者，启动器GUI的主开发者_
* **[`RATE`](https://github.com/e2662020)** - _次开发者，工作室创始人_

### 鸣谢
* **[`Xphost`](https://github.com/xphost008)** - _为启动器内核的基础开发提供帮助_

### 引用的库
**Python 标准库:**
* **[`json`](https://docs.python.org/3/library/json.html)** - _用于解析 Minecraft 的 JSON 以获取各种配置参数_
* **[`platform`](https://docs.python.org/3/library/platform.html)** - _获取详细的系统信息以确保正确启动 Minecraft_
* **[`os`](https://docs.python.org/3/library/os.html)** - _进行文件等操作_
* **[`subprocess`](https://docs.python.org/3/library/subprocess.html)** - _运行 Minecraft 并接收其运行时日志_
* **[`uuid`](https://docs.python.org/3/library/uuid.html)** - _与 hashlib 结合使用，为 Minecraft 离线账户生成 UUID_
* **[`hashlib`](https://docs.python.org/3/library/hashlib.html)** - _与 uuid 一起使用_
* **[`re`](https://docs.python.org/3/library/re.html)** - _用于正则表达式匹配和字符串内容替换_
* **[`zipfile`](https://docs.python.org/3/library/zipfile.html)** - _用于解压 Natives_

### 引用本项目示例
**本项目支持被直接引用并调用函数启动 Minecraft  
以下是调用示例：**

```Python
import EMCLK

EMCLK.launch_minecraft("Your Java path", "Your .minecraft dir path", "Minecraft version name", 1024, "Player name")
```

**`launch_minecraft` 函数参数:**
* **`java_path`** - _必填参数，str 类型，你的 Java 可执行文件的绝对路径_
* **`game_path`** - _必填参数，str 类型，你的 .minecraft 文件夹的绝对路径_
* **`version_name`** - _必填参数，str 类型，你想要启动的 Minecraft 版本的名称，注意这个名称是版本文件夹内的名称_
* **`max_use_ram`** - _必填参数，str 和 int 类型，最大分配内存，单位为 1MB，默认最小值为 256MB，请不要包含单位_
* **`player_name`** - _必填参数，str 类型，玩家名称_
* **`user_type`** - _选填参数，str 类型，用户类型，默认值为 Legacy(即离线登录)_
* **`auth_uuid`** - _选填参数，str 类型，登录 UUID，离线登录可以省略，填写则意味着自定义 UUID，默认根据玩家名称自动生成 UUID，请输入 UUID3 格式的 UUID，可以是标准的 UUID3 或修剪后的 UUID3_
* **`access_token`** - _选填参数，str 类型，正版账号登录令牌(Token)，离线登录无效_
* **`first_options_lang`** - _选填参数，str 类型，首次启动时自动修改语言，默认值为 zh_CN_
* **`options_lang`** - _选填参数，str 类型，启动时自动修改语言，默认为空且不会自动设置语言_
* **`launcher_name`** - _选填参数，str 类型，启动器名称，默认值为 IMCLK_
* **`launcher_version`** - _选填参数，str 类型，启动器版本，默认为 0.1145_
* **`return_methods`** - _选填参数，type 和 IMCLKReturn 类型，输出方式，可以覆盖日志和JVM参数的输出以及异常抛出的方式，默认值为 IMCLKReturn ，注意如果覆盖参数没有添加 @staticmethod 声明只能传入实例，否则可以传入实例和类本身_
* **`out_jvm_params`** - _选填参数，bool 类型，输出JVM参数，修改 return_methods 参数可以覆盖输出方式，默认值为 False_

### 示意图 (部分)
<img src="https://github.com/AEBC08/EMCLK/blob/main/Diagram/Diagram.png" width="50%" height="50%">
<img src="https://github.com/AEBC08/EMCLK/blob/main/Diagram/Diagram1.png" width="50%" height="50%">

### 更新日志
* **`2024.6.9`** - _更新了对 Forge Loader、NeoForged Loader、Quilt Loader 以及主流 Mod Loader 的支持，支持解压 Natives 文件和首次启动时设置 Minecraft 语言，兼容最新和旧版本的 Minecraft ，主开发者只测试了从当前最新的 Minecraft(1.20.6)到 Minecraft 1.7.10 的版本，这些版本都可以正常启动_
* **`2024.?.?`** - _更新了对 Fabric Loader 的支持，目前只支持启动较新的版本，尚不支持解压 Natives 文件_
* **`2024.?.?`** - _编写了启动器的基础部分，目前只支持启动较新的版本，尚不支持解压 Natives 文件_
