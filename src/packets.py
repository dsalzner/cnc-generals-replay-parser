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

from collections import defaultdict

formatHeader = [
  ("game", "c", 6),   # GENREP

  ("unknown", "HEX", 7),

  ("numTimecodes", "h", 2),
  ("name", "c", 0),             # Last Replay
  ("buildVersion", "c", 0),     # Version 1.7
  ("buildDate", "c", 0),

  ("unknown", "HEX", 2),

  ("version_major", "B", 1),
  ("unknown_0", "B", 1),
  ("version_minor", "B", 1),

  ("unknown", "HEX", 8),

  ("configuration", "c", 0),

  ("unknown", "HEX", 8),

  ("is_30", "B", 1),

  ("unknown", "HEX", 3),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # e.g. 1092 (see below)
]

formatLiveReplayHeader = [
  ("game", "c", 6),   # GENREP

  ("unknown", "HEX", 7),

  ("numTimecodes", "h", 2),
  ("name", "c", 0),             # Last Replay
  ("buildVersion", "c", 0),     # Version 1.7
  ("buildDate", "c", 0),

  ("unknown", "HEX", 2),

  ("version_major", "B", 1),
  ("unknown_0", "B", 1),
  ("version_minor", "B", 1),

  ("unknown", "HEX", 8),

  ("configuration", "c", 0),
  ("build_date", "c", 0),

  ("unknown", "HEX", 2),

  ("unknown", "I", 4), # TODO: number of fields may vary depending on selected map (!)
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # e.g. 1092 (see below)
]


format1097 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 14),

  ("nextPacketTime", "I", 4), # 1097
  ("nextPacketType", "I", 4),
]

format1092 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("is_2", "B", 1),
  ("is_4", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("type1092_x", "f", 4),
  ("type1092_y", "f", 4),
  ("type1092_z", "f", 4),

  ("unknown", "HEX", 24),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # 1095 or 1092
]

format1095 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 14),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # 1097
]

format1097 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 14),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # 1092
]

format1003 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 8),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1001 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 8),
  ("unitCount", "B", 1),
  ("is_1", "B", 1),

  ("unitId", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1047 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4), # 1047

  ("unknown", "HEX", 7),

  ("unitType", "B", 1),
  ("buildingIdUnitWasCreated", "B", 1),

  ("unknown", "HEX", 2),

  ("unitNoFromSameBuilding", "B", 1),

  ("unknown", "HEX", 3),

  ("nextPacketTime", "I", 4),
  ("nextPackageType", "I", 4), # 1092
]

format1049 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4), # 1049

  ("unknown", "HEX", 11),

  ("buildingType", "h", 2),
  #("unknown", "B", 1),

  ("unknown", "HEX", 2),

  ("x", "f", 4),
  ("y", "f", 4),
  ("z", "f", 4),

  ("unknown", "HEX", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1068 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4), # 1049

  ("unknown", "HEX", 7),

  ("x", "f", 4),
  ("y", "f", 4),
  ("z", "f", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4)
]

format1043 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 25),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # 1092
]

format1066 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 15),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4), # 1092
]

format1054 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 5),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1060 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 11),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1002 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 8),

  ("type1002_length", "B", 1),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1058 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 5),

  ("type1058_length", "B", 1),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1051 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 62),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1052 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 5),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1044 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 11),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1045 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 17),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1078 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),
  ("unknown", "B", 1),

  ("unknown", "HEX", 60),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1067 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 11),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1065 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 11),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1053 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 11),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1069 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 19),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1074 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "HEX", 5),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1038 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("x", "f", 4),
  ("y", "f", 4),
  ("z", "f", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1042 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1062 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),
  ("unknown", "B", 1),
  ("unknown", "B", 1),

  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1061 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),
  ("unknown", "B", 1),
  ("unknown", "B", 1),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

format1072 = [
  ("packetTime", "I", 4),
  ("packetType", "I", 4),

  ("unknown", "B", 1),

  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("unknown", "I", 4),
  ("unknown", "I", 4),

  ("nextPacketTime", "I", 4),
  ("nextPacketType", "I", 4),
]

formats = {
  "1097" : (format1097, "unknown"),
  "1092" : (format1092, "camera_position"),
  "1095" : (format1095, "repeating"),
  "1003" : (format1003, "related_to_select?"),
  "1001" : (format1001, "select_unit"),
  "1049" : (format1049, "create_building"),
  "1068" : (format1068, "move_order"),
  "1047" : (format1047, "create_unit"),
  "1043" : (format1043, "set_waypoint?"),
  "1066" : (format1066, "unit_enter_structure"),
  "1054" : (format1054, "all_unit_exit_structure"),
  "1060" : (format1060, "attack_order"),
  "1002" : (format1002, "multi_unit_enter?"),
  "1058" : (format1058, "?"),
  "1051" : (format1051, "stop_build"),
  "1052" : (format1052, "sell_building"),
  "1044" : (format1044, "use_experience_points"),
  "1045" : (format1045, "building_upgrade"),
  "1078" : (format1078, "building_feature"),
  "1067" : (format1067, "gather_supplies"),
  "1065" : (format1065, "continue_building"),
  "1053" : (format1065, "single_unit_exit_structure?"),
  "1069" : (format1069, "attack_move"),
  "1074" : (format1074, "unit_stop"),
  "1038" : (format1038, "vehicle_attack"),
  "1042" : (format1042, "capture_building"),
  "1062" : (format1062, "vehicle_to_repair?"),
  "1061" : (format1061, "attack_nothing"),
  "1072" : (format1072, "guard"),
}

"""
buildingTypeMap = defaultdict(lambda: "unknown", {
  # China Tank General
  "1994" : "Nuclear Reactor",
  "1996" : "Barracks",
  "1999" : "Bunker",
  "2001" : "Gattling Gun",
  "1995" : "Supply Center",
  "1998" : "War Factory",
  "2002" : "Internet Center",
  "2000" : "Propaghanda Center",
  "2003" : "Command Center",
  "1997" : "Air Field",
  "1992" : "Nuclear Missile",

  # Usa Laser General
  "1562" : "Laser Turret",
  "1550" : "Cold Fusion Reactor",
  "1556" : "Barracks",
  "1558" : "Supply Center",
  "1557" : "Fire Base",
  "1549" : "War Factory",
  "1553" : "Air Field",
  "1552" : "Strategy Center",
  "1551" : "Particle Canon",
  "1555" : "Supply Drop Zone",

  # Gla
  "1261" : "Gla Barracks",
  "1256" : "Gla Supply Stash"
})
"""

buildingTypeMap = defaultdict(lambda: "unknown", {
  "1264" : "China Barracks",
  "1280" : "China Bunker",
})

unitTypeMap = defaultdict(lambda: "unknown", {
   "6" : "China Red Guard",
   "8" : "China Tank Hunter",
   "29" : "China Construction Dozer",
})

unitBuildTimeMap = defaultdict(lambda: 1, {
   "6" : 19,
   "8": 9,
   "29": 12,
})

buildingBuildTimeMap = defaultdict(lambda: 1, {
    "1264": 21,
    "1280": 12,
})
