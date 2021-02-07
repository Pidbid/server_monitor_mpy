import json
import network
import time
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
from font import fonts


class OLED():
    def __init__(self):
        self.i2c = I2C(scl=Pin(2), sda=Pin(0))
        self.oled = SSD1306_I2C(128, 64, self.i2c)
        self.oled.fill(0)

    def clear(self):
        self.oled.fill(0)
        self.oled.show()
        
    def clear_part(self,x,y,w,h):
        for i in range(h):
            self.oled.hline(x,y+i,w,0)
        self.oled.show()

    def text(self, data, x, y):
        self.oled.text(data, x, y)

    def display(self):
        self.oled.show()

    def loading(self, seconds):
        self.oled.text("Loading now ......", 0, 0)
        self.oled.rect(0, 28, 128, 20, 1)
        for i in range(1, int(128/int(seconds)+1)):
            self.oled.fill_rect(0, 28, i, 20, 1)
            time.sleep_ms(500)
            self.oled.show()
            
    def write_chinese(self,ch_str,x_axis,y_axis):
        offset_ = 0 
        y_axis = y_axis*8  # 中文高度一行占8个  
        x_axis = (x_axis*16)  # 中文宽度占16个 
        for k in ch_str: 
            code = 0x00  # 将中文转成16进制编码 
            data_code = k.encode("utf-8") 
            code |= data_code[0] << 16 
            code |= data_code[1] << 8
            code |= data_code[2]
            byte_data = fonts[code]
            for y in range(0, 16):
                a_ = bin(byte_data[y]).replace('0b', '')
                while len(a_) < 8:
                    a_ = '0'+a_
                b_ = bin(byte_data[y+16]).replace('0b', '')
                while len(b_) < 8:
                    b_ = '0'+b_
                for x in range(0, 8):
                    self.oled.pixel(x_axis+offset_+x, y+y_axis, int(a_[x]))   
                    self.oled.pixel(x_axis+offset_+x+8, y+y_axis, int(b_[x]))   
            offset_ += 16


class MQTT():
    def __init__(self) -> None:
        from mqtt import MQTTClient
        self.config = readconfig("config.json")
        self.client = MQTTClient(
            "umqtt_client", self.config["server"]["mqtt"], 1883, "USER", "PWD")
        self.topic_send = "ListenerSend"
        self.topic_recv = "pdibid/server"
        self.oled = OLED()
        self.oled.clear()
        self.display_title()
        
    def display_title(self):
        self.oled.text("IP:",0,0) #24,0
        self.oled.text("CPU:",0,8)
        self.oled.text("RAM:",0,18)
        self.oled.text("DISK:",0,28)
        self.oled.text("NET:",0,38)
        self.oled.text("TIME:",0,48)
        self.oled.display()

    def call_back(self, topic, msg):
        get_data = json.loads(msg)
        print(get_data)
        display_data = {
            "IP":get_data["ip"],
            "CPU":get_data["cpu"]["lavg_5"][2:] + "% " + get_data["cpu"]["nr"],
            "RAM":str(get_data["memory"]["percent"]) + "% " + str(get_data["memory"]["MemTotal"]),
            "DISK":str(get_data["disk"]["percent"]) + "% " + str(get_data["disk"]["available"]),
            "NET":"i-"+str(get_data["net"]["eth0"]["receive"])[:2] + " o-" + str(get_data["net"]["eth0"]["transmit"])[:2],
            "TIME":get_data["time"][11:-7]
            }
        self.oled.clear_part(24,0,104,8)#ip
        self.oled.text(display_data["IP"],24,0)
        self.oled.clear_part(32,8,128-32,8) #cpu
        self.oled.text(display_data["CPU"],32,8)
        self.oled.clear_part(32,18,128-32,10)# ram
        self.oled.text(display_data["RAM"],32,18)
        self.oled.clear_part(40,28,128-40,10) #disk
        self.oled.text(display_data["DISK"],40,28)
        self.oled.clear_part(32,38,128-32,10) #net 
        self.oled.text(display_data["NET"],32,38)
        self.oled.clear_part(40,48,128-40,10) #time
        self.oled.text(display_data["TIME"],40,48)
        self.oled.display()
        self.client.publish(
            self.topic_send, '{"code":"0","msg":"recviver and run"}', retain=True)

    def run(self):
        self.client.set_callback(self.call_back)
        self.client.connect()
        self.client.subscribe(self.topic_recv)
        self.client.publish(
            self.topic_send, '{"code":"0","msg":"Listener online"}', retain=True)
        while True:
            self.client.wait_msg()


