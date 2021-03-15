import asyncio
from bleak import discover, BleakClient
import numpy as np
import os, time
from datetime import datetime
import matplotlib.pyplot as plt
from aioconsole import ainput

address = "97:4C:30:C8:96:88"  ## nano

BRCST_ID = "00001143-0000-1000-8000-00805f9b34fb"
SETTING_ID = "00001142-0000-1000-8000-00805f9b34fb"
fname = './data/' + datetime.today().strftime('%m_%d') + '.txt'
ftime = './data/' + datetime.today().strftime('%m_%d') + '_time.txt'

score = 0
CRC_N = 10
DATA_LEN = 70 #6
BIN_SENSOR = []


T_COUNT = 0
T_LAST = time.time()
def logTime():
    global T_COUNT, T_LAST
    T_COUNT += 1    
    if T_COUNT == 1000:
        t = time.time() - T_LAST
        print('[TIME]1000 packets in %.2f, frequency = %.2f '%(t, 1000./t))
        T_COUNT = 0
        T_LAST = time.time()
        f = open(ftime, 'a+')
        f.write( '%.2f,'%t )
        f.close()

def checkCrc(a, n):
    c = 0
    for i in a[:-1]:
        c ^= i + n
    if c%256 != a[-1]:
        print('crc error, rcv/real crc: ', c%256, a[-1])
        return False
    return True 

def checkPacket(d):
    if len(d) != DATA_LEN*2 + 4:
        print('packet length error: seq_%d, len_%d'%(d[2] if len(d)>3 else 0, len(d)))
        return False
    else:
        return checkCrc(d, CRC_N)

# for now, just convert 255 to 0.
def packetDecode(packet):
    return [ 0 if i==255 else i for i in packet ]

async def scan_ble():
    devices = await discover()
    for d in devices:
        print("BLE device found: ", d, type(d))
        if d.name == "PressureMeasure":
            addr = d.address
    return addr 

fig, ax = plt.subplots()
values = [ 0 for i in range(10) ]
async def plot_data(): 
    global values
    while True:
        plt.clf()
        values = [score] + values[:-1]
        plt.plot(values, '-o')
        plt.ylim(0, 200)
        plt.pause(0.01)
        await asyncio.sleep(.5)

rawD, tmpD, loopD =[],[],0
def data_rcv(sender: str, data):
    global rawD, tmpD, loopD
    # print('[BLE] rcv: ', sender, list(data))
    rawD += list(data)
    
    while len(rawD) > DATA_LEN:
        if loopD == 0:
            try:
                s2 = rawD.index(0x34, 1)    
                if rawD[s2-1] == 0x12: # find start mNumber, session start
                    tmpD = [0x12, 0x34]
                    rawD = rawD[s2+1:] # dump the previous values
                    loopD = 1
                else:
                    rawD = rawD[s2+1:]
            except:
                print('cant find s2')
                rawD = []

        if loopD == 1:
            try:
                s2 = rawD.index(0x34, 1)
                if rawD[s2-1] == 0x12: # find end mNumber
                    tmpD += rawD[:s2-1] 
                    rawD = rawD[s2-1:] # dump the previous values
                    loopD = 0
                else:
                    tmpD += rawD[:s2+1]
                    rawD = rawD[s2+1:]
            except:  # not finding magic number.
                tmpD += rawD
                rawD = []

            if loopD == 0:
                logTime()
                if checkPacket(tmpD): ## must check if BLE packet is correct.
                    dd = packetDecode(tmpD[3:-1]) ## decode payload
                    dd = [ dd[1+2*i]*256+dd[2*i] for i in range(DATA_LEN)] # bytes to sensor-data
                    dd = [tmpD[2]] + [ v / (1024 - v) * 14000 if v < 500 else 0 for v in dd[1:1+DATA_LEN] ] # AD to OM
                    # print('save data: ', dd)
                    #print('save file in ', fname)
                    f = open(fname, 'a+')
                    f.write( str(dd)[1:-1] + '\n' )
                    f.close()
    

async def start_console_input(client):
    while True:
        line = await ainput("input to ble: ")
        await client.write_gatt_char(SETTING_ID, str.encode(line), False)
        await asyncio.sleep(1)
    return 
  
async def run(address):
    client = BleakClient(address)
    try:
        await client.connect()
        
        x = await client.is_connected()
        print("Connected: {0}".format(x))
        await client.start_notify(
              BRCST_ID, data_rcv,
        )
       
        while True:
            if not await client.connect():
                break
            await asyncio.sleep(0.5)
        
        return x, client
#         model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#         print("Model Number: {0}".format("".join(map(chr, model_number))))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
addr = loop.run_until_complete(scan_ble())

print('Scan over.... Start connection')
loop.run_until_complete(
    asyncio.gather(
        run(addr), 
        # plot_data(),
    )
)


# a / r = 1024 / (r+in)

# +in = (1024 * 10k) / a - 10k 