import json
import platform
import os
import subprocess


class IMCLKException(Exception):
    def __init__(self, code="0xFFF", message="IMCLK Exception"):
        self.info = json.dumps({"Code": code, "Message": message}, ensure_ascii=False, indent=4)

    def __str__(self):
        return self.info


class FileError(IMCLKException):
    def __init__(self, code="0xFFE", message="File Error"):
        self.info = json.dumps({"Code": code, "Message": message}, ensure_ascii=False, indent=4)


class ConvertedError(IMCLKException):
    def __init__(self, code="0xFFD", message="Converted Error"):
        self.info = json.dumps({"Code": code, "Message": message}, ensure_ascii=False, indent=4)


class LaunchError(IMCLKException):
    def __init__(self, code="0xFFC", message="Launch Error"):
        self.info = json.dumps({"Code": code, "Message": message}, ensure_ascii=False, indent=4)


def name_to_path(name):  # 将名字转换为路径函数
    at_index = name.find('@')
    if at_index != -1:
        suffix = name[at_index + 1:]
        name = name[0:at_index]
    else:
        suffix = 'jar'
    parts = name.split(":")
    if len(parts) == 4:
        return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}-{parts[3]}.{suffix}"
    elif len(parts) == 3:
        return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}.{suffix}"
    else:
        raise ConvertedError("0x001", "Name cannot be converted to path")


