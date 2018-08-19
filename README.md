## 说明
路飞学城

## 运行环境

| Project | Status | Description |
|---------|--------|-------------|
| python          | 3.5.4 | 在这个版本以及以上都可以 |
| django                | 1.11 | 必须此版本 |
| django-cors-headers                | 2.4.0 | 版本以及以上 |
| djangorestframework                | 3.8.2 | 版本以及以上 |
| django_redis                | 4.9.0 | 版本以及以上 |

## 安装环境
`pip3 install django==1.11`

`pip3 install django-cors-headers`

`pip3 install djangorestframework`

`pip3 install django_redis`

## 特别说明
如果启动项目时,api_urls.py执行时报错,views找不到xx模块时

需要删除api目录下的views.py,这个文件没有用,由views目录管理了！

## API说明

| 路径 | 功能 |
|---------|--------|
| /api/v1/degreecourse/          | 查看所有学位课 |
| /api/v1/degreecourse/teachers/          | 查看所有学位课并打印学位课名称以及授课老师 |
| /api/v1/degreecourse/scholarship/          | 查看所有学位课并打印学位课名称以及学位课的奖学金 |
| /api/v1/courses/          | 展示所有课程 |
| /api/v1/courses/thematic/          | 展示所有的专题课 |
| /api/v1/courses/module/1/          | 查看id=1的学位课对应的所有模块名称 |
| /api/v1/courses/1/          | 获取id = 1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses |
| /api/v1/courses/faq/1/          | 获取id = 1的专题课，并打印该课程相关的所有常见问题 |
| /api/v1/courses/outline/1/          | 获取id = 1的专题课，并打印该课程相关的课程大纲 |
| /api/v1/courses/chapter/1/          | 获取id = 1的专题课，并打印该课程相关的所有章节 |
| /api/v1/shoppingcart/          | 添加到购物车,支持增删改查,分别对应POST,DELETE,POST,GET |
| /api/v1/payment/          | 添加结算中心,支持增加和查找,分别对应POST,GET |
| /api/v1/auth/          | 登录认证,成功返回token |


## 运行方式
请务必启动Redis,否则admin后台无法登陆！或者造成其他未知错误！
Redis配置在settings.py中

使用Pycharm直接运行即可，
或者使用命令
`python manage.py runserver`

## 表关系
本项目涉及13个表，表关系包含一对一，一对多，多对多！
表关系图如下：

![Image text](https://github.com/987334176/luffycity/blob/master/%E8%A1%A8%E5%85%B3%E7%B3%BB.png)

图中箭头开始的英文字母表示关联字段

按照箭头方向查询，表示正向查询，否则为反向查询

# 效果图
## 首页

![Image text](https://github.com/987334176/luffycity/blob/master/%E6%95%88%E6%9E%9C%E5%9B%BE/%E9%A6%96%E9%A1%B5.png)

## 课程

![Image text](https://github.com/987334176/luffycity/blob/master/%E6%95%88%E6%9E%9C%E5%9B%BE/%E8%AF%BE%E7%A8%8B.png)

## 课程详情
#### 只能通过页面添加到购物车,必须要登录

![Image text](https://github.com/987334176/luffycity/blob/master/%E6%95%88%E6%9E%9C%E5%9B%BE/%E8%AF%BE%E7%A8%8B%E8%AF%A6%E6%83%85.png)

## 购物车
#### 选择价格策略,前端和后端redis数据会更改。可以删除课程！此操作必须要登录

![Image text](https://github.com/987334176/luffycity/blob/master/%E6%95%88%E6%9E%9C%E5%9B%BE/%E8%B4%AD%E7%89%A9%E8%BD%A6.png)


Copyright (c) 2018-present, xiao You