import json
import platform
import os
import subprocess
import uuid
import hashlib
import re
import zipfile
import threading
import requests


class EMCLKException(Exception):  # 核心的异常错误基类
    def __init__(self, error_type="Exception", error_code="0x001", error_message="IMCLK Exception"):
        # error_type是错误类型.error_code是错误代码,它是每一个错误的编号,每一个错误都不相同.error_message是详细错误信息
        self.info = json.dumps({"ErrorType": error_type, "ErrorCode": error_code, "ErrorMessage": error_message}, ensure_ascii=False, indent=4)

    def __str__(self):
        return self.info


class EMCLKReturn:  # 这个类定义了核心的种种内容输出的定义,可将其继承修改再传入启动参数,可实例化也可不实例化
    @staticmethod
    def return_launcher_log(log: str):  # 实时输出核心运行日志函数,每输出一行日志调用一次
        print(log)

    @staticmethod
    def return_minecraft_log(log: str):  # 实时输出游戏运行日志函数,每输出一行日志调用一次
        print(log)

    @staticmethod
    def return_minecraft_exit(exit_code: int):  # 当游戏退出时调用一次,返回退出码
        print(f"游戏已退出, 退出码为 {exit_code}")

    @staticmethod
    def return_jvm_params(jvm_params: str):  # 输出JVM参数函数
        print(jvm_params)

    @staticmethod
    def return_download(file_name: str, download_list: list, downloaded_list: list):
        print(file_name, f"{len(downloaded_list)}/{len(download_list)}")

    @staticmethod
    def return_error_message(error_type: str, error_code: str, error_message: str):  # 输出异常错误函数
        raise EMCLKException(error_type=error_type, error_code=error_code, error_message=error_message)


def name_to_path(name: str, return_methods: type | EMCLKReturn=EMCLKReturn) -> str:  # 将名字转换为路径函数
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
        return_methods.return_error_message(error_type="Launch", error_code="0x002", error_message="名称无法转换为路径")


def name_to_uuid(name: str) -> str:  # 将玩家昵称转换为UUID3函数
    return uuid.UUID(bytes=hashlib.md5(f"OfflinePlayer:{name}".encode('utf-8')).digest()[:16], version=3).hex


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


thread_stop = False
thread_lock = threading.Lock()
download_list_ = []
downloaded_list_ = []


def download_part(download_url: str, part_start: int, part_end: int, file_name: str):
    response = requests.get(download_url, headers={"Range": f"bytes={part_start}-{part_end}"}, stream=True)
    with open(file_name, "wb") as file_part:
        file_part.write(response.content)


def download_thread(download_list: list, return_methods: type | EMCLKReturn=EMCLKReturn):
    global downloaded_list_
    for download_task in download_list:
        download_task0 = download_task[0]
        download_task1 = download_task[1]
        if not thread_stop:
            path_name = ""
            with thread_lock:
                for dir_name in re.split(r"[\\/]", os.path.dirname(download_task1)):
                    path_name += f"{dir_name}/"
                    if not os.path.isdir(path_name):
                        os.makedirs(path_name)
            file_size = int(requests.head(download_task0).headers["Content-Length"])
            half_size = file_size // 2
            download_file = os.path.basename(download_task1)
            part1_path = f"{download_file}.part1"
            thread = threading.Thread(target=download_part, args=(download_task0, 0, half_size - 1, part1_path))
            thread.start()
            part2_path = f"{download_file}.part2"
            download_part(download_task0, half_size, file_size - 1, part2_path)
            thread.join()
            with open(download_task1, "wb") as save_file:
                for part in [part1_path, part2_path]:
                    with open(part, 'rb') as part_file:
                        save_file.write(part_file.read())
                    os.remove(part)
            downloaded_list_.append(download_file)
            return_methods.return_download(file_name=download_file, download_list=download_list_, downloaded_list=downloaded_list_)


