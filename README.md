```bash
pip install git+https://github.com/sword4869/sword_pywifi.git
```

```bash
$ sword_pywifi -h
usage: sword_pywifi [-h] [-i INTERFACE] [-d DICTIONARY_PATH] [-s SKIP] [-a] [-k | -c]

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        网卡接口
  -d DICTIONARY_PATH, --dictionary_path DICTIONARY_PATH
                        字典
  -s SKIP, --skip SKIP  跳过几个
  -a, --interactive     交互模式
  -k, --knwon           过滤已破解AP
  -c, --cache           过滤全部已缓存AP，包括知道密码的和不知道密码但尝试过的

$ sword_pywifi      # 默认全破解
$ sword_pywifi -a     # 选择破解
```
```bash
$ sword_pywifi_gui
```

## version

- 1.1 2024.01.04
    
    fix the bug of wifi connection. Should use ssid, rather than bssid.