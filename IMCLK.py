import json
import platform
import os
import subprocess
import uuid
import hashlib
import re
import zipfile


class IMCLKException(Exception):  # 核心的异常错误基类
    def __init__(self, error_type="Exception", error_code="0x001", error_message="IMCLK Exception"):
        # error_type是错误类型.error_code是错误代码,它是每一个错误的编号,每一个错误都不相同.error_message是详细错误信息
        self.info = json.dumps({"ErrorType": error_type, "ErrorCode": error_code, "ErrorMessage": error_message}, ensure_ascii=False, indent=4)

    def __str__(self):
        return self.info


class IMCLKReturn:  # 这个类定义了核心的种种内容输出的定义,可将其继承修改再传入启动参数,可实例化也可不实例化
    @staticmethod
    def return_log(log: str):  # 实时输出日志函数,每输出一行日志调用一次
        print(log)

    @staticmethod
    def return_jvm_params(jvm_params: str):  # 输出JVM参数函数
        print(jvm_params)

    @staticmethod
    def return_error_message(error_type: str, error_code: str, error_message: str):  # 输出异常错误函数
        raise IMCLKException(error_type=error_type, error_code=error_code, error_message=error_message)


def name_to_path(name: str, return_methods: type | IMCLKReturn=IMCLKReturn) -> str:  # 将名字转换为路径函数
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
        return_methods.return_error_message(error_type="Launch", error_code="0x002", error_message="Name cannot be converted to path")


def name_to_uuid(name: str) -> uuid.UUID:  # 将玩家昵称转换为UUID3函数
    return uuid.UUID(bytes=hashlib.md5(f"OfflinePlayer:{name}".encode('utf-8')).digest()[:16], version=3)


def is_uuid(uuid_string: str) -> bool:  # 检测一个字符串是否为UUID3函数
    try:
        return True if uuid.UUID(uuid_string, version=3).version == 3 else False
    except ValueError:
        return False


def unzip(zip_path: str, unzip_path: str):  # 解压文件函数
    zip_object = zipfile.ZipFile(zip_path)
    for file in zip_object.namelist():
        zip_object.extract(file, unzip_path)
    zip_object.close()


