[Setup]
; 应用基本信息
AppName=坐姿提醒
AppVersion=1.0.0
AppPublisher=Posture Reminder
AppPublisherURL=https://shaorange.com/
AppSupportURL=https://shaorange.com/
AppUpdatesURL=https://shaorange.com/
; 默认安装目录
DefaultDirName={autopf}\Posture Reminder
; 禁用选择目标位置页面，通常可以启用，这里为了简单默认启用
DisableProgramGroupPage=yes
; 卸载图标和信息
UninstallDisplayIcon={app}\logo.ico
; 输出安装包的设置
OutputDir=D:\dev\py\posture_reminder\setup_output
OutputBaseFilename=PostureReminder_Setup
; 安装包图标
SetupIconFile=D:\dev\py\posture_reminder\logo.ico
; 安装向导左侧的大图和右上角的小图 (可选，如果以后有可以加上)
; WizardImageFile=...
; WizardSmallImageFile=...
; 软件信息
InfoBeforeFile=D:\dev\py\posture_reminder\README.md
; 压缩方式
Compression=lzma
SolidCompression=yes
; 需要管理员权限安装
PrivilegesRequired=admin

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; 复制 dist\main 目录下的所有文件及文件夹
Source: "D:\dev\py\posture_reminder\dist\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 复制生成的图标，以备快捷方式使用
Source: "D:\dev\py\posture_reminder\logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 创建开始菜单快捷方式
Name: "{autoprograms}\坐姿提醒"; Filename: "{app}\main.exe"; IconFilename: "{app}\logo.ico"
; 创建桌面快捷方式
Name: "{autodesktop}\坐姿提醒"; Filename: "{app}\main.exe"; Tasks: desktopicon; IconFilename: "{app}\logo.ico"
; 创建快速启动栏快捷方式
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\坐姿提醒"; Filename: "{app}\main.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\logo.ico"

[Run]
; 安装完成后提供运行选项
Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,坐姿提醒}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时清理可能产生的临时文件
Type: filesandordirs; Name: "{app}"