def readconfig(filename):
    with open(filename, "r") as fp:
        conf = json.loads(fp.read())
        print(conf)
    return conf


def writeconfig(data, filename):
    with open(filename, "w") as fp:
        fp.write(json.dumps(data))


def wifi_connect(name, psd):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(name, psd)
    for i in range(6):
        time.sleep(1)
    if sta_if.ifconfig()[0] == "0.0.0.0":
        return False
    else:
        return True


def psd_connect():
    try:
        wifi_msg = readconfig("config.json")["wifi"]
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(wifi_msg['ssid'], wifi_msg['password'])
        for i in range(6):
            time.sleep(1)
        if sta_if.ifconfig()[0] == "0.0.0.0":
            return False
        else:
            print("connect wifi successfully")
            return True
    except:
        return False


def wifi_ap(name, psd):
    ap_if = network.WLAN(network.AP_IF)
    ap_if.config(essid=name, authmode=network.AUTH_WPA_WPA2_PSK, password=psd)
    for i in range(5):
        time.sleep(1)
        print('The AP build......')
    creat_ap = 'The AP was created successfully, and you are now ready to connect.'
    print(creat_ap)
    return True


def chinese(ch_str, x_axis, y_axis):
    from font import fonts
    offset_ = 0
    y_axis = y_axis*8  # 中文高度一行占8个
    x_axis = (x_axis*16)  # 中文宽度占16个
    for k in ch_str:
        code = 0x00  # 将中文转成16进制编码
        data_code = k.encode("utf-8")
        code |= data_code[0] << 16
        code |= data_code[1] << 8
        code |= data_code[2]
        byte_data = fonts[code]
        for y in range(0, 16):
            a_ = bin(byte_data[y]).replace('0b', '')
            while len(a_) < 8:
                a_ = '0'+a_
            b_ = bin(byte_data[y+16]).replace('0b', '')
            while len(b_) < 8:
                b_ = '0'+b_
            for x in range(0, 8):
                OLED.pixel(x_axis+offset_+x, y+y_axis, int(a_[x]))
                OLED.pixel(x_axis+offset_+x+8, y+y_axis, int(b_[x]))
        offset_ += 16


def tcp_server():
    import ure
    import usocket
    # Create STREAM TCP socket
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 80))
    s.listen(5)
    print("TCP is waiting......")
    is_connect = True
    while is_connect:
        conn, addr = s.accept()
        pre_data = str(conn.recv(1024), "utf-8")
        if len(pre_data) == 0:
            conn.close()
            continue
        cmps = ure.search(
            "GET /\?(.*?) HTTP", str(pre_data))
        print(cmps.group(1))
        ssid = str(cmps.group(1)).split(",")[0]
        psd = str(cmps.group(1)).split(",")[1]
        server = str(cmps.group(1)).split(",")[2]
        print(ssid, psd, server)
        isconnect = wifi_connect(ssid, psd)
        if isconnect:
            old_config = readconfig("config.json")
            old_config["wifi"] = {"ssid": ssid, "password": psd}
            old_config["server"] = {"mqtt": server}
            writeconfig(old_config, "config.json")
            is_connect = False
            print("connect successful")
            conn.send("HTTP/1.1 200 OK\r\n")
            conn.send("Server: Esp8266\r\n")
            conn.send("Content-Type: application/json;charset=UTF-8\r\n")
            conn.send("Connection: close\r\n")
            conn.send("\r\n")
            conn.send(json.dumps(dict(connect="yes")))
            conn.close()
        else:
            conn.send("HTTP/1.1 200 OK\r\n")
            conn.send("Server: Esp8266\r\n")
            conn.send("Content-Type: application/json;charset=UTF-8\r\n")
            conn.send("Connection: close\r\n")
            conn.send("\r\n")
            conn.send(json.dumps(dict(connect="no")))
            continue


def main():
    if not psd_connect():
        wifi_ap("Listen_server", "147258369")
        tcp_server()
    mqtt = MQTT()
    mqtt.run()


if __name__ == "__main__":
    main()
