# Steam Workshop 版：订阅后需一次安装

条目：[Rise of Nations EE 简体中文修复版](https://steamcommunity.com/sharedfiles/filedetails/?id=3824946614)。适用于实测的 Windows Steam 1.20；不是订阅即用。发布记录与范围见 [TESTING.md](TESTING.md)。

## 安装

1. 在 Steam 订阅并等下载完成，退出游戏及启动器。先还原其他直接覆盖汉化；不要让旧根目录文件掩盖模组。保留个人配置、存档和其他模组。
2. 从本分支下载 [Install-Workshop.ps1](tools/Install-Workshop.ps1)。在 PowerShell 中运行，替换为 Steam“管理 → 浏览本地文件”显示的真实游戏目录：

```powershell
& .\Install-Workshop.ps1 -GamePath 'D:\SteamLibrary\steamapps\common\Rise of Nations'
```

3. 通过 Steam 启动。在“工具与附加内容 → Steam 创意工坊”保留 `RON_zhCN_Compatibility <LOCAL>` 启用。如果订阅条目同时显示，两个条目指向同一份文件，不能把 LOCAL 当成多余的旧副本删除。修改启用状态后完整退出再启动。

脚本只建立 `mods/RON_zhCN_Compatibility` 到 Steam 实际下载目录的 Windows 目录联接；不复制资源、不修改游戏 EXE、存档或 rise2.ini，也不安装系统字体。Steam 更新会写入联接指向的同一目录，无需重复复制。脚本检查两款字体的 SHA-256，遇到已有真实本地文件夹会拒绝覆盖。支持 `-WhatIf` 预览。

要求正常 `steamapps/common/Rise of Nations` 布局，订阅下载位于同一个 Steam 库的 `steamapps/workshop/content/287450/3824946614`。移动游戏库后，应先卸载旧联接，再针对新路径安装。其他库布局、Linux/Proton 和多人联机尚未验证。若 PowerShell 被组织策略禁止运行脚本，请不要修改安全策略，可使用独立覆盖包。

## 停用与卸载

已知启动器限制：测试期间仍偶发点击 Play 后进程留在后台、没有窗口；恢复订阅联接后再次从 Steam 启动已成功。汉化包不包含启动器修复，不能保证消除此问题。若遇到该情况，先确认游戏已退出，再通过 Steam 重试，避免反复启动多个实例。

临时停用：在游戏内同时停用 LOCAL 和订阅条目，再完整重启；不要仅“重新加载资源”，部分早期 UI 有缓存。

卸载：退出游戏及启动器，运行下列命令移除联接，然后在 Steam 取消订阅或在游戏内禁用订阅条目。脚本仅删除联接本身，保留 Steam 下载目录、原版游戏文件和存档。

```powershell
& .\Install-Workshop.ps1 -GamePath 'D:\SteamLibrary\steamapps\common\Rise of Nations' -Remove
```

## 为什么需要引导

实测纯订阅虽然加载中文正文，却漏载启动阶段的字体和部分 UI；刷新资源也无法修复。保持下载文件不变，仅增加本地目录联接后，冷启动正常。这个做法让游戏按本地模组顺序加载同一份订阅资源。它不是对原版加载器的修改。

发布器还会忽略 `Data/Fonts` 子目录，因此 Workshop 打包将两款 OTF 放在 `Data/`，将 `OFL.txt`、`SOURCES.txt`、`ATTRIBUTION.txt` 放在模组根目录。字体引用是相对 Steam 库路径，不含作者机器的盘符或用户目录。

## 来源与许可

文本基于 xsgteamx/Rise-of-Nations-ZH-CN-Patch，保留繁体零售文本、宽宽汉化 / 3DM 补档来源说明，按上游声明的 CC BY-NC-SA 4.0 标注。改动见 [PR #1](https://github.com/xsgteamx/Rise-of-Nations-ZH-CN-Patch/pull/1)。

字体为未修改的 Noto Sans CJK SC Regular / Bold，官方 Sans2.004 标签，SIL OFL 1.1。字体许可证与文本许可证独立，下载包内附许可证和来源哈希。无需使用或分发微软字体。

启动器先于模组加载，Workshop 不包含 launcher_res；启动器保持英文。请勿叠加覆盖相同文本/字体资源的其他汉化。

## 维护与构建

```text
python tools/build_workshop.py workshop.zip --workshop-id 3824946614
```

ZIP 内 `RON_zhCN_Compatibility/` 是上传资源，安装脚本及准备说明位于目录外。不带 `--workshop-id` 可构建本地字体路径候选供新作者首次私密上传；取得新 ID 后必须修改安装脚本中的条目 ID，并按新 ID 重建，再进行订阅隔离测试。本项目更新同一条目，不能反复新建。

发布文件必须来自工作副本，避免通过运行中的联接编辑订阅下载或让 Steam 更新与发布同时发生。游戏发布器通常额外写入 `_publishinfo.txt`，不计入 144 个资源文件。
