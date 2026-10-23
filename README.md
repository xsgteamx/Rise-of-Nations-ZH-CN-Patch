**文本许可：CC BY-NC-SA 4.0；Noto 字体许可：SIL OFL 1.1（见 Data/Fonts/OFL.txt）**
---
# Rise-of-Nations-ZH-CN-Patch
本项目为《Rise of Nations: Extended Edition》的非官方简体中文汉化补丁。
# Rise of Nations: Extended Edition 简体中文汉化补丁

本项目为《Rise of Nations: Extended Edition》的非官方简体中文汉化补丁。

## 📌 项目说明

- 本补丁基于 **繁体中文零售版文本** 制作  
- 承袭并整理自 **宽宽汉化 / 3DM 旧版补档文本**
- 汉化覆盖游戏主界面、菜单、单位、科技、战役文本等内容
- 本分支修复菜单错义、缺失文本及 Steam 1.20 兼容问题；验证范围见 [TESTING.md](TESTING.md)。全量自动对照不等于全部译文完成逐句精校。

## 📦 下载

👉 前往 [GitHub Release](https://github.com/xsgteamx/Rise-of-Nations-ZH-CN-Patch/releases) 页面获取最新版

## 📥 安装方法

1. 退出 Steam 测试分支  
   Steam → 库 → 右键《Rise of Nations: Extended Edition》→ 属性 → 测试 →  
   选择「无 – 退出所有测试计划」

2. 下载发布页中的独立安装 ZIP。GitHub 自动生成的 Source code ZIP 是源码包，并不是整理好的安装包。没有独立安装包时可使用下方命令构建。

3. 解压后将文件复制到 steamapps\common\Rise of Nations
4. 启动游戏

详细安装与还原方法见 [INSTALL.zh-CN.md](INSTALL.zh-CN.md)。本包包含汉化资源和字体，不包含游戏可执行文件、存档或 `rise2.ini`，不改变个人窗口化设置。

## 构建与本地对照

需要 Python 3.10 或更新版本，仅使用标准库：

```text
python tools/validate.py
python -m unittest discover -s tests -v
python tools/build.py Rise_of_Nations_ZH_CN_steam120.zip
python tools/validate.py --game-dir "D:/clean-reference"
python tools/audit_text.py --game-dir "D:/clean-reference" --output bilingual-review.csv
```

英文对照目录必须是未安装汉化的本地资源，不能与已打补丁的文件自身比较。对照导出覆盖 XML 正文、内嵌标记后的文字、可翻译属性及启动器 INI。数字和未译英文标记仅是待审候选，不会自动改写译文。内部英文名称、命令和路径需要保留。英文对照表供本地审校，不应提交到仓库。

## Steam Workshop

Workshop 版在 Steam 1.20 上需要订阅后运行一次本地引导，解决早期字体/UI 未加载；后续资源由 Steam 更新。详见 [安装、卸载与限制](WORKSHOP.zh-CN.md)。
