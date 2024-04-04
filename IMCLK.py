import json
import platform
import os
import subprocess


def name_to_path(name):  # 将名字转换为路径函数
    parts = name.split(":")
    suffix = "jar" if name.find("@") == -1 else name[name.find("@"):]
    if len(parts) == 4:
        return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}-{parts[3]}.{suffix}"
    elif len(parts) == 3:
        return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}.{suffix}"
    else:
        raise Exception("[Error] Name cannot be converted to path")


def start_minecraft(java_path: str, game_path: str, version_name: str, max_use_ram: int, out_jvm_parameter=False):
    jvm_parameter = ""
    system_type = platform.system()  # 获取系统类型
    if system_type == "Windows":  # 判断是否为Windows
        jvm_parameter += f"\"{java_path}\""
        jvm_parameter += " -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump"
        if platform.release() == "10":
            jvm_parameter += " -Dos.name=\"Windows 10\""
            jvm_parameter += " -Dos.version=10.0"
        if "64" in platform.machine():
            jvm_parameter += " -Xms256M"
        else:
            jvm_parameter += " -Xss256M"
    elif system_type == "Linux":  # 判断是否为Linux
        jvm_parameter += f"{java_path}"
        jvm_parameter += " -Xms256M"
    elif system_type == "Darwin":  # 判断是否为Mac OS
        jvm_parameter += f"{java_path}"
        jvm_parameter += " -Xms256M"
        jvm_parameter += " -XstartOnFirstThread"
    jvm_parameter += f" -Xmx{max_use_ram}M"
    jvm_parameter += " -XX:+UseG1GC"
    jvm_parameter += " -XX:-UseAdaptiveSizePolicy"
    jvm_parameter += " -XX:-OmitStackTraceInFastThrow"
    jvm_parameter += " -Dfml.ignoreInvalidMinecraftCertificates=True"
    jvm_parameter += " -Dfml.ignorePatchDiscrepancies=True"
    jvm_parameter += " -Dlog4j2.formatMsgNoLookups=true"
    with open(f"{game_path}/versions/{version_name}/{version_name}.json", "r", encoding="utf-8") as version_json:  # 读取版本json
        version_json = json.loads(version_json.read())
    for arguments_jvm in version_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
        if type(arguments_jvm) is str:
            jvm_parameter += f" {arguments_jvm.replace(' ', '')}"
    jvm_parameter += f" {version_json.get('mainClass')}"  # 添加游戏主类
    for arguments_game in version_json.get("arguments").get("game"):  # 遍历json中的jvm参数
        if type(arguments_game) is str:
            jvm_parameter += f" {arguments_game.replace(' ', '')}"
    class_path = "\""
    for libraries in version_json.get("libraries"):  # 遍历依赖
        class_path += f"{game_path}/libraries/{name_to_path(libraries.get('name'))};"
    class_path += f"{game_path}/versions/{version_name}/{version_name}.jar\""
    jvm_parameter = jvm_parameter.replace("${classpath}", class_path)  # 把-cp参数内容换成拼接好的依赖路径
    jvm_parameter = jvm_parameter.replace("${classpath_separator}", ";")  # ClassPath分隔符
    jvm_parameter = jvm_parameter.replace("${library_directory}", f"\"{game_path}/libraries\"")  # 依赖文件夹路径
    jvm_parameter = jvm_parameter.replace("${assets_root}", f"\"{game_path}/assets\"")  # 资源文件夹路径
    jvm_parameter = jvm_parameter.replace("${assets_index_name}", version_json.get("assetIndex").get("id"))  # 资源索引id
    for natives_path in os.listdir(f"{game_path}/versions/{version_name}"):
        if "natives" in natives_path:
            jvm_parameter = jvm_parameter.replace("${natives_directory}", f"\"{game_path}/versions/{version_name}/{natives_path}\"")  # 依赖库文件夹路径
            break
    jvm_parameter = jvm_parameter.replace("${game_directory}", f"\"{game_path}/versions/{version_name}\"")  # 游戏文件存储路径
    jvm_parameter = jvm_parameter.replace("${launcher_name}", "IMCLK")  # 启动器名字
    jvm_parameter = jvm_parameter.replace("${launcher_version}", "1.145")  # 启动器版本
    jvm_parameter = jvm_parameter.replace("${version_name}", f"{version_name}")  # 版本名字
    jvm_parameter = jvm_parameter.replace("${version_type}", "release")  # 版本类型
    jvm_parameter = jvm_parameter.replace("${auth_player_name}", "ikun")  # 玩家名字
    jvm_parameter = jvm_parameter.replace("${user_type}", "Legacy")  # 登录方式
    jvm_parameter = jvm_parameter.replace("${auth_uuid}", "23332333233323332333233323332333")  # 唯一标识id
    jvm_parameter = jvm_parameter.replace("${auth_access_token}", "None")  # 正版登录令牌
    if out_jvm_parameter:
        return jvm_parameter  # 输出处理好的jvm参数
    else:
        shell_command = ""
        if system_type == "Windows":  # 判断是否为Windows
            with open("./Start_Minecraft.bat", "w", encoding="utf-8") as bat_file:  # 生成启动脚本
                bat_file.write(jvm_parameter)
                shell_command = os.path.abspath("./Start_Minecraft.bat")
        run_shell_command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # 启动游戏
        for get_log in iter(run_shell_command.stdout.readline, b''):
            out_log = get_log.decode("utf-8", "ignore").strip("\n")
            print(out_log)

