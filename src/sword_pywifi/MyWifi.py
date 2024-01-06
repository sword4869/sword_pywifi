import pywifi
from pywifi import const
import time

class MyWifi(object):
    def __init__(self, interface_index=0):
        wifi = pywifi.PyWiFi()

        ### 获取无线网卡
        print('网卡设备:')
        for i, item in enumerate(wifi.interfaces()):
            print(f'\t{i}-[{item.name()}]')
            
        if len(wifi.interfaces()) == 1:
            print(f'只有一个网卡，使用默认网卡')
            self.iface = wifi.interfaces()[0]
        else:
            print(f'有多个网卡，使用第{interface_index}个网卡')
            self.iface = wifi.interfaces()[interface_index]

        ### 网卡状态
        self.StatusCode = {
            const.IFACE_DISCONNECTED: 'DISCONNECTED',   # 0
            const.IFACE_SCANNING: 'SCANNING',           # 1
            const.IFACE_INACTIVE: 'INACTIVE',           # 2
            const.IFACE_CONNECTING: 'CONNECTING',       # 3
            const.IFACE_CONNECTED: 'CONNECTED',         # 4
        }

        # 断开所有链接
        self.ensure_disconnect()

        ### 创建WiFi连接文件: ssid 和 pwd 之后赋值
        self.profile = pywifi.Profile()
        # 网卡的开放状态
        self.profile.auth = const.AUTH_ALG_OPEN
        # wifi加密算法: WPA2
        self.profile.akm.append(const.AKM_TYPE_WPA2PSK)
        # 加密单元
        self.profile.cipher = const.CIPHER_TYPE_CCMP

    def wifiConnect(self, ssid, pwd, count_down=20):
        '''
        连接wifi: 尝试用 pwd 连接 名为 ssid 的 AP, 尝试 count_down 秒
        '''
        # 断开所有连接
        self.ensure_disconnect()

        # 删除所有连接过的wifi文件，因为 ssid 和 pwd 变化了
        self.iface.remove_all_network_profiles()
        # 设定新的连接文件
        self.profile.ssid = ssid
        self.profile.key = pwd
        tmp_profile = self.iface.add_network_profile(self.profile)

        # 连接
        self.iface.connect(tmp_profile)

        # 密码错误的状态是IFACE_DISCONNECTED状态，但因为一开始是处于IFACE_DISCONNECTED状态，所以不能直接判断密码错误。
        # 我们要的是“IFACE_DISCONNECTED->IFACE_CONNECTING->IFACE_DISCONNECTED”这么一个验证过程。
        CONNECT_IN = False
        CONNECT_OUT = False
        while True:
            result = self.iface.status()
            print(f'\r\t{self.StatusCode[result]}...', end='')
            if CONNECT_IN == False and result == const.IFACE_CONNECTING:
                CONNECT_IN = True

            if CONNECT_IN == True and result == const.IFACE_DISCONNECTED:
                CONNECT_OUT = True

            # 密码正确，连接成功
            if result == const.IFACE_CONNECTED:
                return True

            # wifi连接时间
            time.sleep(1)
            count_down -= 1
            if count_down == 0:
                break
            if CONNECT_OUT:
                break
        
        self.ensure_disconnect()
        return False

    def ensure_disconnect(self):
        self.iface.disconnect()
        time.sleep(1)
        assert self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE], f'断开失败, 网卡状态错误: {self.iface.status()}'

    # 扫描wifi
    def wifiScan(self, wifiList_path=None, scan_time=10, threshold=-80):
        '''
        const.IFACE_SCANNING 就获取不了，所以不能像连接wifi那样判断状态
        需要sleep，再检测

        @return: [signal, bssid, chinese_ssid, ssid]
        '''
        print('扫描WIFI...')
        self.iface.scan()
        time.sleep(scan_time)
        wifi_infos = self.iface.scan_results()    

        nums = len(wifi_infos)
        print("数量: %s"%(nums))
        
        chinese_wifi_infos = []
        print (f"ID | signal | {'BSSID':^18} | SSID")
        for index, wifi_info in enumerate(wifi_infos):
            # signal  # 信号强度(数值越大，信号越强)
            # ssid    # 名字，不支持中文，需要 ssid.encode('raw_unicode_escape','strict').decode()
            # bssid   # mac地址
            chinese_ssid = wifi_info.ssid.encode('raw_unicode_escape','strict').decode()
            if chinese_ssid == '':
                continue
                
            print(f"{index:2} | {wifi_info.signal:^6} | {wifi_info.bssid} | {chinese_ssid}")
            if wifi_info.signal >= threshold:
                chinese_wifi_infos.append((wifi_info.signal, wifi_info.bssid, chinese_ssid, wifi_info.ssid))
        
        # 去重
        chinese_wifi_infos = list(set(chinese_wifi_infos))
        chinese_wifi_infos = [list(chinese_wifi_info) for chinese_wifi_info in chinese_wifi_infos]
        
        # 排序：按照信号强度
        chinese_wifi_infos = sorted(chinese_wifi_infos, key=lambda s: s[0], reverse=True)

        # 写入txt文本文件
        wifi_names = []
        for item in chinese_wifi_infos:
            wifi_names.append(item[2] + '\n')

        if wifiList_path is not None:
            with open(wifiList_path, "w", encoding='utf-8') as wifiList:
                # print(wifi_names)
                wifiList.writelines(wifi_names)

        return chinese_wifi_infos