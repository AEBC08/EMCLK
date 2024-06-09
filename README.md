# Language
* **[简体中文](https://github.com/AEBC08/IMCLK/blob/main/README.md)**  
* **[English](https://github.com/AEBC08/IMCLK/blob/main/README_English.md)**
# IMCLK (IKun Minecraft Launcher Kernel)
**这是一个新的基于 _Python_ 的 _Minecraft Java_ 版本启动器内核  
该项目隶属于 _RATE studio_ 团队**  
<img src="https://github.com/AEBC08/IMCLK/blob/main/RATEstudio_logio/RATEstudio.png" width="30%" height="30%">
## 开发者
* **[[AEBC08](https://github.com/AEBC08)]: _主开发者，此启动器内核几乎都是这一个人开发的_**  
* **[[XiaoShuaiYo](https://github.com/xiaoshuaiyo)]: _次开发者，他是启动器GUI的主开发者_**  
* **[[RATE](https://github.com/e2662020)]: _次开发者，工作室开创者_**
### 鸣谢
* **[[Xphost](https://github.com/xphost008)]: _为此启动器内核的基础开发提供了帮助_**
### 引用的库
**Python 标准库:**
* **[[json](https://docs.python.org/3/library/json.html)]: _用于解析 Minecraft 的 JSON 来获取 Minecraft 的各种配置参数_**  
* **[[platform](https://docs.python.org/3/library/platform.html)]: _用于获取系统的详细信息以保证能够正确启动 Minecraft_**  
* **[[os](https://docs.python.org/3/library/os.html)]: _用于查看文件等操作_**  
* **[[subprocess](https://docs.python.org/3/library/subprocess.html)]: _用于运行 Minecraft 接收 Minecraft 的运行日志_**
* **[[uuid](https://docs.python.org/3/library/subprocess.html)]: _用于与 hashlib 配合生成 Minecraft 离线账户的 UUID_**
* **[[hashlib](https://docs.python.org/3/library/hashlib.html)]: _同 uuid_**
* **[[re](https://docs.python.org/3/library/re.html)]: _用于正则匹配替换字符串内容_**
* **[[zipfile](https://docs.python.org/3/library/zipfile.html)]: _用于解压 Natives_**
### 引用本项目示例
**本项目支持直接被引用然后再调用函数启动 Minecraft
以下是一个调用示范**
```Python
import IMCLK

log_list = []


class Return(IMCLK.IMCLKReturn):
    @staticmethod
    def return_log(log: str):
        log_list.append(log)
        print(log)


IMCLK.launch_minecraft(r"Your Java path", r"Your .minecraft dir path", "Minecraft version name", 1024, "Player name", return_methods=Return)
```
**本示例演示了如何引入本项目并且重写启动函数的日志输出部分
示例解释:
1.首先引入本项目
2.创建一个名为 log_list 的 list 类型的变量
3.继承 IMCLKReturn 类并且重写类中的 return_log 函数
4.调用 launch_minecraft 函数将重写的类等参数传入函数启动 Minecraft
launch_minecraft 函数的参数解释:**
* **[java_path]: _必填参数，str 类型，你的 Java 的可执行文件的绝对路径_**
* **[game_path]: _必填参数，str 类型，你的 .minecraft 文件夹的绝对路径_**
* **[version_name]: _必填参数，str 类型，你想要启动的 Minecraft 版本的名称，注意这个名称是 version 文件夹内的名称_**
* **[max_use_ram]: _必填参数，str 和 int 类型，最大分配的内存，单位1MB，默认最小是256MB，注意请不要带上单位_**
* **[player_name]: _必填参数，str 类型，玩家名称_**
* **[user_type]: _选填参数，str 类型，用户类型，默认值为 Legacy (即离线登录)_**
* **[auth_uuid]: _选填参数，str 类型，登录的UUID，离线登录可不填，填入即自定义UUID，默认自动根据玩家名称自动生成一个UUID，注意请填入一个UUID3格式的UUID，可以是标准的UUID3也可以是修剪后的UUID3_**
* **[access_token]: _选填参数，str 类型，正版账号登录令牌(Token)，离线登录填入无效_**
* **[first_options_lang]: _选填参数，str 类型，首次启动自动修改语言，默认值为 zh_CN_**
* **[options_lang]: _选填参数，str 类型，启动自动修改语言，默认留空不自动设置语言_**
* **[launcher_name]: _选填参数，str 类型，启动器名字，默认值 IMCLK_**
* **[launcher_version]: _选填参数，str 类型，启动器版本，默认 0.1145_**
* **[return_methods]: _选填参数，type 和 IMCLKReturn 类型，输出方式，可重写日志和 JVM 参数的输出还有异常的抛出方式，默认值为 IMCLKReturn，注意若重写参数不加上 @staticmethod 语句的话只能传入实例，反之可传入实例和类的本身_**
* **[out_jvm_params]: _选填参数，bool 类型，输出 JVM 参数，修改 return_methods 参数可重写输出方式，默认值为 False_**

### 示意图(部分)
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram.png" width="50%" height="50%">
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram1.png" width="50%" height="50%">

### 更新日志
* **[2024.6.9]: _更新了对于 Forge Loader、NeoForged Loader、Quilt Loader 等主流 Mod Loader 的支持，支持解压缩 Natives 与首次启动设置 Minecraft 语言，兼容了当前最新版乃至老版本的 Minecraft 版本，主开发者只测试了 Minecraft当前最新版(1.20.6) 至 Minecraft1.7.10 的版本，均可正常启动_**
* **[2024.?.?]: _更新了对于 Fabric Loader 的支持，仅支持启动较新的版本，暂不支持解压缩 Natives_**  
* **[2024.?.?]: _编写了启动器的基础部分，仅支持启动较新的版本，暂不支持解压缩 Natives_**
