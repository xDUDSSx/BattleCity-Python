from __future__ import annotations
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from core.game import Game

import os

from core import constants


class Stage:
    def __init__(self, map_file: str, stage_number: int, stage_index: int):
        self.number = stage_number
        self.index = stage_index

        self.tanks = constants.DEFAULT_TANK_COUNT
        self.max_tanks_at_once = constants.MAX_TANKS_AT_ONCE
        self.flag_lives = 1
        self.player_lives = constants.PLAYER_LIVES

        self.active_tanks = self.tanks
        self.active_flag_lives = self.flag_lives
        self.active_player_lives = self.player_lives

        self.map_file = map_file
        self.map_data = self.load_stage_file(map_file)

    def load(self, game: Game):
        game.game_map.generate_map_from_map_data(self.map_data, game)

        self.active_tanks = self.tanks
        self.active_flag_lives = self.flag_lives
        self.active_player_lives = self.player_lives

    def load_stage_file(self, file_path: str) -> dict:
        """
        Loads and validates a stage file.

        Stage files can begin with any number of commands on each line in the format:
        COMMAND=VALUE
        Every line after the last command will be considered a part of the map.
        The file ends with a newline OR last symbol of the map.

        Throws a RuntimeError on failure.
        :param file_path:
        :return: A dictionary with information about the loaded map. Contains keys
        "lines" (list of str), "width" (int), "height" (int), "pixel_width" (int) and "pixel_height" (int).
        """
        with open(file_path, 'r') as stage_file:
            stage_lines = stage_file.readlines()

            if not stage_lines:
                raise RuntimeError(f"Stage file for stage {self.number} contains no lines!")

            command_count = 0
            for i in range(len(stage_lines)):
                line = stage_lines[i].rstrip()
                if "MAP=" in line:  # Stop loading commands on the MAP command
                    command_count += 1
                    break

                command = Stage.parse_stage_file_command(line)
                if command is None:
                    print(f"Invalid command at line {i+1}: '{line}' in stage {self.number}")
                    command_count += 1
                    continue

                try:
                    if not self.process_command(command):
                        print(f"Unknown command '{command[0]}' on line {i+1}"
                              f" in stage {self.number}.")
                except Exception as e:
                    print(f"Failed to process command '{command[0]}' on line {i+1}"
                          f" in stage {self.number}. Message: '{e}'")
                command_count += 1

            map_lines = stage_lines[command_count:]
            return Stage.generate_map_data(map_lines, command_lines=command_count)

    def process_command(self, command: list) -> bool:
        """
        Processes a stage file command.
        :param command: The command. A list of lengtg 2: [command: str, value: str].
        :return: True if command was processed successfully.
        """
        if command[0] == "TANKS":
            self.tanks = int(command[1])
            self.active_tanks = self.tanks
        elif command[0] == "MAX_TANKS":
            self.max_tanks_at_once = int(command[1])
        elif command[0] == "MAP":
            pass
        else:
            return False

        return True

    @staticmethod
    def parse_stage_file_command(line: str) -> Union[list, None]:
        """
        Looks for and a stage file command in a line.
        :param line: Line of text
        :return: A list containing [command: str, value: str] if property was successfully parsed, None if invalid
        """
        if "=" not in line:
            return None
        parts = line.split("=")
        if len(parts) != 2:
            return None
        return parts

    @staticmethod
    def generate_map_data(map_lines: list, command_lines=0):
        first_line_width = len(map_lines[0].rstrip())
        for i in range(0, len(map_lines)):
            map_lines[i] = map_lines[i].rstrip()
            if len(map_lines[i]) != first_line_width:
                raise RuntimeError(
                    f"Map file line width is inconsistent at line {i + 1 + command_lines} ({len(map_lines[i])} != {first_line_width})! "
                    "(All lines must be the same width as the first one)")

        map_data = {
            "lines": map_lines,
            "width": len(map_lines[0]),
            "height": len(map_lines),
            "pixel_width": len(map_lines[0]) * constants.TILE_SIZE,
            "pixel_height": len(map_lines) * constants.TILE_SIZE
        }
        return map_data

    @staticmethod
    def load_stages(stage_folder_path: str) -> list:
        """
        Goes through the stage folder and loads stages from files whose filename matches the pattern:
        stage[1-9]*\.?.*
        :param stage_folder_path: The stage folder absolute path.
        :return: A list of Stage objects.
        :raises RuntimeError on failure.
        """
        stages = []
        stage_numbers = []
        for file in os.listdir(stage_folder_path):
            if len(file) > 5 and file[0:5] == "stage" and file[5:].split(".")[0].isdigit():
                stage_number = int(file[5:].split(".")[0])
                try:
                    stage_path = stage_folder_path + os.sep + file
                    new_stage = Stage(stage_path, stage_number, len(stages))
                except RuntimeError as e:
                    print(f"Failed to load stage {stage_number} at {stage_path}!\nMessage: {e}")
                    stages.append(None)
                    stage_numbers.append(stage_number)
                    continue

                stages.append(new_stage)
                stage_numbers.append(stage_number)

        if len(set(stage_numbers)) != len(stage_numbers):
            raise RuntimeError("The stages folder contains two stages with the same stage number!")
        if len(stages) <= 0:
            raise RuntimeError("No stages found in the stage folder! "
                               "At least a single stage file should be present (stage1.txt).")

        return stages