# -- coding: utf-8 --
__author__ = 'dk'
import  os
import  app_traffic_gather_tunnel
import time

pcap_destination_dir ="./pcap_oneplus6t/"


def clear_userdata(package):
    ###清除用户的历史数据,这一项对vpn应用很有效果
    cmd='adb shell rm -fr /data/user/0/{0}/'.format(package)
    print(cmd)
    os.system(cmd)


def lancher(package_name):
    print('lancher app to run……')
    os.system('adb shell settings put global airplane_mode_on 0')
    os.system("adb shell svc wifi enable")# 确保网络是打开的
    time.sleep(1.5)
    #clear_userdata(package_name)
    os.system('adb shell monkey -p %s -c android.intent.category.LAUNCHER 1' % package_name)  # 启动指定app
    #os.system("adb shell monkey sleep 5")
    ##启动后等待6秒
    #
    print('sleep now!!!!')
    time.sleep(3.5)


def close(package_name,userId):
    print('force stop app running.')
    os.system("adb shell am force-stop %s" % package_name)
    #os.system("adb shell pkill -U {0}".format(userId))
    time.sleep(1)
    app_traffic_gather_tunnel.close_back_process()


def operator(package_name):
    # os.system('adb shell monkey --pct-syskeys 0 --pct-majornav 0 --pct-nav 0 --pct-trackball 0 --pct-motion 0 --pct-anyevent 0 --pct-appswitch 20 --throttle 450 -p %s 300' % package_name)
    print('Please Now do whatever you should according to the xls list')
    while 1:
        s=input()
        if s=='y':
            break
        else:
            print('Tap y to make sure. ')

def capture_main(package,operation):
    timestamp = int(time.time())

    #打开tcpdump
    userId=app_traffic_gather_tunnel.get_userId(package)
    app_traffic_gather_tunnel.dumppcap('senra.rixcloud',timestamp,operation)  # 监听小飞机转发的所有代理包

    #启动APP
    lancher(package)

    #测试APP
    operator(package)

    #关闭APP
    close(package,userId)

    #关闭抓包进程
    app_traffic_gather_tunnel.close_tcpdump()

    ##获取版本号
    versionName = app_traffic_gather_tunnel.get_versionName(package)
    ##创建目录
    dst_dir = pcap_destination_dir+"{0}/{1}/".format(package,versionName)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    ##获取数据包,保存数据包
    app_traffic_gather_tunnel.pullpcap(timestamp,dst_dir,operation)
    print('using {0} seconds'.format(int(time.time())-timestamp))


def reboot():
    cmd="adb shell reboot"
    os.system(cmd)
    time.sleep(120)
    while not len(os.popen("adb devices").readlines()) > 2:
        time.sleep(5)
        print('wait for device reboot....')
    os.system("adb root")
    cmd="adb shell input tap 10 1910"   #唤醒屏幕
    os.system(cmd)

    cmd="adb shell input swipe 500 1400 500 500"    #解除锁屏
    os.system(cmd)
    print('reboot success now!!!')


if __name__ == '__main__':
    with open('app_list',encoding='utf8') as fp :
        package_list = fp.readlines()[1:]
    # package_list.reverse()
    for each in package_list:  # 对每个应用
        for _ in range(1):  # 重复执行n次,此处可以根据需要来修改每个应用循环执行的次数
            package =each.strip().split(",")[1]
            print("Current app: {0} ".format(package))
            print("Please input your operation name:")
            operation=input()
            try:
                capture_main(package,operation)
                print("===========================================================")
            except BaseException as exp:
                print('Error :',exp)
                #reboot()
        print('Please change the configuration in rixcloud……')
        while(1):
            s=input()
            if s=='y':
                break
            else:
                print('Input y if you have already change the configuration.')
