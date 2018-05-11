# -*- coding: utf-8 -*-
from optparse import OptionParser
import os
import subprocess
import sys
import time
import datetime
import re
import codecs

'''返回：status,result'''


def getstatusoutput(cmd):
    pipe = os.popen(cmd)
    text = pipe.read()
    sts = pipe.close()
    if sts is None:
        sts = 0
    if text[-1:] == '\n':
        text = text[:-1]
    return sts, text


'''返回：PSS,NativeHeap,DalvikHeap'''


def getProcessMem(pid, device_id):
    cmd = "adb -s %s shell dumpsys meminfo %s" % (device_id, pid)
    status, output = getstatusoutput(cmd)
    GC = 0.0

    m = re.search(r'TOTAL\s*(\d+)', output)
    m1 = re.search(r'Native Heap\s*(\d+)', output)
    m2 = re.search(r'Dalvik Heap\s*(\d+)', output)
    m3 = re.search(r'.GC\s*(\d+)', output)
    PSS = float(m.group(1))
    NativeHeap = float(m1.group(1))
    DalvikHeap = float(m2.group(1))
    # print PSS,NativeHeap,DalvikHeap,GC
    if m3 is not None:
        GC = float(m3.group(1))

    return PSS, NativeHeap, DalvikHeap, GC


'''
dumpsys cpuinfo方法
'''


def getProcessCpuDumpsys(pid, device_id):
    cmd = "adb -s %s shell dumpsys cpuinfo" % (device_id)
    status, output = getstatusoutput(cmd)

    r = '\s+(\d+)%%\s*%s' % (pid)
    m = re.search(r, output)
    # print "%s,%s" % (m,output)
    if m:
        return float(m.group(1))
    return float(0.0)


'''
/proc/pid/stat字段说明，参考：http://blog.chinaunix.net/uid-22145625-id-2974389.html
进程的总Cpu时间processCpuTime = utime + stime + cutime + cstime（按顺序14~17字段），该值包括其所有线程的cpu时间，参考: http://blog.csdn.net/q838197181/article/details/50622498
return processCpu
'''


def getProcessCpuStat(pid, device_id):
    cmd = "adb -s %s shell cat /proc/%s/stat" % (device_id, pid)
    status, output = getstatusoutput(cmd)

    toks = re.split("\\s+", output.strip())
    processCpu = float(toks[13]) + float(toks[14]) + \
                 float(toks[15]) + float(toks[16])
    return processCpu


'''
参考: http://blog.csdn.net/q838197181/article/details/50622498
结论1：总的cpu时间totalCpuTime = user + nice + system + idle + iowait + irq + softirq
proc/stat结果 
第一行的数值表示的是CPU总的使用情况，所以我们只要用第一行的数字计算就可以了
return totalCpu,idleCpu
'''


def getTotalCpuStat(device_id):
    cmd = "adb -s %s shell cat /proc/stat" % device_id
    status, output = getstatusoutput(cmd)

    m = re.search(
        r'cpu\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)', output)
    totalCpu = float(m.group(1)) + float(m.group(2)) + float(m.group(3)) + \
               float(m.group(4)) + float(m.group(6)) + \
               float(m.group(5)) + float(m.group(7))
    idleCpu = float(m.group(4))
    return totalCpu, idleCpu


'''
查找cpu内核数量
'''


def getCpuCores(device_id):
    cmd = "adb -s %s shell ls /sys/devices/system/cpu/" % device_id
    status, output = getstatusoutput(cmd)

    m = re.findall("cpu\\d+", output)
    return len(m)


'''
PID      PR     CPU%   S      #THR       VSS             RSS          PCY           UID           Name
PID:进程在系统中的ID
CPU% - 当前瞬时所以使用CPU占用率
#THR - 程序当前所用的线程数
UID - 运行当前进程的用户id
Name - 程序名称Android.process.media
VSS - Virtual Set Size 虚拟耗用内存（包含共享库占用的内存）
RSS - Resident Set Size 实际使用物理内存（包含共享库占用的内存）
PSS - Proportional Set Size 实际使用的物理内存（比例分配共享库占用的内存）
USS - Unique Set Size 进程独自占用的物理内存（不包含共享库占用的内存）
return cpu,thr,vss,rss
'''


