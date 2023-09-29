from pythonosc import osc_message_builder
from pythonosc import udp_client

# Configura il client OSC
client = udp_client.SimpleUDPClient("127.0.0.1", 12345)  

# Invia un intero (0 o 1) a Processing
value_to_send = 1  # Cambia questo valore a 0 se vuoi inviare 0 invece di 1
msg = osc_message_builder.OscMessageBuilder(address="/data")
msg.add_int(value_to_send)
client.send(msg.build())