# 安卓app半自动化隧道流量采集
## 一、	抓包工具及环境
1. 模拟器：雷神模拟器（4.0前瞻版，Android 7.1内核），
2. 抓包工具：模拟器内部运行tcpdump 
3. 其他辅助工具：黑阈app，用于及时清理Android后台

## 二、	抓包规范
<暂无>

## 三、	前期配置
1. 下载雷神模拟器，配置shadowsocksR代理；
2. 在主机下载黑阈apk并安装到模拟器中，具体配置方法另附；
3. 按照给定的应用名在模拟器中通过google play下载对应的apk并安装；
4. 注册账号并登录，以进行后续的指定网络行为；
5. 在主机中运行如下命令，向模拟器中导入tcpdump并授予权限：
```
adb root
adb push tcpdump /data
adb shell chmod 777 /data/tcpdump
```
注：不同设备下命令可能会略有不同，部分设备需要添加如下的命令修饰：
```
adb shell push tcpdump /data/tcpdump
adb shell chmod 777 /data/tcpdump
```
或：
```
adb shell su -c push tcpdump /data/tcpdump
adb shell su -c chmod 777 /data/tcpdump
```

## 四、	抓包：
1. 构建app-list文件
使用命令：
```
adb shell pull /data/system/packages.xml /*雷神模拟器中默认的电脑共享文件夹*/ 
```
以获取Packages.xml，其中记录了已安装到当前设备中的所有app的相关信息。Packages.xml的结构如图下所示。其中package name字段和userid字段均唯一标识了设备内的某一指定应用，且package name字段通常携带与应用名相同或相近的信息，易于人为辨认。
 
App-list是csv文件，存储了应用名与package name之间的对应关系。首列标识应用名，第二列为应用所对应的package name, 第三列为其他备注或附加信息。在实际运行过程中，脚本仅读取并使用app-list文件中的第二列（即应用的package name字段），结合adb命令实现指定应用的循环自启动，因此抓包过程中抓包者仅需要关注【本次需要执行何种网络行为】即可，不需人为操作应用的频繁启动、关闭与后台清理操作。

2. 实际的抓包流程
脚本的抓包流程简述如下：
```
读取app-list中的package name字段；
指定的应用运行次数下：
For <app> in app-list:
   输入本次要执行的网络行为对应名称；
      Tcpdump启动抓包，监听通过ssr转发的所有数据包；
      应用自启动；
      挂起等待，抓包者进行实际的网络行为，完成后在控制台输入y确认本次行为已完成（没有反应就尝试多输一两次，至看到控制台返回force stop app running），结束采集；
      应用进程结束,清理后台；
      Tcpdump结束抓包，将形成的pcap文件存储到模拟器存储区中；
      Adb pull将pcap文件转存到主机；
```

附注：
1. 每次开始抓包前最好：
```
1.	Adb kill-server
2.	Adb start-server
3.	Adb remount
```
然后查看adb devices，是否有当前模拟器对应的机器，或者是否有其他多开机器，避免出现模拟机脱机状态导致脚本运行失败
  
2. 模拟器重启后需要确认黑阈的相关设置是否符合要求