def launch_minecraft(java_path: str, game_path: str, version_name: str, max_use_ram: str | int, player_name: str, user_type: str="Legacy", auth_uuid="", access_token: str="None", first_options_lang: str = "zh_CN", options_lang: str ="", launcher_name: str="IMCLK", launcher_version: str="0.1145", return_methods: type | IMCLKReturn=IMCLKReturn, out_jvm_params=False):
    if bool(re.search(pattern=r"[^a-zA-Z0-9\-_+.]", string=player_name)):  # 检测用户名是否合法
        return_methods.return_error_message(error_type="Param", error_code="0x004", error_message="The player name cannot contain characters other than numbers, dash (minus), underline, plus, or English period")
    if auth_uuid != "" and not is_uuid(str(auth_uuid)):  # 检测是否定义了UUID,是否合法
        return_methods.return_error_message(error_type="Param", error_code="0x005", error_message="This is an incorrect UUID, which must consist of 32 hexadecimal integer characters")
    jvm_params = ""
    jvm_params_list = []
    delimiter = ":"  # Class path分隔符
    natives_list = []
    system_type = platform.system()  # 获取系统类型
    if system_type == "Windows":  # 判断是否为Windows
        system_type = "windows"
        delimiter = ";"
        jvm_params_list.append(f"\"{java_path}\"")
        jvm_params_list.append(" -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump")
        if platform.release() == "10":  # 判断Windows版本是否为10(11返回的也是10)
            jvm_params_list.append(" -Dos.name=\"Windows 10\" -Dos.version=10.0")
        if "64" in platform.machine():  # 判断是否为64位
            jvm_params_list.append(" -Xms256M")
        else:
            jvm_params_list.append(" -Xss256M")
    elif system_type == "Linux":  # 判断是否为Linux
        system_type = "linux"
        jvm_params_list.append(f"{java_path} -Xms256M")
    elif system_type == "Darwin":  # 判断是否为Mac OS
        system_type = "osx"
        jvm_params_list.append(f"{java_path}")
        jvm_params_list.append(" -XstartOnFirstThread -Xms256M")
    jvm_params_list.append(f" -Xmx{max_use_ram}M -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    with open(f"{game_path}/versions/{version_name}/{version_name}.json", "r", encoding="utf-8") as version_json:  # 读取版本json
        version_json = json.loads(version_json.read())
    if version_json.get("arguments") is not None:
        if version_json.get("arguments").get("jvm") is not None:
            for arguments_jvm in version_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
                if type(arguments_jvm) is str:
                    if "${classpath_separator}" in arguments_jvm:  # 这个判断针对NeoForged的,为-p参数的依赖两边加双引号
                        jvm_params_list.append(f" \"{arguments_jvm.replace(' ', '')}\"")
                    else:
                        jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
    else:
        if version_json.get("minecraftArguments") is not None:
            jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    main_class = ""
    if "${classpath}" in jvm_params:
        jvm_params += f" {version_json.get('mainClass')}"  # 添加游戏主类
    else:
        main_class = version_json.get('mainClass')
    if version_json.get("arguments") is not None:
        for arguments_game in version_json.get("arguments").get("game"):  # 遍历json中的jvm参数
            if type(arguments_game) is str:
                jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
    else:
        if version_json.get("minecraftArguments") is not None:
            jvm_params_list.append(f" {version_json.get('minecraftArguments')}")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    class_path = "\""
    class_path_list = []
    natives_path_cache_list = []
    for libraries in version_json.get("libraries"):  # 遍历依赖
        class_path_list.append(f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}{delimiter}")
        if libraries.get("natives") is not None and libraries.get("natives").get(system_type) is not None:
            natives_path = os.path.dirname(f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}")
            if os.path.dirname(natives_path) not in natives_path_cache_list:
                for natives in os.listdir(natives_path):
                    if "natives" in natives:
                        natives_list.append(f"{natives_path}/{natives}")
                natives_path_cache_list.append(os.path.dirname(natives_path))
    natives_path_cache_list.clear()
    class_path += "".join(class_path_list)
    class_path_list.clear()
    version_jar = ""
    if os.path.isfile(f"{game_path}/versions/{version_name}/{version_name}.jar"):
        version_jar = f"{game_path}/versions/{version_name}/{version_name}.jar"
        if version_json.get("inheritsFrom") is None:
            class_path += f"{game_path}/versions/{version_name}/{version_name}.jar"
    asset_index_id = ""
    if version_json.get("assetIndex") is not None and version_json.get("assetIndex").get("id") is not None:  # 判断assetIndex id是否存在
        asset_index_id = version_json.get("assetIndex").get("id")
    if version_json.get("inheritsFrom") is not None:  # 判断是否是有Mod加载器的版本
        find_version = False
        for game_versions in os.listdir(f"{game_path}/versions"):
            with open(f"{game_path}/versions/{game_versions}/{game_versions}.json", "r", encoding="utf-8") as open_game_json:
                game_json = json.loads(open_game_json.read())
            if game_json.get("id") == version_json.get("inheritsFrom"):
                find_version = True
                if game_json.get("arguments") is not None:
                    for arguments_jvm in game_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
                        if type(arguments_jvm) is str and arguments_jvm.replace(' ', '') not in jvm_params:
                            jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
                else:
                    if game_json.get("minecraftArguments") is not None and " -Djava.library.path=${natives_directory} -cp ${classpath}" not in jvm_params:
                        jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
                jvm_params += "".join(jvm_params_list)
                jvm_params_list.clear()
                if main_class != "":
                    jvm_params += f" {main_class}"  # 添加游戏主类
                if game_json.get("arguments") is not None:
                    for arguments_game in game_json.get("arguments").get("game"):  # 遍历json中的jvm参数
                        if type(arguments_game) is str and arguments_game.replace(' ', '') not in jvm_params:
                            jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
                else:
                    if game_json.get("minecraftArguments") is not None and game_json.get("minecraftArguments") not in jvm_params:
                        jvm_params_list.append(f" {game_json.get('minecraftArguments')}")
                jvm_params += "".join(jvm_params_list)
                jvm_params_list.clear()
                for libraries in game_json.get("libraries"):  # 遍历依赖
                    a_class_path = f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}{delimiter}"
                    if a_class_path not in class_path:
                        class_path_list.append(a_class_path)
                    if libraries.get("natives") is not None and libraries.get("natives").get( system_type) is not None:
                        natives_path = os.path.dirname(f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}")
                        if os.path.dirname(natives_path) not in natives_path_cache_list:
                            for natives in os.listdir(natives_path):
                                if "natives" in natives and natives not in natives_list:
                                    natives_list.append(f"{natives_path}/{natives}")
                            natives_path_cache_list.append(os.path.dirname(natives_path))
                natives_path_cache_list.clear()
                class_path += "".join(class_path_list)
                class_path_list.clear()
                if not os.path.isfile(f"{game_path}/versions/{version_name}/{version_name}.jar") and version_jar == "":
                    class_path += f"{game_path}/versions/{version_json.get('inheritsFrom')}/{version_json.get('inheritsFrom')}.jar"
                else:
                    class_path += version_jar
                if asset_index_id == "":
                    asset_index_id = game_json.get("assetIndex").get("id")
                break
        if not find_version:
            return_methods.return_error_message(error_type="File", error_code="0x003", error_message="Unable to find the original game file. Please confirm that the original game has been installed correctly")
    jvm_params = jvm_params.replace("${classpath}", class_path.strip(";") + "\"")  # 把-cp参数内容换成拼接好的依赖路径
    jvm_params = jvm_params.replace("${library_directory}", f"\"{game_path}/libraries\"", 1)  # 依赖文件夹路径
    jvm_params = jvm_params.replace("${assets_root}", f"\"{game_path}/assets\"")  # 资源文件夹路径
    jvm_params = jvm_params.replace("${assets_index_name}", asset_index_id)  # 资源索引id
    find_natives_dir = False
    for natives_path in os.listdir(f"{game_path}/versions/{version_name}"):
        if "natives" in natives_path:
            jvm_params = jvm_params.replace("${natives_directory}", f"\"{game_path}/versions/{version_name}/{natives_path}\"")  # 依赖库文件夹路径
            find_natives_dir = True
            break
    if not find_natives_dir:
        os.makedirs(f"{game_path}/versions/{version_name}/natives-{system_type}")
        for native_path in natives_list:
            unzip(zip_path=native_path, unzip_path=f"{game_path}/versions/{version_name}/natives-{system_type}")
        for not_native in os.listdir(f"{game_path}/versions/{version_name}/natives-{system_type}"):
            if not not_native.endswith(".dll") and os.path.isfile(f"{game_path}/versions/{version_name}/natives-{system_type}/{not_native}"):
                os.remove(f"{game_path}/versions/{version_name}/natives-{system_type}/{not_native}")
        jvm_params = jvm_params.replace("${natives_directory}", f"{game_path}/versions/{version_name}/natives-{system_type}")  # 依赖库文件夹路径
    if not find_natives_dir or options_lang != "":
        options_contents = lang = f"lang:{first_options_lang}"
        if options_lang != "":
            lang = f"lang:{options_lang}"
        if os.path.isfile(f"{game_path}/versions/{version_name}/options.txt"):
            with open(f"{game_path}/versions/{version_name}/options.txt", "r", encoding="utf-8") as options:
                options_contents = options.read()
            options_contents = re.sub(r"lang:\S+", lang, options_contents)
        with open(f"{game_path}/versions/{version_name}/options.txt", "w", encoding="utf-8") as options:
            options.write(options_contents)
    natives_list.clear()
    jvm_params = jvm_params.replace("${game_directory}", f"\"{game_path}/versions/{version_name}\"")  # 游戏文件存储路径
    jvm_params = jvm_params.replace("${launcher_name}", launcher_name)  # 启动器名字
    jvm_params = jvm_params.replace("${launcher_version}", launcher_version)  # 启动器版本
    jvm_params = jvm_params.replace("${version_name}", version_name)  # 版本名字
    jvm_params = jvm_params.replace("${version_type}", version_json.get("type"))  # 版本类型
    jvm_params = jvm_params.replace("${auth_player_name}", player_name)  # 玩家名字
    jvm_params = jvm_params.replace("${user_type}", user_type)  # 登录方式
    if user_type == "Legacy":  # 离线模式设置唯一标识id
        if auth_uuid == "":
            jvm_params = jvm_params.replace("${auth_uuid}", name_to_uuid(player_name).hex)
        else:
            jvm_params = jvm_params.replace("${auth_uuid}", auth_uuid)
    jvm_params = jvm_params.replace("${auth_access_token}", access_token)  # 正版登录令牌
    jvm_params = jvm_params.replace("${user_properties}", "{}")  # 老版本的用户配置项
    jvm_params = jvm_params.replace("${classpath_separator}", delimiter)  # NeoForged的逆天参数之一,替换为Class path的分隔符就行了
    jvm_params = jvm_params.replace("${library_directory}", f"{game_path}/libraries")  # NeoForged的逆天参数之二,获取依赖文件夹路径
    if version_jar != "":
        jvm_params = jvm_params.replace("${primary_jar_name}", os.path.basename(version_jar))  # NeoForged的逆天参数之三,替换为游戏本体JAR文件名就行了
    if out_jvm_params:
        return_methods.return_jvm_params(jvm_params=jvm_params)
    else:
        shell_command = ""
        if system_type == "windows":  # 判断是否为Windows
            with open("./LaunchMinecraft.bat", "w", encoding="utf-8") as bat_file:  # 生成启动脚本
                bat_file.write(jvm_params)
                shell_command = os.path.abspath("./LaunchMinecraft.bat")
        run_shell_command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # 启动游戏
        for get_log in iter(run_shell_command.stdout.readline, b''):
            return_methods.return_log(log=get_log.decode(encoding="utf-8", errors="ignore").strip("\n"))

