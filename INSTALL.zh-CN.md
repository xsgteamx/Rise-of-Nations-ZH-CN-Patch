# 安装与还原（Steam Extended Edition 1.20）

本版修复以 Steam build 14787288 为对照。其他版本尚未验证。
现有合理译文保持不变；命令、资源路径、快捷键名和纯占位符不会为了消除英文而被翻译。

## 安装

1. 退出游戏和启动器。在 Steam 属性 → 测试中选择“无”。
2. 首次安装前，将游戏目录的 `Data`、`conquest`、`scenario`、`tribes` 和
   `launcher_res/en` 备份到游戏目录之外。备份 `%APPDATA%/Microsoft Games/Rise of Nations/rise2.ini`。
   以前装过其他汉化时，先还原干净版本再备份，不要叠加不同汉化包。
3. 使用本修复版构建出的 ZIP，将其目录直接合并到 `steamapps/common/Rise of Nations`，
   替换对应文件。ZIP 顶层应直接包含 `Data`、`conquest`、`scenario`、`tribes`、`launcher_res`。
4. 启动游戏，确认主菜单、教学游戏和战役名称均为中文。

**不要只复制源码中的 `mods/Chinese` 后等待创意工坊自动启用。**
在测试的 1.20 安装中，该裸目录未出现在模组管理器，必须将其中内容合并到游戏根目录。
打包工具会自动处理目录和重复的 Data 文件，并排除未汉化的世界地图定义。

本包不包含也不改写 `rise2.ini`；窗口化、分辨率及个人存档保持原样。
不要同时启用另一份覆盖这些资源的语言模组。

若启动器的 Play 关闭后长期无游戏窗口，先退出卡住的进程，再从游戏目录启动
`riseofnations.exe`（快捷方式的“起始位置”也设为游戏目录）。本次测试中原版与汉化版
都出现过启动器交接停滞，而直接启动均能进入菜单；这不是所有机器通用的根因结论。

## 还原

退出游戏，将第 2 步备份的文件放回原位置。移除本包新增且原版没有的
`Data/Fonts/msjh.ttc`、`msjhbd.ttc`、`msyh.ttf`、`msyhbd.ttf`，不要删除原有字体。
如果使用过旧的 `mods/Chinese` 布局，也应先将该目录移出游戏目录，避免继续覆盖文件。
没有备份时可使用 Steam 的“验证游戏文件完整性”恢复原版受管理文件；它不会自动清理新增模组文件。

## 从源码构建与验证

需要 Python 3.10 或更新版本，仅使用标准库：

```text
python tools/validate.py
python -m unittest discover -s tests -v
python tools/validate.py --game-dir "D:/SteamLibrary/steamapps/common/Rise of Nations"
python tools/build.py Rise_of_Nations_ZH_CN_steam120.zip
```

`--game-dir` 必须指向**未打汉化的干净游戏目录**，否则可能把补丁与自身比较。
验证器只读取该目录，不上传或打包游戏原始文件。
构建命令拒绝覆盖已有 ZIP。仓库保留的 UTF-16 XML 和启动器旧编码不是单凭编码即可判定的错误；
校验会检查 XML 是否可解析，以及文件镜像、占位符、非文本属性和教程资源引用。

完整测试范围及限制见 `TESTING.md`。
