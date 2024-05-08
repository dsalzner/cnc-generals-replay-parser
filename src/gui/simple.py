"""
Command and Conquer Replay File Parser
Copyright (C) 2023 D.Salzner <mail@dennissalzner.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import threading
from tkinter import Tk, Text, END

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, ".."))

from packets import *
from parser import *

def get_username():
  return os.environ.get('USER', os.environ.get('USERNAME'))

replay_file = r"C:\Users\<username>\Documents\Command and Conquer Generals Zero Hour Data\Replays\00000000.rep"
replay_file = replay_file.replace("<username>", get_username())
is_live_replay = True

# -- user interface --
window = Tk()
window.title('CNC-Generals-Replay-Parser')
window.geometry("538x640+10+10")

textField = Text(window, width=66, height=38) 
textField.place(x=2, y=2)

# -- parser --
def getValueByFieldNameFromEntries(entries, sFieldName):
    for (packetTime, file_pos, fieldName, fieldType, fieldLength, value, formatName, extraInfo) in entries:
        if fieldName == sFieldName:
            return value

def cb_packet(entries):
    global textField

    packetType = getValueByFieldNameFromEntries(entries, "packetType")
    if packetType != "1049" and packetType != "1047" and packetType != "1068"  and packetType != "1001":
        return

    game_time = int(float(getValueByFieldNameFromEntries(entries,"packetTime")) / 30)
    text = f"{game_time: >5}; "
    
    if packetType == "1049": # create_building
        building_type_id = getValueByFieldNameFromEntries(entries,"buildingType")
        building_type = buildingTypeMap[building_type_id]
        if building_type == "unknown":
            building_type += f" (id {building_type_id})"

        x = float(getValueByFieldNameFromEntries(entries, "x"))
        y = float(getValueByFieldNameFromEntries(entries, "y"))
        z = float(getValueByFieldNameFromEntries(entries, "z"))
        
        text += f'create_building \"{building_type}\"; x={x:.2f}; y={y:.2f}; z={z:.2f}\n'
        
    if packetType == "1047": # create_unit
        unit_type_id = getValueByFieldNameFromEntries(entries,"unitType")
        unit_type = unitTypeMap[unit_type_id]
        if unit_type == "unknown":
            unit_type += f" (id {unit_type_id})"
            
        queue_no = int(getValueByFieldNameFromEntries(entries, "unitNoFromSameBuilding"))
        
        text += f'create_unit \"{unit_type}\"; queue {queue_no}\n'

    if packetType == "1068": # move_order
        x = float(getValueByFieldNameFromEntries(entries, "x"))
        y = float(getValueByFieldNameFromEntries(entries, "y"))
        z = float(getValueByFieldNameFromEntries(entries, "z"))
        
        text += f'move_order; x={x:.2f}; y={y:.2f}; z={z:.2f}\n'
    
    if packetType == "1001": # select_unit
        unit_id = getValueByFieldNameFromEntries(entries,"unitId")
        
        text += f'select_unit; unit_id: {unit_id}\n'
    
    textField.insert(END, text)
    textField.see("end")
    
def loop():
    with open(replay_file, "rb") as f:
        print(f"=== {os.path.basename(replay_file)} ===")
        (lastPacketType, lastPacketPos) = parse(f, 0, is_live_replay, 0, cb_packet)
        print("---")
        
        while(True):
            print(f"=== {os.path.basename(replay_file)} ===")
            if not lastPacketType == 0:
                f.seek(lastPacketPos)

            (packetType, packetPos) = parse(f, 0, is_live_replay, lastPacketType, cb_packet)
            if packetType != 0:
                lastPacketType = packetType
                lastPacketPos = packetPos

            print(f"--- {lastPacketType} {packetPos}", flush=True)

            time.sleep(0.5)
    print("theead closed")

# -- user interface --
t = threading.Thread(target=loop, args = ())
t.daemon = True
t.start()

window.mainloop()
