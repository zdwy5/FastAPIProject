# FastAPI AI项目 简介

## 目前进展
StoneAi: 
- 现阶段UI上的所有需求已经已经完成，包括最新的日程需求，但是没经过全面的测试
易拍居: 
- 对话流接口已经完成，后续可能需要改进，Eason那边提供更多的信息，现在只用到了详情接口的信息。
- 尽职调查报告Eason那边生成，需要AI侧给他提供数据
- Dify和Python服务需要部署到客户服务器上，已经完成了Docker的离线部署，其他两个暂未部署


## 部署和启动
目前只需要一个外部mysql服务即可成功启动项目
部分接口执行会依赖一些初始化数据,可自行去src/db/ddl/dml.sql 中查看，如果不迁移服务器的话，服务器上的mysql就有完整的数据

**需要根据.env.template 创建一个.env文件**

服务器的该路径下有 .env 配置文件和历史镜像 /www/wwwroot/ricDocker

服务器连接信息：
**Agent服务器（腾讯云-广州-Dify）** IP：[1.12.43.211](http://1.12.43.211) 
账号：ubuntu 密码：Cu28eRe9C+v9v5uT%vR6e 
外网面板地址: [https://1.12.43.211:28058/4ebc94d6](https://1.12.43.211:28058/4ebc94d6) 
内网面板地址: [https://10.1.12.11:28058/4ebc94d6](https://10.1.12.11:28058/4ebc94d6) 
username: bme6rczl 
password: d2ad722f

服务器mysql数据库连接信息：
1.12.43.211  3306 root /a3f5c8e1d7b90246

Dify访问路径：
http://1.12.43.211/apps
账号密码：  1124317604@qq.com | 7553977a

Dify里面叫 极小妹 和 易拍居的两个工作流是在使用的，其他的都没有利用起来可以忽略。

### 运行环境与依赖
- Python 3.12+
- FastAPI
- SQLModel（基于 SQLAlchemy）
- 其他依赖见项目 `requirements.txt`

### python项目容器化部署
这是实际开发中打包镜像 部署docker容器时会用的命令  [stone-ai:0.1.10] 镜像名和版本可自行修改 

项目根目录下运行该命令，构建镜像
docker build -t stone-ai:0.1.10 .
docker buildx build --platform linux/amd64 -t stone-ai:0.2.1 .

保存镜像至根目录，然后将其复制到服务器的/www/wwwroot/ricDocker下， 理论上任何位置都行，但是需要有一个 .env 配置文件
docker save -o stone-ai-0.1.10.tar stone-ai:0.1.10

在服务器对应目录下执行该命令 加载镜像  加载完可以运行 docker images 确认， 通常无需确认
docker load -i stone-ai-0.1.10.tar

运行镜像， 以 8000端口代理容器的8000 端口  指定配置文件 为当前目录下的 .env ，  指定数据卷为ai_upload_volume  指定容器的名称为 stone-ai-0110
docker run -p 8000:8000 --env-file .env -d -v ai_upload_volume:/app/uploads --name stone-ai-0110 stone-ai:0.1.10


## 文件架构
- src/ai 通用的对Ai库的封装以及常用函数封装，目前只对openAI库进行了封装
- src/common 通用文件夹，打算放一些枚举类或常量
- src/controller 控制层,存放接口
- src/dao 数据访问层,存放数据库操作
- src/db 数据库文件夹,存放数据库的DDL和DML
- src/env 环境变量、常量等存放处
- src/exception 自定义异常类存放处
- src/myHttp Http相关处理，包括结果封装类，以及http请求封装
- src/mySchedules 定时任务存放处
- src/pojo 实体类、视图类、业务类 存放处
- src/service 业务逻辑层，存放业务逻辑
- src/test 测试类存放处
- src/utils 工具类存放处
- static/ 静态资源存放处,部署到服务器上有时候请求不到swagger的UI资源，干脆把它download到本地了


### 核心代码详解
src/controller/business 这个包下面的控制类是业务控制类
目前包含两个文件， erpController  和ERP系统相关的接口
				ypjController  和易拍居相关的接口

src/controller/dify 这个包下面是Dify封装接口， 主要封装了 stoneAi和 易拍居 两个对话流接口


src/controller/ai 和Ai应用相关的一些接口 比如说提示词、api...

src/controller/common 公共接口，现在有文件管理相关的接口

