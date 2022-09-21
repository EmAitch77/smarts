import json
from time import time

filename= 'data.json'

# Set

def set_open(open_time):
    datar= open(filename, 'r')
    dataj= json.load(datar)
    dataj['time']['open'] = int(open_time)
    datar.close()
    f = open(filename, 'w')
    f.write(json.dumps(dataj, indent=4))
    f.close()
    return True

def set_close(close_time):
    datar= open(filename, 'r')
    dataj= json.load(datar)
    dataj['time']['close'] = int(close_time)
    datar.close()
    f = open(filename, 'w')
    f.write(json.dumps(dataj, indent=4))
    f.close()
    return True

def add_room(room_id):
    datar= open(filename, 'r')
    dataj= json.load(datar)
    dataj['rooms']['channels'].append(int(room_id))
    datar.close()
    f = open(filename, 'w')
    f.write(json.dumps(dataj, indent=4))
    f.close()
    return True

def set_updates(roomid):
    datar= open(filename, 'r')
    dataj= json.load(datar)
    dataj['rooms']['updates'] = int(roomid)
    datar.close()
    f = open(filename, 'w')
    f.write(json.dumps(dataj, indent=4))
    f.close()
    return True

# Get

def get_time(type):
    datar= open(filename, 'r')
    dataj= json.load(datar)
    datar.close()
    return dataj['time'][type]

def load_channels():
    datar= open(filename, 'r')
    dataj= json.load(datar)
    datar.close()
    return dataj['rooms']['channels']

def get_updates():
    datar= open(filename, 'r')
    dataj= json.load(datar)
    datar.close()
    return dataj['rooms']['updates']

def reset(all):
    if all:
        datar= open(filename, 'r')
        dataj= json.load(datar)
        dataj['owner'] = None
        dataj['time']['open'] = None
        dataj['time']['close'] = None
        dataj['rooms']['updates'] = None
        dataj['rooms']['channels'].clear()
        dataj['set'] = False
        datar.close()
        f = open(filename, 'w')
        f.write(json.dumps(dataj, indent=4))
        f.close()
        return True