def launch_minecraft(java_path: str, game_path: str, version_name: str, max_use_ram: int, out_jvm_params=False):
    jvm_params = ""
    jvm_params_list = []
    delimiter = ":"  # Class path分隔符
    system_type = platform.system()  # 获取系统类型
    if system_type == "Windows":  # 判断是否为Windows
        delimiter = ";"
        jvm_params_list.append(f"\"{java_path}\"")
        jvm_params_list.append(
            " -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump")
        if platform.release() == "10":
            jvm_params_list.append(" -Dos.name=\"Windows 10\"")
            jvm_params_list.append(" -Dos.version=10.0")
        if "64" in platform.machine():
            jvm_params_list.append(" -Xms256M")
        else:
            jvm_params_list.append(" -Xss256M")
    elif system_type == "Linux":  # 判断是否为Linux
        jvm_params_list.append(f"{java_path}")
        jvm_params_list.append(" -Xms256M")
    elif system_type == "Darwin":  # 判断是否为Mac OS
        jvm_params_list.append(f"{java_path}")
        jvm_params_list.append(" -XstartOnFirstThread")
        jvm_params_list.append(" -Xms256M")
    jvm_params_list.append(f" -Xmx{max_use_ram}M")
    jvm_params_list.append(" -XX:+UseG1GC")
    jvm_params_list.append(" -XX:-UseAdaptiveSizePolicy")
    jvm_params_list.append(" -XX:-OmitStackTraceInFastThrow")
    jvm_params_list.append(" -Dfml.ignoreInvalidMinecraftCertificates=True")
    jvm_params_list.append(" -Dfml.ignorePatchDiscrepancies=True")
    jvm_params_list.append(" -Dlog4j2.formatMsgNoLookups=true")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    with open(f"{game_path}/versions/{version_name}/{version_name}.json", "r", encoding="utf-8") as version_json:  # 读取版本json
        version_json = json.loads(version_json.read())
    if version_json.get("arguments").get("jvm") is not None:
        for arguments_jvm in version_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
            if type(arguments_jvm) is str:
                jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    main_class = ""
    if "${classpath}" in jvm_params:
        jvm_params += f" {version_json.get('mainClass')}"  # 添加游戏主类
    else:
        main_class = version_json.get('mainClass')
    for arguments_game in version_json.get("arguments").get("game"):  # 遍历json中的jvm参数
        if type(arguments_game) is str:
            jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    class_path = "\""
    class_path_list = []
    for libraries in version_json.get("libraries"):  # 遍历依赖
        class_path_list.append(f"{game_path}/libraries/{name_to_path(libraries.get('name'))}{delimiter}")
    class_path += "".join(class_path_list)
    class_path_list.clear()
    version_jar = ""
    if os.path.isfile(f"{game_path}/versions/{version_name}/{version_name}.jar"):
        if version_json.get("inheritsFrom") is not None:
            version_jar = f"{game_path}/versions/{version_name}/{version_name}.jar"
        else:
            class_path += f"{game_path}/versions/{version_name}/{version_name}.jar"
    asset_index_id = ""
    if version_json.get("assetIndex") is not None and version_json.get("assetIndex").get("id") is not None:  # 判断assetIndex id是否存在
        asset_index_id = version_json.get("assetIndex").get("id")
    # 判断是否是有Mod加载器的版本
    if version_json.get("inheritsFrom") is not None:
        if os.path.isdir(f"{game_path}/versions/{version_json.get('inheritsFrom')}"):
            # 读取对应版本的原版Json
            with open(f"{game_path}/versions/{version_json.get('inheritsFrom')}/{version_json.get('inheritsFrom')}.json", "r", encoding="utf-8") as open_game_json:
                game_json = json.loads(open_game_json.read())
            for arguments_jvm in game_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
                if type(arguments_jvm) is str and arguments_jvm.replace(' ', '') not in jvm_params:
                    jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
            jvm_params += "".join(jvm_params_list)
            jvm_params_list.clear()
            if main_class != "":
                jvm_params += f" {main_class}"  # 添加游戏主类
            for arguments_game in game_json.get("arguments").get("game"):  # 遍历json中的jvm参数
                if type(arguments_game) is str and arguments_game.replace(' ', '') not in jvm_params:
                    jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
            jvm_params += "".join(jvm_params_list)
            jvm_params_list.clear()
            for libraries in game_json.get("libraries"):  # 遍历依赖
                a_class_path = f"{game_path}/libraries/{name_to_path(libraries.get('name'))}{delimiter}"
                if a_class_path not in class_path:
                    class_path_list.append(a_class_path)
            class_path += "".join(class_path_list)
            class_path_list.clear()
            if not os.path.isfile(f"{game_path}/versions/{version_name}/{version_name}.jar") and version_jar == "":
                class_path += f"{game_path}/versions/{version_json.get('inheritsFrom')}/{version_json.get('inheritsFrom')}.jar"
            else:
                class_path += version_jar
            if asset_index_id == "":
                asset_index_id = game_json.get("assetIndex").get("id")
        else:
            raise FileError("0x002", "Unable to find the original game file. Please confirm that the original game has been installed correctly")
    jvm_params = jvm_params.replace("${classpath}", class_path.strip(";") + "\"")  # 把-cp参数内容换成拼接好的依赖路径
    jvm_params = jvm_params.replace("${library_directory}", f"\"{game_path}/libraries\"")  # 依赖文件夹路径
    jvm_params = jvm_params.replace("${assets_root}", f"\"{game_path}/assets\"")  # 资源文件夹路径
    jvm_params = jvm_params.replace("${assets_index_name}", asset_index_id)  # 资源索引id
    for natives_path in os.listdir(f"{game_path}/versions/{version_name}"):
        if "natives" in natives_path:
            jvm_params = jvm_params.replace("${natives_directory}", f"\"{game_path}/versions/{version_name}/{natives_path}\"")  # 依赖库文件夹路径
            break
    jvm_params = jvm_params.replace("${game_directory}", f"\"{game_path}/versions/{version_name}\"")  # 游戏文件存储路径
    jvm_params = jvm_params.replace("${launcher_name}", "IMCLK")  # 启动器名字
    jvm_params = jvm_params.replace("${launcher_version}", "1.145")  # 启动器版本
    jvm_params = jvm_params.replace("${version_name}", f"{version_name}")  # 版本名字
    jvm_params = jvm_params.replace("${version_type}", "release")  # 版本类型
    jvm_params = jvm_params.replace("${auth_player_name}", "ikun")  # 玩家名字
    jvm_params = jvm_params.replace("${user_type}", "Legacy")  # 登录方式
    jvm_params = jvm_params.replace("${auth_uuid}", "23332333233323332333233323332333")  # 唯一标识id
    jvm_params = jvm_params.replace("${auth_access_token}", "None")  # 正版登录令牌
    if out_jvm_params:
        print(jvm_params)
        return jvm_params  # 输出处理好的jvm参数
    else:
        shell_command = ""
        if system_type == "Windows":  # 判断是否为Windows
            with open("./Start_Minecraft.bat", "w", encoding="utf-8") as bat_file:  # 生成启动脚本
                bat_file.write(jvm_params)
                shell_command = os.path.abspath("./Start_Minecraft.bat")
        run_shell_command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # 启动游戏
        for get_log in iter(run_shell_command.stdout.readline, b''):
            out_log = get_log.decode("utf-8", "ignore").strip("\n")
            print(out_log)

