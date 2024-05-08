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
from tkinter import Tk, Text, END, Frame
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import matplotlib.colors as mcolors

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, ".."))

from packets import *
from parser import *

def get_username():
  return os.environ.get('USER', os.environ.get('USERNAME'))

replay_file = r"C:\Users\<username>\Documents\Command and Conquer Generals Zero Hour Data\Replays\00000000.rep"
replay_file = replay_file.replace("<username>", get_username())
is_live_replay = True

selected_unit = 0
build_entries = []
game_time = 0

# -- user interface --
window = Tk()
window.title('CNC-Generals-Replay-Parser - Build Sequence Chart')
window.geometry("800x600+10+10")

textField = Text(window, width=132, height=9, font=("Helvetica", 8))
textField.place(x=2, y=20)

textFieldGameTime = Text(window, width=8, height=1, font=("Helvetica", 8)) 
textFieldGameTime.place(x=2, y=2)

# -- plot --
plotFrame = Frame(window)
plotFrame.pack(fill=None, expand=False)
plotFrame.place(x=0, y=154)
    
fig = Figure(figsize = (10, 4), dpi=100)
fig.subplots_adjust(
    top=0.925,
    bottom=0.16,
    left=0.06,
    right=0.64, # specifies space for legend
    hspace=0.2, wspace=0.2
)
gnt = fig.add_subplot(111) 
canvas = FigureCanvasTkAgg(fig, master=plotFrame) 
  
toolbar = NavigationToolbar2Tk(canvas, plotFrame)

def plot():
    global gnt
    global canvas
    
    # --
    gnt.clear()
    gnt.set_xlabel('Time (s)')
    gnt.set_ylabel('Unit No')
    gnt.grid(True)
    
    colours = {}
    for idx,entry in enumerate(build_entries):
        # -- set colour
        if not entry["type"] in colours:
            colours[entry["type"]] = list(mcolors.TABLEAU_COLORS.keys())[len(colours)]
        # -- draw bar
        gnt.broken_barh(
            [(entry["start_time"], entry["finish_time"] - entry["start_time"])],
            (idx, 1),
            facecolors =(colours[entry["type"]]),
            label = entry["type"]
        )

    # -- remove duplicate labels
    handles, labels = gnt.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    gnt.legend(
        by_label.values(), by_label.keys(),
        loc='lower left', bbox_to_anchor=(1, 0),
        prop={'size': 6}
    )

    canvas.draw()
    canvas.get_tk_widget().pack()

# -- parser --
def getValueByFieldNameFromEntries(entries, sFieldName):
    for (packetTime, file_pos, fieldName, fieldType, fieldLength, value, formatName, extraInfo) in entries:
        if fieldName == sFieldName:
            return value

def cb_packet(entries):
    global textField
    global textFieldGameTime
    global selected_unit
    global build_entries
    global game_time

    packetType = getValueByFieldNameFromEntries(entries, "packetType")
    if packetType != "1049" and packetType != "1047" and packetType != "1068"  and packetType != "1001":
        return

    game_time = int(float(getValueByFieldNameFromEntries(entries,"packetTime")) / 30)
    clock()
    
    text = ""
    
    if packetType == "1049": # create_building
        building_type_id = getValueByFieldNameFromEntries(entries,"buildingType")
        building_type = buildingTypeMap[building_type_id]
        if building_type == "unknown":
            building_type += f" (id {building_type_id})"

        start_time = int(game_time)
        build_entry = {
            "type": building_type,
            "order_time": int(game_time),
            "from_building_id": selected_unit,
            "start_time": start_time,
            "finish_time": start_time + buildingBuildTimeMap[building_type_id],
        }
        build_entries += [build_entry]
        text += f"{build_entry}\n"
    
    if packetType == "1001": # select_unit
        unit_id = getValueByFieldNameFromEntries(entries,"unitId")
        selected_unit = unit_id

    if packetType == "1047": # create_unit
        unit_type_id = getValueByFieldNameFromEntries(entries,"unitType")
        unit_type = unitTypeMap[unit_type_id]
        if unit_type == "unknown":
            unit_type += f" (id {unit_type_id})"

        # -- check how much time is consumed with other units first
        start_time = int(game_time)
        for build_entry in build_entries:
            if build_entry["from_building_id"] == selected_unit: # same building
                start_time = max(start_time, build_entry["finish_time"])

        build_entry = {
            "type": unit_type,
            "order_time": int(game_time),
            "from_building_id": selected_unit,
            "start_time": start_time,
            "finish_time": start_time + unitBuildTimeMap[unit_type_id],
        }
        build_entries += [build_entry]
        text += f"{build_entry}\n"

    plot()
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

# ---

global last_time
last_time = 0

def clock():
    global game_time
    global last_time
    textFieldGameTime.delete('1.0', END)
    textFieldGameTime.insert(END, str(int(game_time)))
    
    game_time += (time.time() - last_time) # game speed is usually 30 ticks/second
    last_time = time.time()    
    
    timer = window.after(500, clock)
    
timer = window.after(500, clock)

# -- user interface --
t = threading.Thread(target=loop, args = ())
t.daemon = True
t.start()

window.mainloop()