def download_manager(download_list: list, max_thread: int, return_methods: type | EMCLKReturn=EMCLKReturn):
    global download_list_, downloaded_list_
    download_list_len = len(download_list)
    if download_list_len != 0:
        download_list_ = download_list.copy()
        downloaded_list_ = []
        max_thread = min(max_thread // 2, download_list_len)
        step = download_list_len // max_thread
        remainder = download_list_len % max_thread
        start = 0
        download_threads = []
        for download_task in range(max_thread):
            end = start + step + (download_task < remainder)
            thread = threading.Thread(target=download_thread, args=(download_list[start:end], return_methods))
            thread.start()
            download_threads.append(thread)
            start = end
        for wait_thread in download_threads:
            wait_thread.join()


def launch_minecraft(java_path: str, game_path: str, version_name: str, max_use_ram: str | int, player_name: str, user_type: str = "Legacy", auth_uuid="", access_token: str="None", first_options_lang: str="zh_CN", options_lang: str ="", launcher_name: str="EMCLK", launcher_version: str="0.1145", default_version_type: bool=False, custom_jvm_params: str = "", return_methods: type | EMCLKReturn=EMCLKReturn, completes_file: bool=True, out_jvm_params: bool=False):
    if bool(re.search(pattern=r"[^a-zA-Z0-9\-_+.]", string=player_name)):  # 检测用户名是否合法
        return_methods.return_error_message(error_type="参数", error_code="0x004", error_message="玩家名称不能包含数字、减号、下划线、加号或英文句号(小数点)以外的字符")
    if auth_uuid != "" and not is_uuid(str(auth_uuid)):  # 检测是否定义了UUID3,是否合法
        return_methods.return_error_message(error_type="参数", error_code="0x005", error_message="这是一个不正确的UUID3，它必须由32个十六进制整数字符组成")
    return_methods.return_launcher_log(log="准备启动中...")
    jvm_params = ""
    jvm_params_list = []
    delimiter = ":"  # Class path分隔符
    natives_list = []
    jvm_params_list.append(f"\"{java_path}\"")
    system_type = platform.system()  # 获取系统类型
    if system_type == "Windows":  # 判断是否为Windows
        return_methods.return_launcher_log(log="系统类型: Windows")
        system_type = "windows"
        delimiter = ";"
        jvm_params_list.append(" -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump")
        if platform.release() == "10":  # 判断Windows版本是否为10(11返回的也是10)
            jvm_params_list.append(" -Dos.name=\"Windows 10\" -Dos.version=10.0")
        if "64" in platform.machine():  # 判断是否为64位
            jvm_params_list.append(" -Xms256M")
        else:
            jvm_params_list.append(" -Xss256M")
    elif system_type == "Linux":  # 判断是否为Linux
        return_methods.return_launcher_log(log="系统类型: Linux")
        system_type = "linux"
        jvm_params_list.append(f" -Xms256M")
    elif system_type == "Darwin":  # 判断是否为MacOS(OSX)
        return_methods.return_launcher_log(log="系统类型: MacOS")
        system_type = "osx"
        jvm_params_list.append(f" -XstartOnFirstThread -Xms256M")
    else:
        return_methods.return_error_message(error_type="系统", error_code="0x006", error_message="您的系统不是Windows、Linux、MacOS(OSX)")
    jvm_params_list.append(f" -Xmx{max_use_ram}M -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    if custom_jvm_params != "":
        for a_jvm_param in custom_jvm_params.split(" "):
            if a_jvm_param != "":
                jvm_params_list.append(f" {a_jvm_param.replace(' ', '')}")
        jvm_params += "".join(jvm_params_list)
        jvm_params_list.clear()
    download_lists = []
    with open(f"{game_path}/versions/{version_name}/{version_name}.json", "r", encoding="utf-8") as version_json:  # 读取版本json
        version_json = json.loads(version_json.read())
    return_methods.return_launcher_log(log="当前版本 Json 文件加载完毕")
    if completes_file:
        return_methods.return_launcher_log(log="正在检查当前版本需要补全的依赖库文件...")
        for libraries in version_json.get("libraries"):  # 检测补全libraries
            libraries_path = f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}"
            if not os.path.isfile(libraries_path):
                download_lists.append([f"https://bmclapi2.bangbang93.com/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}", libraries_path])
        return_methods.return_launcher_log(log="当前版本需要补全的依赖库文件检查完毕")
    else:
        return_methods.return_launcher_log(log="已跳过文件完整性检查")
    find_version = False
    if version_json.get("inheritsFrom") is not None:  # 判断是否是有Mod加载器的版本
        return_methods.return_launcher_log(log="当前版本带有模组加载器, 正在加载原版游戏 Json 文件")
        for game_versions in os.listdir(f"{game_path}/versions"):
            with open(f"{game_path}/versions/{game_versions}/{game_versions}.json", "r", encoding="utf-8") as open_game_json:
                game_json = json.loads(open_game_json.read())
            if game_json.get("id") == version_json.get("inheritsFrom"):
                return_methods.return_launcher_log(log="原版游戏 Json 文件加载完毕")
                find_version = True
                if completes_file:
                    return_methods.return_launcher_log(log="正在检查原版游戏需要补全的依赖库文件...")
                    for libraries in game_json.get("libraries"):  # 检测补全libraries
                        libraries_path = f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}"
                        if not os.path.isfile(libraries_path):
                            download_lists.append([f"https://bmclapi2.bangbang93.com/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}", libraries_path])
                    return_methods.return_launcher_log(log="原版游戏需要补全的依赖库文件检查完毕")
                break
        if not find_version:
            return_methods.return_error_message(error_type="文件", error_code="0x003", error_message="找不到该版本的原版游戏, 请确认原版游戏已正确安装")
    if completes_file:
        if len(download_lists) != 0:
            max_thread = 64
            return_methods.return_launcher_log(log=f"共有 {len(download_lists)} 个需要补全的文件, 限制最大下载线程为 {max_thread} 个线程\n开始下载需要补全的文件...")
            download_manager(download_lists, max_thread, return_methods)  # 启动下载管理器
        else:
            return_methods.return_launcher_log(log="没有需要补全的文件")
    return_methods.return_launcher_log(log="正在拼接游戏启动参数...")
    if version_json.get("arguments") is not None:
        if version_json.get("arguments").get("jvm") is not None:
            for arguments_jvm in version_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
                if type(arguments_jvm) is str:
                    if "${classpath_separator}" in arguments_jvm:  # 这个判断针对NeoForged的,为-p参数的依赖两边加双引号
                        jvm_params_list.append(f" \"{arguments_jvm.replace(' ', '')}\"")
                    else:
                        jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
    elif version_json.get("minecraftArguments") is not None:
        jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
    jvm_params += "".join(jvm_params_list)
    jvm_params_list.clear()
    main_class = ""
    if "${classpath}" in jvm_params:
        jvm_params = jvm_params.replace("${classpath}", "${classpath}" + f" {version_json.get('mainClass')}")  # 添加游戏主类
    else:
        main_class = version_json.get("mainClass")
    version_jvm_params_list = []
    if version_json.get("arguments") is not None:
        for arguments_game in version_json.get("arguments").get("game"):  # 遍历json中的jvm参数
            if type(arguments_game) is str:
                version_jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
    elif version_json.get("minecraftArguments") is not None:
        version_jvm_params_list.append(f" {version_json.get('minecraftArguments')}")
    if not find_version:
        jvm_params += "".join(version_jvm_params_list)
        version_jvm_params_list.clear()
    class_path = "\""
    class_path_list = []
    natives_path_cache_list = []
    for libraries in version_json.get("libraries"):  # 遍历依赖
        libraries_path = f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}{delimiter}"
        class_path_list.append(libraries_path)
        if libraries.get("natives") is not None and libraries.get("natives").get(system_type) is not None:
            natives_path = os.path.dirname(libraries_path)
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
            class_path += version_jar
    asset_index_id = ""
    if version_json.get("assetIndex") is not None and version_json.get("assetIndex").get("id") is not None:  # 判断assetIndex id是否存在
        asset_index_id = version_json.get("assetIndex").get("id")
    if find_version:
        if game_json.get("arguments") is not None:
            for arguments_jvm in game_json.get("arguments").get("jvm"):  # 遍历json中的jvm参数
                if type(arguments_jvm) is str and arguments_jvm.replace(' ', '') not in jvm_params:
                    jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
        elif game_json.get("minecraftArguments") is not None and " -Djava.library.path=${natives_directory} -cp ${classpath}" not in jvm_params:
            jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
        jvm_params += "".join(jvm_params_list)
        jvm_params_list.clear()
        if main_class != "":
            jvm_params = jvm_params.replace("${classpath}", "${classpath} " + main_class)  # 添加游戏主类
        if game_json.get("arguments") is not None:
            for arguments_game in game_json.get("arguments").get("game"):  # 遍历json中的jvm参数
                if type(arguments_game) is str and arguments_game.replace(' ', '') not in jvm_params:
                    jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
        elif game_json.get("minecraftArguments") is not None and game_json.get("minecraftArguments") not in jvm_params:
            jvm_params_list.append(f" {game_json.get('minecraftArguments')}")
        jvm_params += "".join(jvm_params_list)
        jvm_params_list.clear()
        jvm_params += "".join(version_jvm_params_list)
        version_jvm_params_list.clear()
        for libraries in game_json.get("libraries"):  # 遍历依赖
            a_class_path = f"{game_path}/libraries/{name_to_path(name=libraries.get('name'), return_methods=return_methods)}{delimiter}"
            if a_class_path not in class_path:
                class_path_list.append(a_class_path)
            if libraries.get("natives") is not None and libraries.get("natives").get(system_type) is not None:
                natives_path = os.path.dirname(a_class_path)
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
    return_methods.return_launcher_log(log="游戏启动参数拼接完成\n正在替换对应游戏启动参数...")
    jvm_params = jvm_params.replace("${classpath}", class_path.strip(";") + "\"")  # 把-cp参数内容换成拼接好的依赖路径
    jvm_params = jvm_params.replace("${library_directory}", f"\"{game_path}/libraries\"", 1)  # 依赖文件夹路径
    jvm_params = jvm_params.replace("${assets_root}", f"\"{game_path}/assets\"")  # 资源文件夹路径
    jvm_params = jvm_params.replace("${assets_index_name}", asset_index_id)  # 资源索引id
    find_natives_dir = False
    for natives_path in os.listdir(f"{game_path}/versions/{version_name}"):
        if "natives" in natives_path:
            find_natives_dir = True
            jvm_params = jvm_params.replace("${natives_directory}", f"\"{game_path}/versions/{version_name}/{natives_path}\"")  # 依赖库文件夹路径
            break
    if not find_natives_dir:
        return_methods.return_launcher_log(log="正在解压本地运行库...")
        os.makedirs(f"{game_path}/versions/{version_name}/natives-{system_type}")
        for native_path in natives_list:
            unzip(zip_path=native_path, unzip_path=f"{game_path}/versions/{version_name}/natives-{system_type}")
        for not_native in os.listdir(f"{game_path}/versions/{version_name}/natives-{system_type}"):
            if not not_native.endswith(".dll") and os.path.isfile(f"{game_path}/versions/{version_name}/natives-{system_type}/{not_native}"):
                os.remove(f"{game_path}/versions/{version_name}/natives-{system_type}/{not_native}")
        jvm_params = jvm_params.replace("${natives_directory}", f"\"{game_path}/versions/{version_name}/natives-{system_type}\"")  # 运行库文件夹路径
        return_methods.return_launcher_log(log="本地运行库解压完毕")
    if not find_natives_dir or options_lang != "":
        return_methods.return_launcher_log(log="正在设置游戏默认语言...")
        options_contents = lang = f"lang:{first_options_lang}"
        if options_lang != "":
            lang = f"lang:{options_lang}"
        if os.path.isfile(f"{game_path}/versions/{version_name}/options.txt"):
            with open(f"{game_path}/versions/{version_name}/options.txt", "r", encoding="utf-8") as options:
                options_contents = options.read()
            options_contents = re.sub(r"lang:\S+", lang, options_contents)
        with open(f"{game_path}/versions/{version_name}/options.txt", "w", encoding="utf-8") as options:
            options.write(options_contents)
        return_methods.return_launcher_log(log="游戏默认语言设置完毕")
    natives_list.clear()
    jvm_params = jvm_params.replace("${game_directory}", f"\"{game_path}/versions/{version_name}\"")  # 游戏文件存储路径
    jvm_params = jvm_params.replace("${launcher_name}", f"\"{launcher_name}\"")  # 启动器名字
    jvm_params = jvm_params.replace("${launcher_version}", f"\"{launcher_version}\"")  # 启动器版本
    jvm_params = jvm_params.replace("${version_name}", f"\"{version_name}\"")  # 版本名字
    if default_version_type:
        jvm_params = jvm_params.replace("${version_type}", version_json.get("type"))  # 版本类型
    else:
        jvm_params = jvm_params.replace("${version_type}", f"\"{launcher_name}\"")  # 版本类型
    jvm_params = jvm_params.replace("${auth_player_name}", f"\"{player_name}\"")  # 玩家名字
    jvm_params = jvm_params.replace("${user_type}", user_type)  # 登录方式
    if user_type == "Legacy":  # 离线模式设置唯一标识id
        if auth_uuid.isspace():
            auth_uuid = name_to_uuid(player_name)
            return_methods.return_launcher_log(log=f"没有配置 UUID 自动生成 UUID 为: {auth_uuid}")
        jvm_params = jvm_params.replace("${auth_uuid}", auth_uuid)
    jvm_params = jvm_params.replace("${auth_access_token}", access_token)  # 正版登录令牌
    jvm_params = jvm_params.replace("${user_properties}", "{}")  # 老版本的用户配置项
    jvm_params = jvm_params.replace("${classpath_separator}", delimiter)  # NeoForged的逆天参数之一,替换为Class path的分隔符就行了
    jvm_params = jvm_params.replace("${library_directory}", f"{game_path}/libraries")  # NeoForged的逆天参数之二,获取依赖文件夹路径
    if version_jar != "":
        jvm_params = jvm_params.replace("${primary_jar_name}", os.path.basename(version_jar))  # NeoForged的逆天参数之三,替换为游戏本体JAR文件名就行了
    return_methods.return_launcher_log(log="游戏启动参数替换完成")
    if out_jvm_params:
        return_methods.return_launcher_log(log="输出游戏启动参数")
        return_methods.return_jvm_params(jvm_params=jvm_params)
    else:
        return_methods.return_launcher_log(log="正在生成游戏启动脚本...")
        file_suffix = "sh"
        if system_type == "windows":  # 判断是否为Windows
            file_suffix = "bat"
        with open(f"./LaunchMinecraft.{file_suffix}", "w", encoding="utf-8") as shell_file:  # 生成启动脚本
            shell_file.write(jvm_params)
        return_methods.return_launcher_log(log="游戏启动脚本生成完毕\n正在启动游戏...")
        shell_command = f"\"{os.path.abspath(f'./LaunchMinecraft.{file_suffix}')}\""
        run_shell_command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # 启动游戏
        for get_log in iter(run_shell_command.stdout.readline, b''):
            return_methods.return_minecraft_log(log=get_log.decode(encoding="utf-8", errors="ignore").strip("\n"))
        return_methods.return_minecraft_log(log=run_shell_command.communicate()[1].decode(encoding="utf-8", errors="ignore"))
        return_methods.return_minecraft_exit(exit_code=run_shell_command.returncode)

