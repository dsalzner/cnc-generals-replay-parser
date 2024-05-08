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

from packets import *
from parser import *
import time
import sys
import os

def get_username():
  return os.environ.get('USER', os.environ.get('USERNAME'))

replay_file = r"C:\Users\<username>\Documents\Command and Conquer Generals Zero Hour Data\Replays\00000000.rep"
replay_file = replay_file.replace("<username>", get_username())
is_live_replay = True

def getValueByFieldNameFromEntries(entries, sFieldName):
    for (packetTime, file_pos, fieldName, fieldType, fieldLength, value, formatName, extraInfo) in entries:
        if fieldName == sFieldName:
            return value

def cb_packet(entries):
    isCreateUnit = False

    if getValueByFieldNameFromEntries(entries, "packetType") == "1047": # create_unit
        print("!!!! CREATE UNIT\n\n\n")
    else:
        return

    if getValueByFieldNameFromEntries(entries,"unitType") == "6": # China Tank Red Guard
        print("CHINA TANK")
        print("unitNoFromSameBuilding " + str(getValueByFieldNameFromEntries(entries, "unitNoFromSameBuilding")))


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

