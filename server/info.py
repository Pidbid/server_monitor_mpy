# -*- encoding: utf-8 -*-
'''
@File    :   info.py
@Time    :   2021/02/07 18:20:08
@Author  :   Wicos 
@Version :   1.0
@Contact :   wicos@wicos.cn
@Blog    :   https://www.wicos.me
'''

# here put the import lib
import socket
import fcntl
import struct
import os
from datetime import datetime

class INFO:
    def __init__(self):
        pass

    def memory_stat(self):
        mem = {}
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if len(line) < 2:
                    continue
                name = line.split(':')[0]
                var = line.split(':')[1].split()[0]
                mem[name] = float(var)
            mem['MemUsed'] = mem['MemTotal'] - \
                mem['MemFree'] - mem['Buffers'] - mem['Cached']
            # 记录内存使用率 已使用 总内存和缓存大小
            res = {}
            res['percent'] = int(round(mem['MemUsed'] / mem['MemTotal'] * 100))
            res['used'] = round(mem['MemUsed'] / (1024 * 1024), 2)
            res['MemTotal'] = round(mem['MemTotal'] / (1024 * 1024), 2)
            #res['Buffers'] = round(mem['Buffers'] / (1024 * 1024), 2)
            return res
        
    def cpu_stat(self):
        loadavg = {}
        with open("/proc/loadavg") as f:
            con = f.read().split()
            loadavg['lavg_1'] = con[0]
            loadavg['lavg_5'] = con[1]
            loadavg['lavg_15'] = con[2]
            loadavg['nr'] = con[3]
            prosess_list = loadavg['nr'].split('/')
            loadavg['running_prosess'] = prosess_list[0]
            loadavg['total_prosess'] = prosess_list[1]

            loadavg['last_pid'] = con[4]

            return loadavg

    def disk_stat(self):
        hd = {}
        disk = os.statvfs('/')
        #hd['available'] = float(disk.f_bsize * disk.f_bavail)
        hd['capacity'] = float(disk.f_bsize * disk.f_blocks)
        hd['used'] = float((disk.f_blocks - disk.f_bfree) * disk.f_frsize)
        res = {}
        res['used'] = round(hd['used'] / (1024 * 1024 * 1024), 2)
        res['capacity'] = round(hd['capacity'] / (1024 * 1024 * 1024), 2)
        res['available'] = res['capacity'] - res['used']
        res['available'] = round(res['available'],2)
        res['percent'] = int(round(float(res['used']) / res['capacity'] * 100))
        return res

    def get_ip(self, ifname="eth0"):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15].encode("utf-8"))))[20:24])

    def net_stat(self,ifname="eth0"):
        net = {}
        with open("/proc/net/dev") as f:
            lines = f.readlines()
            if not ifname:
                for line in lines[2:]:
                    line = line.split(":")
                    eth_name = line[0].strip()
                    if eth_name != 'lo':
                        net_io = {}
                        net_io['receive'] = round(
                            float(line[1].split()[0]) / (1024.0 * 1024.0 * 1024.0), 2)
                        net_io['transmit'] = round(
                            float(line[1].split()[8]) / (1024.0 * 1024.0 * 1024.0), 2)
                        net[eth_name] = net_io
                return net
            else:
                for line in lines[2:]:
                    line = line.split(":")
                    eth_name = line[0].strip()
                    if eth_name == ifname:
                        net_io = {}
                        net_io['receive'] = round(
                            float(line[1].split()[0]) / (1024.0 * 1024.0 * 1024.0), 2)
                        net_io['transmit'] = round(
                            float(line[1].split()[8]) / (1024.0 * 1024.0 * 1024.0), 2)
                        net[eth_name] = net_io
                return net

    def server_stat(self):
        net = self.net_stat("eth0")
        ip = self.get_ip()
        disk = self.disk_stat()
        cpu = self.cpu_stat()
        memory = self.memory_stat()
        server_all = {
            "ip":ip,
            "cpu":cpu,
            "memory":memory,
            "disk":disk,
            "net":net,
            "time":str(datetime.now())
        }
        return server_all
    
    def fake_msg(self):
        return '{"cpu":"123"}'

''' 
if __name__ == '__main__':
    a = INFO()
    print(a.server_stat())
 '''