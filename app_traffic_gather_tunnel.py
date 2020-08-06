# -- coding: utf-8 --
__author__ = 'dk'
import  os
import time
import multiprocessing


def close_back_process():
    ###清理后台运行
    cmd = "adb shell input keyevent 187"    #打开最近APP
    os.system(cmd)
    time.sleep(2)
    # cmd = "adb shell input swip 517,182 554,2000"    #  滑动到任务抽屉顶端
    # os.system(cmd)
    cmd = "adb shell input tap 950 150"    # 点击全部清除
    os.system(cmd)


def get_userId(package_name):
    ##首先获取package_name对应的userid
    os.system("adb root")
    cmd = "adb shell dumpsys package {0} | findstr userId".format(package_name)
    print(cmd)
    userId = os.popen(cmd).readlines()
    if len(userId) > 0:
        userId = int(userId[0].strip().split(" ")[0].split("=")[-1])
        return userId
    return  0 #找不到应用


def open_tcpdump(userId,timestamp,operation):
    ###打开tcpdump,同时监控APP和系统的流量,注意tcpdump是最新版本的
    if userId!=0:
        cmd = "adb shell /data/tcpdump -i nflog:{0} -w /sdcard/app_traffic/{1}_clear.pcap".format(userId,timestamp)
    else:
        cmd = "adb shell /data/tcpdump -i eth0 -s 0 -w /sdcard/app_traffic/ad_{2}_{1}_.pcap".format(userId,timestamp,operation)
    print(cmd)
    os.system(cmd)


def close_tcpdump():
    ###关闭tcpdump
    cmd = "adb shell pkill tcpdump"
    time.sleep(1)
    os.system(cmd)
    print(cmd)
    # clear_iptables_rule()


def add_iptables_rule(userId):
    ###添加NFLOG的iptables规则
    clear_iptables_rule()
    cmd = "adb shell iptables -A OUTPUT -m owner --uid-owner {0} -j CONNMARK --set-mark {0}".format(userId)
    print(cmd)
    os.system(cmd)
    cmd = "adb shell iptables -A INPUT -m connmark --mark {0} -j NFLOG --nflog-group {0}".format(userId)
    print(cmd)
    os.system(cmd)
    cmd="adb shell iptables -A OUTPUT -m connmark --mark {0} -j NFLOG --nflog-group {0}".format(userId)
    print(cmd)
    os.system(cmd)
    time.sleep(2)


def clear_iptables_rule():
    #清空全部的iptables历史规则
    print('clear iptables rules')
    os.system("adb shell iptables -F")


def dumppcap(package_name,timestamp,operation):
    process2 = multiprocessing.Process(target=open_tcpdump,args=(0,timestamp,operation))
    process2.start()
    return 0


def pullpcap(timestamp,dst_dir,operation):
    ##关闭所有的tcpdump
    close_tcpdump()
    ##获取数据
    # os.system("adb pull /sdcard/app_traffic/{0}_clear.pcap {1}/{2}_clear.pcap".format(timestamp,dst_dir,timestamp))
    os.system("adb pull /sdcard/app_traffic/ad_{3}_{0}_.pcap {1}".format(timestamp,dst_dir,timestamp,operation))
    ##删除数据
    # os.system("adb shell rm /sdcard/app_traffic/{0}_clear.pcap".format(timestamp))
    os.system("adb shell rm /sdcard/app_traffic/ad_{3}_{0}_.pcap".format(timestamp,dst_dir,timestamp,operation))


def get_versionName(package):
    cmd ="adb shell dumpsys package {0}| findstr versionName".format(package)
    output=os.popen(cmd).readlines()
    if len(output) == 0:
        raise BaseException('{0} does not exist'.format(package))
    return  output[0].strip().split("=")[-1]
if __name__ == '__main__':
    print(get_versionName("com.findtheway"))