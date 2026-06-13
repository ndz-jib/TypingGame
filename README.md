# TypingGame
这是一个正在更新的项目

# 当前版本说明
若你看到此README文档，则你所获取的是这个项目的浅层框架，目前仅更新
- 确定Py环境并fronze为request与pyproject文档
- 明确Py后端以main测试py环境
- 明确Py后端主要实现在impl文件夹，而controller文件夹是抽象实现说明
- 明确Py后端初始化予配置环境交予脚本config.py
- 明确作为后端的运行脚本为serve.py
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