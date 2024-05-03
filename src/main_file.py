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

replay_file = os.path.join("..", "data", "2023-11-23_21-38-27_china-moving-around.rep")
is_live_replay = False

print(f"=== {replay_file} ===")
with open(replay_file, "rb") as f:
    parse(f, 0, is_live_replay)