def getTopInfo(device_id, package_name):
    cmd = "adb -s %s shell \"top -n 1|grep -E \'%s|%s\'\"" % (
        device_id, package_name, r'/system/bin/mediaserver')
    status, output = getstatusoutput(cmd)

    r = '(\d+)%%\s+\w+\s+(\d+)\s+(\d+)\w+\s+(\d+)\w+.+\s+%s[^\S]' % package_name
    r1 = '(\d+)%%\s*.*%s' % r'/system/bin/mediaserver'
    m = re.search(r, output)
    m1 = re.search(r1, output)
    if m1:
        mediaserver = m1.group(1)
    else:
        mediaserver = 0
    if m:
        return m.group(1), m.group(2), m.group(3), m.group(4), mediaserver
    else:
        return 0, 0, 0, 0, mediaserver


def getTopOutput(device_id):
    cmd = "adb -s %s shell \"top -n 1\"" % device_id
    status, output = getstatusoutput(cmd)

    return output


def getCpuInfo(pid, device_id, package_name):
    totalCpu = 0.0
    idleCpu = 0.0
    processCpu = 0.0

    cmd = "adb -s %s shell cat /proc/%s/stat /proc/stat" % (device_id, pid)
    status, output = getstatusoutput(cmd)

    m = re.search(
        r'cpu\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)', output)
    if m:
        totalCpu = float(m.group(1)) + float(m.group(2)) + float(m.group(3)) + float(
            m.group(4)) + float(m.group(6)) + float(m.group(5)) + float(m.group(7))
        idleCpu = float(m.group(4))
    m1 = re.split('\n', output.strip())[0]
    if m1:
        toks = re.split("\\s+", m1.strip())
        processCpu = float(toks[13]) + float(toks[14]) + \
                     float(toks[15]) + float(toks[16])
    # print output,m1
    return totalCpu, idleCpu, processCpu


'''
获取uid，先认为应用唯一uid
Uid:    10114   10114   10114   10114
'''


def getUid(device, pid):
    cmd = "adb -s %s shell cat /proc/%s/status" % (device, pid)
    status, outputs = getstatusoutput(cmd)
    m = re.search(r'Uid:\s+(\d+)', outputs)
    if m:
        uid = m.group(1)
    else:
        print("Couldn't find uid from pid: %s" % pid)
        sys.exit(-1)
    return uid


'''
获取pid
'''


def getPid(device, appname):
    cmd = "adb -s %s shell top -m 10 -n 1" % device
    status, outputs = getstatusoutput(cmd)
    r = "(\\d+).*\\s+%s[^:]" % appname
    m = re.search(r, outputs)
    # print outputs
    if m:
        return m.group(1)
    else:
        print("Couldn't find pid of %s from %s" % (appname, outputs))
        sys.exit(-1)


'''
参考：http://blog.csdn.net/yyh352091626/article/details/50599621
'''


def getSndTraffic(device, uid):
    cmd = "adb -s %s shell cat /proc/uid_stat/%s/tcp_snd" % (device, uid)
    status, outputs = getstatusoutput(cmd)
    m = re.search(r'(\d+)', outputs)

    if m:
        sndTraffic = float(m.group(1))
    else:
        sndTraffic = -1.0
    # print outputs,sndTraffic
    return sndTraffic


def getRcvTraffic(device, uid):
    cmd = "adb -s %s shell cat /proc/uid_stat/%s/tcp_rcv" % (device, uid)
    status, outputs = getstatusoutput(cmd)
    m = re.search(r'(\d+)', outputs)
    if m:
        rcvTraffic = float(m.group(1))
    else:
        rcvTraffic = -1.0
    # print outputs,rcvTraffic
    return rcvTraffic


'''
https://testerhome.com/topics/2643
android 2.2后可采集 /proc/net/xt_qtaguid/stats
'''


def getXT(device, uid):
    cmd = "adb -s %s shell \"cat /proc/net/xt_qtaguid/stats|grep %s\"" % (
        device, uid)
    status, output = getstatusoutput(cmd)
    lines = output.strip().split('\n')

    rx_bytes = 0.0
    tx_bytes = 0.0
    for x in lines:
        array = x.strip().split('\n')
        if len(array) < 8:
            print('cannot get xt_qtaguid')
            break
        rx_bytes += float(array[5])
        tx_bytes += float(array[7])
    return rx_bytes, tx_bytes


