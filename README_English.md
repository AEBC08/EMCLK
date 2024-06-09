# Language
* **[Simplified Chinese](https://github.com/AEBC08/IMCLK/blob/main/README.md)**
* **[English](https://github.com/AEBC08/IMCLK/blob/main/README_English.md)**

# IMCLK (IKun Minecraft Launcher Kernel)
**This is a new _Minecraft Java_ version launcher kernel based on _Python_
The project is part of the _RATE studio_ team**  
<img src="https://github.com/AEBC08/IMCLK/blob/main/RATEstudio_logio/RATEstudio.png" width="30%" height="30%">

## Developers
* **[[AEBC08](https://github.com/AEBC08)]: _Main developer, almost the entire launcher kernel was developed by this individual_**
* **[[XiaoShuaiYo](https://github.com/xiaoshuaiyo)]: _Secondary developer, the main developer of the launcher GUI_**
* **[[RATE](https://github.com/e2662020)]: _Secondary developer, founder of the studio_**

### Acknowledgments
* **[[Xphost](https://github.com/xphost008)]: _Provided help with the basic development of this launcher kernel_**

### Referenced Libraries
**Python Standard Library:**
* **[[json](https://docs.python.org/3/library/json.html)]: _Used to parse Minecraft's JSON to obtain various configuration parameters of Minecraft_**
* **[[platform](https://docs.python.org/3/library/platform.html)]: _Used to obtain detailed system information to ensure correct launching of Minecraft_**
* **[[os](https://docs.python.org/3/library/os.html)]: _Used for file operations_**
* **[[subprocess](https://docs.python.org/3/library/subprocess.html)]: _Used to run Minecraft and receive Minecraft's operation logs_**
* **[[uuid](https://docs.python.org/3/library/subprocess.html)]: _Used in conjunction with hashlib to generate UUID for Minecraft offline accounts_**
* **[[hashlib](https://docs.python.org/3/library/hashlib.html)]: _Same as uuid_**
* **[[re](https://docs.python.org/3/library/re.html)]: _Used for regular expression matching to replace string content_**
* **[[zipfile](https://docs.python.org/3/library/zipfile.html)]: _Used to unzip Natives_**

### Example of Referencing This Project
**This project supports being directly referenced and then calling functions to launch Minecraft.
Below is a demonstration call:**
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
**This example demonstrates how to import this project and rewrite the log output part of the launch function.
Explanation of the example:
1. First, import the project.
2. Create a variable named log_list of type list.
3. Inherit the IMCLKReturn class and rewrite the return_log function in the class.
4. Call the launch_minecraft function and pass the rewritten class and other parameters into the function to launch Minecraft.
Explanation of the launch_minecraft function parameters:**
* **[java_path]: _Required parameter, str type, the absolute path of your Java executable file_**
* **[game_path]: _Required parameter, str type, the absolute path of your .minecraft folder_**
* **[version_name]: _Required parameter, str type, the name of the Minecraft version you want to launch, note that this name is the name inside the version folder_**
* **[max_use_ram]: _Required parameter, str and int types, the maximum allocated memory, unit 1MB, the default minimum is 256MB, please do not include the unit_**
* **[player_name]: _Required parameter, str type, player name_**
* **[user_type]: _Optional parameter, str type, user type, default value is Legacy (i.e., offline login)_**
* **[auth_uuid]: _Optional parameter, str type, login UUID, not required for offline login, if filled in, it customizes the UUID, default is automatically generated based on player name, please fill in a UUID3 format UUID, can be a standard UUID3 or a trimmed UUID3_**
* **[access_token]: _Optional parameter, str type, genuine account login token (Token), invalid for offline login_**
* **[first_options_lang]: _Optional parameter, str type, automatically change language on first launch, default value is zh_CN_**
* **[options_lang]: _Optional parameter, str type, automatically change language on launch, default left blank to not automatically set language_**
* **[launcher_name]: _Optional parameter, str type, launcher name, default value IMCLK_**
* **[launcher_version]: _Optional parameter, str type, launcher version, default 0.1145_**
* **[return_methods]: _Optional parameter, type and IMCLKReturn type, output method, can rewrite the output of logs and JVM parameters as well as the throwing of exceptions, default value is IMCLKReturn, note if rewriting parameters do not include the @staticmethod statement, only instances can be passed, otherwise both instances and the class itself can be passed_**
* **[out_jvm_params]: _Optional parameter, bool type, output JVM parameters, modifying return_methods parameter can rewrite the output method, default value is False_**

### Diagrams (Partial)
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram.png" width="50%" height="50%">
<img src="https://github.com/AEBC08/IMCLK/blob/main/Diagram/Diagram1.png" width="50%" height="50%">

### Update Log
* **[2024.6.9]: _Updated support for mainstream Mod Loaders such as Forge Loader, NeoForged Loader, Quilt Loader, etc., supports unzipping Natives and setting Minecraft language on first launch, compatible with the latest and older versions of Minecraft, the main developer only tested versions from the latest Minecraft (1.20.6) to Minecraft 1.7.10, all of which can be launched normally_**
* **[2024.?.?]: _Updated support for Fabric Loader, only supports launching newer versions, does not support unzipping Natives yet_**
* **[2024.?.?]: _Wrote the basic part of the launcher, only supports launching newer versions, does not support unzipping Natives yet_**
