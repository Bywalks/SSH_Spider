# SSH_Spider V1.0 #

**SSH_Spider** 是一个通过公私钥SSH批量登录IP，在每台登录主机执行命令，把执行的命令提取放到本地的小工具

### Install ###

```
python -m pip install -r requirements.txt
```

### 开始使用 ###

```
id_rsa放入主机私钥
server_list.txt放入konwn_hosts文件处理后的IP
python SSH_Spider.py
```

### 如何实现微信通知？

下载文件后，在代码中添加上你自己的 Server酱 key 就行了， Server酱 key 的申请地址为：[http://sc.ftqq.com/](http://sc.ftqq.com/)

### 如何实现公告监测？

首先在 vps 上下载安装该工具，之后设置定时任务即可。比如我想在每天的上午 9 点获取一下各大 SRC 有没有新的公告：

1、输入`crontab -e`

2、在打开的界面中输入`00 9 * * * python3 /root/OnTimeHacker/OnTimeHacker.py`即可。

### 扫描结果 ###

![SSH_Spider](./image/SSH_Spider.jpg)

### 微信消息 ###

![Notice](./image/Notice.jpg)

### 参考 ###
本想自己写一个这样的工具，查询后发现有小伙伴已经写了，拿小伙伴的代码改一改自己中意的SRC和些许功能，原版@teamssix
