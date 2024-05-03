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

import itertools
import struct
import os
import packets
import importlib
from packets import *
from colorama import Fore, Style

def parseFromFormat(f, formatData):
  results = []
  for t in formatData:
    (keyStr, typeStr, byteCount) = t
    value = ""
    # - parse
    if typeStr == "HEX":
      for no in range(0, byteCount):
        value += str(f.read(1).hex())    
    elif typeStr == "c": # -- text is special case that can be read until null termination
      null_char_count = 0
      for no in range(0, 255):
        char_code = struct.unpack(typeStr, f.read(1))[0]
        if char_code == b'\x00':
          null_char_count += 1
        else:
          null_char_count = 0
        if null_char_count > 1:
          f.seek(f.tell() + 1) # skip the one
          break
        value += char_code.decode('UTF-8', errors="ignore")
    else:
      value = str(struct.unpack(typeStr, f.read(byteCount))[0])

      if keyStr == "unitCount": # unit count can vary in length
        extraInfo = "\nis_1; B; 1; " + str(struct.unpack('B', f.read(1))[0])
        extraInfo += "\n" + Fore.YELLOW + "[SELECTED] "

        for i in range(0, int(value)):
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","
        extraInfo += Style.RESET_ALL

        value += extraInfo
        f.seek(f.tell() - 5)

      if keyStr == "type1058_length": # can vary in length
        extraInfo = "\nis_1; B; 1; " + str(struct.unpack('B', f.read(1))[0])
        extraInfo += "\n" + Fore.YELLOW + "[SELECTED] "

        for i in range(0, int(int(value) / 2)):
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","
        extraInfo += Style.RESET_ALL

        if int(value) == 4: ## todo hacky?
            f.seek(f.tell() - 4)
        value += extraInfo

      if keyStr == "type1002_length": # can vary in length
        extraInfo = "\nis_1; B; 1; " + str(struct.unpack('B', f.read(1))[0])
        extraInfo += "\n" + Fore.YELLOW + "[SELECTED] "

        if int(value) == 1:
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","

        if int(value) == 4:
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","
            extraInfo += str(struct.unpack('I', f.read(4))[0]) + ","

        extraInfo += Style.RESET_ALL
        value += extraInfo

    results += [(int(f.tell()), keyStr, typeStr, byteCount, value)]
  return results

type1092_lastValue = defaultdict(lambda: 0.0)

def parse_packet(f, packet_format):
  log = []
  packetTime = 0
  packetType = "0"

  for (file_pos, fieldName, fieldType, fieldLength, value) in parseFromFormat(f, packet_format):
    formatName = ""
    extraInfo = ""
    if fieldName == "packetTime":
      packetTime = int(value)
    if fieldName == "packetType":
       _, formatName = formats[value]
       if formatName == "unknown":
        formatName = Fore.GREEN + formatName + Style.RESET_ALL
       elif formatName == "repeating":
        formatName = Fore.BLUE + formatName + Style.RESET_ALL
       else:
         formatName = Fore.RED + formatName + Style.RESET_ALL
    if fieldName == "unitType":
      extraInfo = Fore.GREEN + unitTypeMap[value] + Style.RESET_ALL
    if fieldName == "buildingType":
      extraInfo = Fore.GREEN + buildingTypeMap[value] + Style.RESET_ALL
    if fieldName == "unitId":
      extraInfo = Fore.YELLOW + value + Style.RESET_ALL

    if "type1092_" in fieldName:
        if type1092_lastValue[fieldName] != float(value):
            print("camera_position " + Fore.YELLOW + f"{fieldName} = {value}" + Style.RESET_ALL)
            type1092_lastValue[fieldName] = float(value)
      
    log += [f"{packetTime}; {file_pos}; {fieldName}; {fieldType}; {fieldLength}; {value}; {formatName}; {extraInfo}"]
  f.seek(f.tell() - 8)
  return (value, log, packetTime)

def repetitionsOf1092(f):
  count = 0
  nextPacketType = 0
  while(True):
    nextPacketType,log,_ = parse_packet(f, format1092)

    if nextPacketType != "1092":
        break

    count += 1
  print(f"> {count} repetitions of 1092, ending with {nextPacketType}")

def parse(f, untilGameTimestamp=0, isLive=False, nextPacketType=0):
  lastPacketType = 0
  lastPacketPos = 0

  importlib.reload(packets)

  count1092 = 0
  if nextPacketType == 0:
      print(f"> header")
      if isLive:
        nextPacketType,log,packetTime = parse_packet(f, packets.formatLiveReplayHeader)
      else:
        nextPacketType,log,packetTime = parse_packet(f, packets.formatHeader)
      print("\n".join(log))
      print(f"{log[-1]}")
  while f.tell() < os.fstat(f.fileno()).st_size - 4:
    if nextPacketType in packets.formats:
        formatList, _ = packets.formats[nextPacketType]
        currentPacketType = nextPacketType
        try:
            lastPacketType = nextPacketType
            lastPacketPos = f.tell()
            nextPacketType, log, packetTime = parse_packet(f, formatList)
        except Exception as e:
            print(f"parse failed {e}")
            return (lastPacketType,lastPacketPos)

        if currentPacketType != "1092":
            if count1092 > 0:
                print(f"> repetitions of 1092: {count1092}")
                count1092 = 0
            if nextPacketType != "27":
                if nextPacketType in packets.formats:
                    _, formatName = packets.formats[nextPacketType]
                else:
                    print("\n".join(log))
                    print(f"can't find next package type {nextPacketType}")
                    break
            else:
                formatName = "end"
            print("\n".join(log))
        else:
            count1092 += 1
    else:
        print(f"packet {nextPacketType} not found")
        break
    if not isLive and untilGameTimestamp != 0 and untilGameTimestamp < int(packetTime):
      print("done")
      return (0,0)
    print(Style.RESET_ALL, end="")

  print("> Made it to")
  file_pos = f.tell()
  file_len = os.fstat(f.fileno()).st_size
  file_pos_pcnt = file_pos / (file_len / 100)
  print(f"{f.tell()} of {file_len} ({'{:.2f}'.format(file_pos_pcnt)}%)")

  print("> Next 400 bytes after PacketType are")
  f.seek(lastPacketPos)
  value = ""
  for no in range(0, 200):
    value += str(f.read(1).hex())
  print(value)

  return (lastPacketType,lastPacketPos)
