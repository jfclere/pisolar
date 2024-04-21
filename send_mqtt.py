#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import ssl

# This is the Publisher

client = mqtt.Client()
client.username_pw_set("admin", "admin")
#client.connect("localhost",1883,60)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect("192.168.1.124",8883,60)
client.publish("topic/test", "Hello world!");
client.disconnect();
