# Net Class Clearance Matrix (NCCM) KiCad Plugin
# Copyright (C) 2025 Mage Control Systems Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re

import kipy
from kipy import errors
import wx
from wx import PyEventBinder

from nccm_gui import NetClassClearanceMatrixDialog, InfoDialog

__version__ = "0.1.2"
__author__ = "Yiannis Michael (ymich9963)"
__license__ = "GNU General Public License v3.0 only"

# Numeric constants
MIN = 0.000000
MAX = 999.999999
DP = 6
COL_WIDTH = 100
MAX_CHAR_COL_LABEL = 12

# Section strings
SECTION_START_STR = "### 4E43434D NCCM SECTION START ###\n"
SECTION_END_STR = "### 4E43434D NCCM SECTION END ###\n"

# Rule strings
START_OF_RULE_NAME = 'rule "CLR_'
START_OF_CLEARANCE = "  (constraint clearance (min "


class NetClassClearanceMatrix(NetClassClearanceMatrixDialog):
    """wxWidgets Frame class for the NCCM.

    :param kicad: A connection to a running KiCad instance.
    :param board:  A reference to the PCB open in KiCad, if one exists.
    :param project: The project that the board is a part of.
    :param net_classes: A list of the board net classes.
    :param class_count: Number of net classes.
    :param valid_coords: List containing the valid coordinates of the table.
    :param invalid_coords: List containing the invalid coordinates of the table.
    :param coord_val_dict: Dictionary containing coordinates and their value as key-value pairs.
    :param class_val_dict: Dictionary containing the two classes and their value as key-value pairs.
    :param rule_strings: List of the rule strings to be used.
    """

    def __init__(self):
        super(NetClassClearanceMatrix, self).__init__(None)
        self.kicad = kipy.KiCad()

        try:
            self.board = self.kicad.get_board()
        except errors.ConnectionError:
            self.show_dialog("Please open KiCad before using the NCCM plugin.")
            wx.Exit()
        except errors.ApiError:
            self.show_dialog(
                "Unable to connect to a board file.\nPlease make sure one is open."
            )
            wx.Exit()

        self.project = self.board.get_project()
        self.net_classes = self.project.get_net_classes()
        self.class_count = len(self.net_classes)
        self.valid_coords = []
        self.invalid_coords = []
        self.coord_val_dict = {}
        self.class_val_dict = {}
        self.rule_strings = []

        self.generate_coords("top")
        self.init_grid()
        self.get_existing_data()
        self.refresh_sizes()

    def get_existing_data(self) -> int:
        """Get data from the existing project kicad_dru file.

        :return: 0 or 1, used when testing the function
        """
        dru_file = self.project.name + ".kicad_dru"

        if dru_file in os.listdir(self.project.path):
            # Open the file to read its contents
            f_read = open(os.path.join(self.project.path, dru_file), "r")
            file_contents = f_read.readlines()
            f_read.close()

            # Extract the NCCM section
            section_lines = get_or_remove_section(file_contents, "get")
        else:
            return 1

        # If no section is found then just return
        if not section_lines:
            return 1

        self.class_val_dict = get_class_val_dict_from_section(section_lines)

        # regex to get the number from the string
        reg_float = re.compile(r"^\d+[.,]?\d*")

        # Add matrix data to the grid
        for c in range(self.class_count):
            col = self.gridNCCM.GetColLabelValue(c)
            for r in range(self.class_count):
                row = self.gridNCCM.GetRowLabelValue(r)
                for val, _ in self.class_val_dict.items():
                    if val == (col, row):
                        value_float = reg_float.findall(self.class_val_dict[(col, row)])
                        self.gridNCCM.SetCellValue(
                            (c, r), value_float[0] + " mm"
                        )



        self.refresh_sizes()

        return 0

    def generate_coords(self, use_top_bot: str):
        """Generate both valid and invalid grid coordinates

        :param use_top_bot: Use the top or bottom diagonal table section for the valid coords.
        """

        # Get all the coords
        coords_list = list()
        for col in range(self.class_count):
            for row in range(self.class_count):
                coords_list.append((row, col))

        # Use the section from the top of the diagonal or the bottom
        if use_top_bot == "top":
            # Get the valid coords that will have data
            for col in range(self.class_count):
                for row in range(self.class_count):
                    self.valid_coords.append((row, col))
                    if row == col:
                        break
        elif use_top_bot == "bot":
            for row in range(self.class_count):
                for col in range(self.class_count):
                    self.valid_coords.append((row, col))
                    if row == col:
                        break

        # Get the difference between the two lists to get the invalid coords
        self.invalid_coords = list(set(coords_list) ^ set(self.valid_coords))

    def check_cells(self, event: PyEventBinder):
        """Check that all cells in the valid coordinates are the correct value.

        :param event: wxWidgets PyEventBinder.
        """
        for invalid_coord in self.invalid_coords:
            self.gridNCCM.SetCellValue(invalid_coord, "-")

        # Create a dict to relate the value to the coordinate
        cell_value_dict = {key: float() for key in self.valid_coords}

        # regex to get the number from the string
        reg_float = re.compile(r"^\d+[.,]?\d*")

        # Check all cells for valid numbers, store them, and add 'mm' at the end
        for valid_coord in self.valid_coords:
            cell_value_str = self.gridNCCM.GetCellValue(valid_coord)

            cell_value_float = reg_float.findall(cell_value_str)

            # Get only the results with values
            if cell_value_float and len(cell_value_float) == 1:
                value_float = convert_to_float(cell_value_float[0])
                cell_value_dict[valid_coord] = value_float
                self.gridNCCM.SetCellValue(valid_coord, str(value_float) + " mm")
            else:
                self.gridNCCM.SetCellValue(valid_coord, "")

        # Extract the non-zero values
        self.coord_val_dict = {
            key: val for key, val in cell_value_dict.items() if val != 0
        }

        # Refresh the table and window size so that new data is visible
        self.refresh_sizes()

    def init_grid(self):
        """Initialise the grid by adding class names, refreshing size, setting default
        column header size, and setting the invalid coords to have the dash and colouring."""

        # Adds the class names to the grid
        for pos, net_class in enumerate(self.net_classes):
            self.gridNCCM.AppendRows(1, True)
            self.gridNCCM.SetRowLabelValue(pos, net_class.name)
            self.gridNCCM.AppendCols(1, True)
            self.gridNCCM.SetColLabelValue(pos, net_class.name)

        # Set the column headers to be the same size as other cells
        self.gridNCCM.SetColLabelSize(self.gridNCCM.GetRowSize(0))

        # Set the default column width
        for col in range(self.class_count):
            self.gridNCCM.SetColSize(col, COL_WIDTH)
            if len(self.gridNCCM.GetColLabelValue(col)) > MAX_CHAR_COL_LABEL:
                self.gridNCCM.AutoSizeColumn(col)

        self.auto_size_row_labels_width()

        # Set the invalid coords to have dashes
        for invalid_coord in self.invalid_coords:
            self.gridNCCM.SetCellValue(invalid_coord, "-")
            self.gridNCCM.SetCellBackgroundColour(
                invalid_coord[0],
                invalid_coord[1],
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_SCROLLBAR),
            )

    def auto_size_row_labels_width(self):
        """Adjust row label width to fit the longest label."""
        dc = wx.ClientDC(self.gridNCCM)
        dc.SetFont(self.gridNCCM.GetLabelFont())

        max_width = 0
        for row in range(self.gridNCCM.GetNumberRows()):
            label = self.gridNCCM.GetRowLabelValue(row)
            width, _ = dc.GetTextExtent(label)
            max_width = max(max_width, width)

        # Add padding (e.g., 10 pixels)
        self.gridNCCM.SetRowLabelSize(max_width + 10)


    def refresh_sizes(self):
        """Refresh the window when new data is added to the matrix"""

        # Refresh grid and window
        self.gridNCCM.ForceRefresh()

        # Gets the best size based on the new grid size
        self.SetSizeHints(self.GetBestSize())

        # Fits the window to the new size
        self.Fit()

    def gui_exit(self, event: PyEventBinder):
        """Exit the GUI.

        :param event: wxWidgets PyEventBinder.
        """
        wx.Exit()

    def update_custom_rules(self, event: PyEventBinder):
        """Update the custom rules file.

        :param event: wxWidgets PyEventBinder.
        """
        dru_file = self.project.name + ".kicad_dru"
        file_created = False

        # Check if it exists and if it doesn't create it and add the necessary version string
        # If it does exist then remove the previously inserted section
        if dru_file in os.listdir(self.project.path):
            # Open the file to read its contents
            f_read = open(os.path.join(self.project.path, dru_file), "r")
            file_contents = f_read.readlines()
            f_read.close()

            # Open the file and write to it its old contents minus the NCCM section
            f_write = open(os.path.join(self.project.path, dru_file), "w")

            # First check if the version string is there
            found_version = False
            for line in file_contents:
                if "(version 1)" in line.strip():
                    found_version = True
                    break

            if not found_version:
                f_write.write("(version 1)\n")

            file_contents = get_or_remove_section(file_contents, "remove")

            for line in file_contents:
                f_write.write(line)

            f_write.close()
        else:
            file_created = True
            f_write = open(os.path.join(self.project.path, dru_file), "w")
            f_write.write("(version 1)\n")
            f_write.close()

        # Write custom rules to file
        f_write = open(os.path.join(self.project.path, dru_file), "a")
        self.rule_strings = self.get_rule_strings()

        f_write.write(SECTION_START_STR)

        for rule in self.rule_strings:
            f_write.write(rule)

        f_write.write(SECTION_END_STR)
        f_write.close()

        if file_created:
            self.show_dialog(
                "No custom rules file (.kicad_dru) was found,\ntherefore one was created."
            )
        else:
            self.show_dialog("Updated custom rules.")

    def remove_from_custom_rules(self, event: PyEventBinder):
        """Remove the NCCM entry from the custom rules file,
        and also empty the table.

        :param event: wxWidgets PyEventBinder.
        """
        dru_file = self.project.name + ".kicad_dru"

        # If the file doesn't exist simply return from the function.
        if dru_file in os.listdir(self.project.path):
            # Open the file to read its contents
            f_read = open(os.path.join(self.project.path, dru_file), "r")
            file_contents = f_read.readlines()
            f_read.close()

            # Open the file and write to it its old contents minus the NCCM section
            f_write = open(os.path.join(self.project.path, dru_file), "w")

            file_contents = get_or_remove_section(file_contents, "remove")

            for line in file_contents:
                f_write.write(line)

            f_write.close()
        else:
            self.show_dialog("No custom rules file detected.")
            return

        # Empty the table
        for valid_coord in self.valid_coords:
            self.gridNCCM.SetCellValue(valid_coord, "")

        self.show_dialog("Removed NCCM entry from the custom rules file.")

    def show_dialog(self, text: str):
        """Show a dialog with some text.

        :param text: Text to show on the dialog.
        """
        info = Info(text)
        info.ShowModal()

    def get_rule_strings(self) -> list[str]:
        """Get the rule strings based on the table data.

        :return: List of rule strings.
        """
        rule_strings = []
        for key, val in self.coord_val_dict.items():
            col_class = self.gridNCCM.GetColLabelValue(key[0])
            row_class = self.gridNCCM.GetRowLabelValue(key[1])

            # Create the rule and add it to a list containing all the necessary rules
            rule_string = f"\n(rule \"CLR_{col_class}_to_{row_class}\"\n  (severity error)\n  (condition \"A.NetClass == '{col_class}' && B.NetClass == '{row_class}'\")\n  (constraint clearance (min {val}mm))\n)\n"
            rule_strings.append(rule_string)

        return rule_strings


