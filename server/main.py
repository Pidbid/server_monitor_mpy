import paho.mqtt.client as mqtt
import schedule
from datetime import datetime
from info import INFO
import json

pub_topic = "pidbid/server"
pub_delay = 20

class MONITOR:
    def __init__(self):
        super(MONITOR,self).__init__()
        self.broker = "broker.emqx.io"
        self.port = 1883
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_message = self.__on_message
        

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def __on_disconnect(self,client, userdata, rc):
        self.disconnected = True, rc

    def __on_message(self,client, userdata, msg):
        print(msg.payload.decode())
    
    
    def subscrib(self,topic):
        self.client.subscribe(topic)
        self.client.loop_forever()

    def publish(self,topic,msg):
        self.client.publish(topic,msg)
        print("publish {} to {} at {}".format(msg[:30],topic,str(datetime.now())))
    
    def connect(self):
        self.client.connect(self.broker, self.port)

def publish_new():
    mqtt.publish(pub_topic,json.dumps(server_stat.server_stat()))

if __name__ == '__main__':
    mqtt = MONITOR()
    mqtt.connect()
    server_stat = INFO()
    schedule.every(pub_delay).seconds.do(publish_new)
    while True:
        schedule.run_pending()
    