# Windows 坐直提醒工具 (Posture Reminder)

这是一个基于 Python 开发的 Windows 桌面应用程序，灵感来源于 macOS 的 Dorso。它通过电脑摄像头实时监测你的坐姿，当你开始驼背或脖子前倾时，屏幕会逐渐变暗以提醒你坐直。

## 🌟 功能特点
- **完全本地运行**：使用 Google MediaPipe 最新的 Tasks API 进行轻量级的人体姿态估计，不连接网络，保护隐私。
- **渐进式提醒**：驼背越严重，屏幕变暗的程度越深，一旦坐直瞬间恢复明亮。
- **系统托盘运行**：程序静默隐藏在系统托盘（右下角），不占用任务栏空间。
- **一键校准**：随时右键点击托盘图标重新校准您的标准坐姿。
- **实时监控悬浮窗**：支持通过菜单开启一个置顶的无边框小窗口，显示摄像头画面并实时绘制人体骨骼关键点（如肩膀、面部等），方便您确认监控效果。悬浮窗支持鼠标自由拖拽。

## 🛠️ 安装与运行

1. 确保已安装 Python 环境 (建议 3.9 - 3.13)。
2. 创建并激活虚拟环境，然后安装依赖：
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```cmd
   python main.py
   ```
   *(注：首次运行时，程序会自动加载同目录下的 `pose_landmarker_lite.task` 模型文件)*

## 📖 使用说明
1. 启动程序后，**Windows 任务栏右下角（系统托盘）** 会出现一个图标（通常为电脑图标或蓝色方块）。
2. **端正坐好**，让摄像头能清晰看到你的面部和肩膀。
3. 右键点击该托盘图标，选择 **"重新校准 (坐直并点击)"**。
4. 此时程序已记录你的标准坐姿，当你头部下倾或驼背时，屏幕会自动变暗提醒。
5. 如果想查看摄像头的识别效果，可以在托盘菜单中选择 **"显示摄像头画面"**，画面可自由拖动，再次点击可隐藏。
6. 需要临时暂停时，点击 **"暂停监控"** 即可。

## 📦 打包与分发方案

如果你希望将此 Python 脚本打包为无需 Python 环境的独立可执行文件（`.exe` 或 `.app`），可以使用 `PyInstaller`。
由于项目中包含额外的资源文件（如 `pose_landmarker_lite.task` 模型文件和 `gifs/` 文件夹），在打包时需要特别注意资源的路径映射。

### 1. 资源路径适配说明 (必读)

在使用 PyInstaller 打包成单文件 (`--onefile`) 时，运行时的临时目录会变。为了让程序在打包后仍能找到模型和 GIF，请确保代码中使用的是安全的绝对路径。
*当前项目代码已做适配，参考逻辑如下：*
```python
import os
import sys

def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境与 PyInstaller 打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

# 使用示例
model_path = get_resource_path('pose_landmarker_lite.task')
gifs_dir = get_resource_path('gifs')
```

*(注意：你需要先在 `posture_tracker.py` 和 `indicator.py` 中应用此路径函数，才能完美支持单文件打包)*

### 2. Windows 平台打包方案

在 Windows 环境下，我们可以打包成一个隐藏控制台窗口的独立 `.exe` 程序。

**准备工作：**
```cmd
pip install pyinstaller
```

*(注意：如果你所在的路径包含中文，比如 `D:\dev\py\坐直提醒`，PyInstaller 在处理 PyQt5 的插件目录时可能会抛出 `Exception: Qt plugin directory '.../????/...' does not exist!` 乱码错误。建议将项目目录移动到一个**纯英文路径**下再进行打包)*

**执行打包命令：**

建议使用默认的目录模式（即不加 `--onefile`），因为 MediaPipe 包含了大量的动态链接库和底层 C 模块。如果打包成单文件，会导致程序每次启动时需要解压大量文件，启动极慢。

```cmd
pyinstaller --noconsole --add-data "pose_landmarker_lite.task;." --add-data "gifs;gifs" --exclude-module tensorflow --collect-all mediapipe main.py
```

**参数说明：**
- `--noconsole`: 运行时不显示黑色的 cmd 控制台窗口。
- `--add-data`: 附加资源文件。Windows 下格式为 `"源路径;目标目录"`（注意是用分号 `;` 分隔）。
- `--exclude-module tensorflow`: 排除 TensorFlow 依赖（MediaPipe 包含一些可选依赖，如果不排除，PyInstaller 会将其误包含进去，导致打包极慢且包体巨大）。
- `--collect-all mediapipe`: **(重要)** 强制收集 MediaPipe 库的所有隐藏子模块、二进制文件和数据。如果不加此参数，打包后的程序运行时会报 `ModuleNotFoundError: No module named 'mediapipe.tasks.c'` 错误。

*(如果你必须打包为单文件，可以加上 `--onefile` 参数，但请做好程序每次启动都需要等待 10 秒以上的心理准备)*

**产出：** 打包完成后，在 `dist/main/` 目录下会生成包含 `main.exe` 及其依赖的完整目录。将整个 `main` 文件夹发给别人，双击其中的 `main.exe` 即可运行。

### 3. macOS 平台打包方案

在 macOS 环境下，打包步骤类似，但路径分隔符和应用包结构有所不同。

**准备工作：**
在 macOS 终端中激活你的环境并安装：
```bash
pip install pyinstaller
```

**执行打包命令：**
```bash
pyinstaller --noconsole --add-data "pose_landmarker_lite.task:." --add-data "gifs:gifs" --collect-all mediapipe main.py
```

**参数说明：**
- `--add-data`: macOS 和 Linux 下使用冒号 `:` 分隔源路径和目标路径。
- `--collect-all mediapipe`: 解决 macOS 下同样的隐藏模块依赖问题。
- 打包后会生成一个 UNIX 可执行文件，但在 macOS 上，若要更好的用户体验（如设置图标、权限请求），建议打包为 `.app` 格式。

**打包为 macOS `.app` 包（推荐）：**
使用窗口模式打包，并排除不必要的依赖：
```bash
pyinstaller --windowed --add-data "pose_landmarker_lite.task:." --add-data "gifs:gifs" --exclude-module tensorflow --collect-all mediapipe main.py
```
这将在 `dist/` 目录下生成一个 `main.app`。

**macOS 权限注意事项：**
macOS 对摄像头权限控制非常严格。当你运行打包好的 `.app` 时：
1. 可能会被 Gatekeeper 拦截（提示未签名的开发者），需要在 `系统设置 -> 隐私与安全性` 中点击“仍要打开”。
2. 应用第一次尝试访问摄像头时，系统会弹出请求摄像头权限的确认框。如果拒绝了，需手动到隐私设置中为你的 `main.app` 勾选摄像头权限。

---

## 💻 技术栈
- **OpenCV**: 捕获摄像头视频流
- **MediaPipe (Tasks API)**: 提取面部和肩膀的关键点坐标进行姿态评估
- **PyQt5**: 实现系统托盘、多线程处理、全屏透明的变暗遮罩层以及可拖拽的实时监控悬浮窗
