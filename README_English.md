# Language Selection
* **[`简体中文`](https://github.com/AEBC08/EMCLK/blob/main/README.md)**
* **[`English`](https://github.com/AEBC08/EMCLK/blob/main/README_English.md)**

**If you need a version of C#, please go to: [_ ` AEBC08/EMCLK_For_CSharp `](https://github.com/AEBC08/EMCLK_For_CSharp)**

# EMCLK (Elegant Minecraft Launcher Kernel)
**This is a new _Minecraft Java_ edition launcher kernel based on _Python_, belonging to the _RATE studio_ team.** 
<img src="https://github.com/AEBC08/EMCLK/blob/main/RATEstudio_logo/RATEstudio.png" width="30%" height="30%">

## Developers
* **[`AEBC08`](https://github.com/AEBC08)** - _Lead Developer_
* **[`XiaoShuaiYo`](https://github.com/xiaoshuaiyo)** - _Co-Developer, Main Developer of the Launcher GUI_
* **[`RATE`](https://github.com/e2662020)** - _Co-Developer, Founder of the Studio_

### Acknowledgments
* **[`Xphost`](https://github.com/xphost008)** - _Provided help with the foundational development of the launcher kernel_

### Libraries Used
**Python Standard Libraries:**
* **[`json`](https://docs.python.org/3/library/json.html)** - _For parsing Minecraft's JSON to obtain various configuration parameters_
* **[`platform`](https://docs.python.org/3/library/platform.html)** - _To get detailed system information to ensure correct Minecraft launch_
* **[`os`](https://docs.python.org/3/library/os.html)** - _For file operations_
* **[`subprocess`](https://docs.python.org/3/library/subprocess.html)** - _To run Minecraft and receive its runtime logs_
* **[`uuid`](https://docs.python.org/3/library/uuid.html)** - _In conjunction with hashlib to generate UUID for Minecraft offline accounts_
* **[`hashlib`](https://docs.python.org/3/library/hashlib.html)** - _Used with uuid_
* **[`re`](https://docs.python.org/3/library/re.html)** - _For regular expression matching and string content replacement_
* **[`zipfile`](https://docs.python.org/3/library/zipfile.html)** - _For unzipping Natives_

### Example of Project Reference
**This project supports being directly referenced and then calling functions to launch Minecraft.  
Please note that all the comments in the code are in Chinese; you may choose to use a translator to translate them into Chinese.  
Here is a demonstration call:**

```python
import EMCLK

EMCLK.launch_minecraft("Your Java path", "Your .minecraft dir path", "Minecraft version name", 1024, "Player name")
```

**Explanation of the example:**
1. First, import the project.
2. Create a list-type variable named `log_list`.
3. Inherit the `IMCLKReturn` class and override the `return_log` function within the class.
4. Call the `launch_minecraft` function and pass the overridden class and other parameters into the function to launch Minecraft.  
**Explanation of `launch_minecraft` function parameters:**
* **`java_path`** - _Required parameter, str type, the absolute path of your Java executable file_
* **`game_path`** - _Required parameter, str type, the absolute path of your .minecraft folder_
* **`version_name`** - _Required parameter, str type, the name of the Minecraft version you want to launch, note that this name is the name inside the version folder_
* **`max_use_ram`** - _Required parameter, str and int type, the maximum allocated memory, unit 1MB, the default minimum is 256MB, please do not include the unit_
* **`player_name`** - _Required parameter, str type, player name_
* **`user_type`** - _Optional parameter, str type, user type, default value is Legacy (i.e., offline login)_
* **`auth_uuid`** - _Optional parameter, str type, login UUID, offline login can be omitted, entering it means customizing the UUID, the default is automatically generated based on the player name, please enter a UUID3 format UUID, which can be a standard UUID3 or a trimmed UUID3_
* **`access_token`** - _Optional parameter, str type, genuine account login token (Token), invalid for offline login_
* **`first_options_lang`** - _Optional parameter, str type, automatically modify the language on the first launch, the default value is zh_CN_
* **`options_lang`** - _Optional parameter, str type, automatically modify the language on launch, default is empty and does not automatically set the language_
* **`launcher_name`** - _Optional parameter, str type, launcher name, default value IMCLK_
* **`launcher_version`** - _Optional parameter, str type, launcher version, default 0.1145_
* **`return_methods`** - _Optional parameter, type and IMCLKReturn type, output method, can override the output of logs and JVM parameters and the way exceptions are thrown, the default value is IMCLKReturn, note that if the override parameter does not add the @staticmethod statement, only instances can be passed in, otherwise both the instance and the class itself can be passed in_
* **`out_jvm_params`** - _Optional parameter, bool type, output JVM parameters, modifying the return_methods parameter can override the output method, the default value is False_

### Diagrams (Partial)
<img src="https://github.com/AEBC08/EMCLK/blob/main/Diagram/Diagram.png" width="50%" height="50%">
<img src="https://github.com/AEBC08/EMCLK/blob/main/Diagram/Diagram1.png" width="50%" height="50%">

### Update Log
* **`2024.6.9`** - _Updated support for Forge Loader, NeoForged Loader, Quilt Loader, and mainstream Mod Loaders, supports unzipping Natives and setting Minecraft language on first launch, compatible with the latest and older versions of Minecraft, the lead developer has only tested versions from the latest Minecraft (1.20.6) to Minecraft 1.7.10, all of which can be launched normally_
* **`2024.?.?`** - _Updated support for Fabric Loader, only supports launching newer versions, does not support unzipping Natives yet_
* **`2024.?.?`** - _Wrote the basic part of the launcher, only supports launching newer versions, does not support unzipping Natives yet_
