import os
import shutil

if __name__ == '__main__':
    config = open("config.py.exmple", 'r').read()
    print("欢迎使用SYOJ！")
    domain=input("请输入mysql服务器地址（不带端口）：")
    port=input("请输入mysql服务器端口：")
    user=input("请输入用户名：")
    passwd=input("请输入密码：")
    dbname=input("请输入数据库名称（请务必确保数据库存在）：")
    open('config.py', 'w').write(config.replace("{{ database }}",'mysql+pymysql://' + user + ':' + passwd + '@' + domain +':' + port +'/' + dbname))
    print("正在初始化数据库...")
    from syzoj import db
    db.drop_all()
    db.create_all()
    print("初始化完成，正在启动syoj...")
    os.system('nohup python3 run.py &')
    print("syoj已在23333端口运行，感谢使用syoj！")