def collect_msg(interval, arg_log_path, package_name, device_id):
    # 根据应用的包名称 获取CPU以及内存占用
    send_network_str = 0.0
    rec_network_str = 0.0
    lastSend = 0.0
    lastReC = 0.0
    flow = 0.0
    d1 = datetime.datetime.now()
    d2 = d1
    firstRun = True

    # GPU cmd
    load_cmd = "adb -s %s shell cat /sys/class/kgsl/kgsl-3d0/gpubusy" % device_id

    app_pid = getPid(device_id, package_name)
    cpuCores = getCpuCores(device_id)

    # datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    filename = os.path.join(arg_log_path, "%s_%s%s.csv" %
                            (device_id, package_name, file_time))
    # f = codecs.open(filename, 'a', 'utf-8')
    with codecs.open(filename, 'a', 'gb2312') as f:
        f.write(
            u"时间,上行流量(KB/s),下行流量(KB/s),应用cpu占比(% top),线程数(top),虚拟内存vss(top)MB,实际内存rss(top)MB,GPU（%）,mediaserver cpu(%)\n")

    uid = getUid(device_id, app_pid)
    totalCpu2 = 0.0
    while True:
        # 获取GPU
        status, output = getstatusoutput(load_cmd)
        m = re.search(r'\s*(\d+)\s*(\d+)', output)
        if m:
            utilization_arg_1 = m.group(1)
            utilization_arg_2 = m.group(2)
        else:
            print("Couldn't get utilization data from: %s!" % output)
            utilization_arg_1 = 0
            utilization_arg_2 = 0

        if utilization_arg_2 != '0':
            load = str(round((float(utilization_arg_1) /
                              float(utilization_arg_2)) * 100, 2))
        else:
            load = 0.00

        # dumpsys获取流量使用情况
        # PSS,NativeHeap,DalvikHeap,GC = getProcessMem(app_pid,device_id)

        cpu, thr, vss, rss, mediaserver = getTopInfo(device_id, package_name)

        cmd = "adb -s %s shell cat /proc/%s/net/dev" % (device_id, app_pid)
        status, outputs = getstatusoutput(cmd)
        d1 = datetime.datetime.now()
        '''获取Receive and Transmit
            Inter-|   Receive                                                |  Transmit
             face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
        '''
        m = re.search(
            r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', outputs)
        if m:
            rec_network_str = float(m.group(1))
            send_network_str = float(m.group(2))
        else:
            print("Couldn't get rx and tx data from: %s!" % outputs)
            rec_network_str = 0.0
            send_network_str = 0.0

        if firstRun is False:
            d = d1 - d2
            seconds = d.seconds + d.microseconds / 1000000.0
            d2 = d1
            upflow = ((send_network_str - lastSend) / 1024) / seconds
            downflow = ((rec_network_str - lastReC) / 1024) / seconds
            upflow = round(upflow, 2)
            downflow = round(downflow, 2)
            lastReC = rec_network_str
            lastSend = send_network_str

            str_now_time = time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(time.time()))
            write_str = "%20s,%8s,%8s,%5s,%6s,%10s,%9s,%5s,%4s\n" % (str_now_time, upflow, downflow, cpu, thr, round(
                float(vss) / 1024, 2), round(float(rss) / 1024, 2), load, mediaserver)
            print(write_str)
            with codecs.open(filename, 'a', 'gb2312') as f:
                f.write(write_str)
        else:
            firstRun = False
            d2 = d1
            upflow = 0
            downflow = 0
            lastReC = rec_network_str
            lastSend = send_network_str
            flow = upflow + downflow

        time.sleep(float(interval))


'''
device_id = '0123456789ABCDEF':  未开机接usb状态
unauthorized: 

返回一个数组
'''


def find_device():
    cmd = "adb devices"
    status, output = getstatusoutput(cmd)
    m = re.findall("\n(\\S+)\\s*device[$\n]", output)
    if m:
        return m
    else:
        print(u"%s\n%s\n手机没插好，或offline状态，请检查" % (cmd, output))
        sys.exit(-1)


'''
检查机器是否正常运行
'''


def check_device(device):
    cmd = "adb devices"
    status, output = getstatusoutput(cmd)

    m = re.search("\\n(\\S+)\\s*device", output)
    if m is None:
        print(u"%s\n%s\n手机没插好，或offline状态，或deviceid：%s输入错误，请检查" %
              (cmd, output, device))
        sys.exit(-1)
    return device



if __name__ == "__main__":
    usage = u"用法: %prog -p 包名 -t 时间间隔 -d 结果存放目录 -s 设备ID"
    parse = OptionParser(usage=usage)
    parse.add_option("-p", type="string",
                     help="read the data on which package", default="com.t20000.lvji")
    parse.add_option("-i", type="int",
                     help="the interval to read the data", default=0)
    parse.add_option("-d", type="string",
                     help="the dicectory to store log file", default="")
    parse.add_option("-s", type="string",
                     help="directs command to the device with the given serial number", default=find_device()[0])
    (options, args) = parse.parse_args(sys.argv)
    collect_msg(options.i, options.d, options.p, options.s)
