import websocket
import threading
import json
import time
from ctypes import Structure
import ctypes, struct
from struct import pack_into


class CliMarketdataRes(Structure):
    _pack = 1
    _fields_ = [
        ('exchange', ctypes.c_uint32),
        ('token', ctypes.c_uint32),
        ('moving', ctypes.c_uint32),
        ('open_price', ctypes.c_uint64),
        ('high', ctypes.c_uint64),
        ('low', ctypes.c_uint64),
        ('close', ctypes.c_uint64),
        ('volume', ctypes.c_uint64),
    ]
    size = 53

    def get_CliMarketdataRes_Instruct(self, packet_buffer):
        self.exchange = struct.unpack('>I', packet_buffer[1:5])[0]
        self.token = struct.unpack('>I', packet_buffer[5:9])[0]
        self.moving = struct.unpack('>I', packet_buffer[9:13])[0]
        self.open_price = struct.unpack('>Q', packet_buffer[13:21])[0]
        self.high = struct.unpack('>Q', packet_buffer[21:29])[0]
        self.low = struct.unpack('>Q', packet_buffer[29:37])[0]
        self.close = struct.unpack('>Q', packet_buffer[37:45])[0]
        self.volume = struct.unpack('>Q', packet_buffer[45:53])[0]
        
def heartbeat_thread(clientSocket):
    while clientSocket:
        send_data = '{"a": "h", "v": [], "m": ""}'
        try:
            clientSocket.send(send_data)
        except Exception as e:
            print("HEARTBEAT [ERROR]: [BLITZ_HYDRA_STREAM] Connection closed.")
            break
        print("Sent Heart-Beat to Exchange")
        time.sleep(15)

        
def on_message(ws, message):
    marketdataPkt = CliMarketdataRes()
    marketdataPkt.get_CliMarketdataRes_Instruct(message)
    print "Exchange Code", marketdataPkt.exchange
    print "Token ", marketdataPkt.token
    print "Moving", marketdataPkt.moving
    print "Open", marketdataPkt.open_price
    print "High", marketdataPkt.high
    print "Low", marketdataPkt.low
    print "close", marketdataPkt.close
    print "volume", marketdataPkt.volume

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    hbThread = threading.Thread(target=heartbeat_thread, args=(ws,))
    hbThread.start()
    sub_packet = {
        "a": "subscribe",
        "v": [[11,1304], [11, 1303]],  # ETH-CGC, BTC-CGC
        "m": "24hrstats"
    }
    ws.send(json.dumps(sub_packet))
    
if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://alpha.tradesprite.com/hydrasocket/v2/websocket",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