class Info(InfoDialog):
    """Class for the info dialog appearing on certain events."""

    def __init__(self, text):
        super(Info, self).__init__(None)
        self.txtMessage.SetLabelText(text)

    def okay(self, event: PyEventBinder):
        """Destroy the dialog box.

        :param event: wxWidgets event.
        """
        self.Destroy()


def get_or_remove_section(file_contents: list[str], mode: str) -> list[str]:
    """Get the NCCM section or get the file contents without the section.

    :param file_contents: Read file contents.
    :param mode: Specify between "get" or "remove".
    :return: File or section contents.
    """
    check = True
    if mode == "get":
        check = True
    elif mode == "remove":
        check = False

    found_section = False
    content_lines = []
    for line in file_contents:
        if line.find(SECTION_START_STR.strip("\n")) != -1:
            found_section = True
        if line.find(SECTION_END_STR.strip("\n")) != -1:
            found_section = False
            continue
        if found_section is check:
            content_lines.append(line)

    return content_lines


def get_class_val_dict_from_section(section_lines: list[str]) -> dict[tuple, str]:
    """Get the class_val_dict from the NCCM section

    :param section_lines: Lines of the NCCM section.
    :return: A dict with the classes and their corresponding value as key-value pairs.
    """
    classes = ()
    clearance = ""
    rule_name_found = False
    clearance_found = False
    matrix_data_dict = {}

    # Populate the data dict
    for line in section_lines:
        if line.find(START_OF_RULE_NAME) != -1:
            classes = tuple(
                line[len(START_OF_RULE_NAME) + 1 : len(line) - 2].split("_to_")
            )
            rule_name_found = True
        if line.find(START_OF_CLEARANCE) != -1:
            clearance = line[len(START_OF_CLEARANCE) : len(line) - 3]
            clearance_found = True
        if rule_name_found and clearance_found:
            matrix_data_dict[classes] = clearance
            rule_name_found = False
            clearance_found = False

    return matrix_data_dict


def convert_to_float(val: str) -> float:
    """Convert a string value to a float with an amount of decimal points
    determined by the constant DP. Also check it is withing MIN and MAX.

    :param val: String value to convert to float.
    :return: Float value.
    """
    try:
        val_float = float(val)
    except ValueError:
        val_float = float(MIN)

    if val_float < MIN:
        val_float = MIN

    if val_float > MAX:
        val_float = MAX

    # Truncate by converting to string and then back to float
    val_str_list = str(val_float).split(".")
    val_str_list[1] = val_str_list[1][0:DP]
    val_str = ".".join(val_str_list)

    return float(val_str)


if __name__ == "__main__":
    app = wx.App()
    nccm = NetClassClearanceMatrix()
    nccm.Show()
    app.MainLoop()
