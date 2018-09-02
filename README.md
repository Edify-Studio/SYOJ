# Hello SYOJ!
> 一个开源的 OI/ACM/icpc在线测评平台

## 依赖项
mysql
*注意：本文档不介绍mysql的配置工作*
python3
flask
flask-sqlalchemy
pymysql

## 如何安装它
*以下教程以ubuntu为例，其他linux请自行替换apt*

1.安装python3以及pip
```bash
sudo apt install python3 python3-pip -y
```
2.安装flask等python模块
```bash
sudo pip3 install flask flask-sqlalchemy pymysql
```
3.下载、配置并运行syoj
```bash
sudo apt install git -y && git clone https://github.com/Edify-Studio/SYOJ.git
cd SYOJ && sudo python3 install.py
```
然后根据提示安装即可，安装后会自动运行

4.直接运行syoj
```bash
sudo nohup python3 run.py &
```

## TODO LIST

1.一个更为简单易用的syoj安装&管理脚本

2.网站后台

3.更加友好的前端交互设计

4.网页响应式
