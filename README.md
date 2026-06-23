# TypingGame
这是一个课程项目，现已结束更新。

# 最终版本说明
该版本已兼容electron打包后的桌面应用，可下载“打字游戏 Setup 0.0.0.exe”下载体验。其中游戏内存文件与存档导出文件在安装指顶的文件目录下“frontend\resources\backend\data”与“frontend\resources\backend\exports”同级目录文件夹log可查看运行日志，而serve.exe是后端服务程序文件。另外可下载项目根目录文件夹“extensionData”存放了用于测试的音效、字体以及文章等文件可供使用。使用说明后续将在视频网站上传使用视频，在此不做说明。

## BUG说明
serve.exe是在默认在端口5000运行的程序且没有占用后的兼容流程，故如发现后端启动失败请检查端口5000的占用情况；同理，若您运行该程序后发现端口5000持续被占用或者无法卸载该程序请在任务管理器kill掉serve.exe该程序。
如游玩过程中发现无法向输入卡输入内容，请先检查中英文输入法问题，然后若游玩前有自定义用户信息等设置在同同一次运行中请关闭程序重启即可解决。

## 打包说明
推荐根据pyproject和request文件创建虚拟环境，然后执行指令```pyinstaller --onefile --distpath ./backend_dist serve.py```即可在项目根目录下“backend_dist”文件夹中获取“serve.exe”后端运行程序。
之后将之粘贴到前端根目录“frontend\backend”中，运行先指令```npm run build```后运行```npm run electron:build```运行无误后即可在“frontend\release”找到安装程序即打包成功


# 古早版本说明
若你看到此README文档该部分一级标题为“当前版本说明”，则你所获取的是这个项目的浅层框架，目前仅更新
- 确定Py环境并fronze为request与pyproject文档
- 明确Py后端以main测试py环境
- 明确Py后端主要实现在impl文件夹，而controller文件夹是抽象实现说明
- 明确Py后端初始化予配置环境交予脚本config.py实现
- 明确作为后端的运行脚本为serve.py提供
- 明确后续后端开发添置脚本需放入tool文件夹，当前已完成editTool与loggerTool两项基础工具无需更改
- 前端事项此版本暂未涉及
- 并提供后续测试所需要的额外数据在extenstionData文件夹中

# 予后端开发者说明
- 注意后续开发过程中需要添置的额外脚本请放入tool文件夹
- 当前gameController、config、main与serve脚本已经定型切勿做更改，不然与我联系
- 目前你的任务是完善controller、impl文件夹，辅助脚本在tool文件夹更新
- 更多后端开发说明请见exporedPlan文件夹内相应文档

# 予前端开发者说明
- 目前只完成了vue的基本temple实现，可以动工了
- 主要更新范围在compontents的具体实现以及配套的js脚本支持
- js脚本请更新在services、stores、utils三个文件夹内
- services主要是存放与后端api的连接，以及本地计算机txt、音频、图片路径互动
- stores主要是维护各个页面内缓存信息，诸如颜色主题、临时的数据记录（错词记录、游玩记录）等等
- utils则是散放各种你不知道如何归类的js文件脚本，统称为工具类即可
- 如有页面功能你感到困惑详请见exporedPlan文件夹内相应文档