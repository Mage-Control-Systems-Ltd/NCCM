import pytest
import wx
import wx.grid
import os
from nccm_action import NetClassClearanceMatrix, Info, convert_to_float, MAX, MIN

# INFO: Please remember to open the test-project-nccm.kicad_pcb before running the tests
# since the KiCAD Plugin API attaches to a running KiCAD instance.


@pytest.fixture(scope="module")
def app():
    app = wx.App(False)
    yield app
    app.Destroy()


@pytest.fixture
def frame(app):
    frame = NetClassClearanceMatrix()
    yield frame
    frame.Destroy()


def test_frame_title(frame: NetClassClearanceMatrix):
    assert frame.GetTitle() == "Net Class Clearance Matrix"


def test_info_dialogue(app):
    info_dialogue = Info("Text")
    assert info_dialogue.GetTitle() == "Net Class Clearance Matrix"


def test_init(frame: NetClassClearanceMatrix):
    assert frame.class_count == 5

    net_class_names = []
    for net_class in frame.net_classes:
        net_class_names.append(net_class.name)

    expected_net_class_names = [
        "Default",
        "BAT+",
        "BAT-",
        "LED",
        "THIS_IS_A_LONG_NET_CLASS_NAME",
    ]
    assert net_class_names == expected_net_class_names


def test_generate_coords(frame: NetClassClearanceMatrix):
    expected_valid_coords = [
        (0, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
        (0, 4),
        (1, 4),
        (2, 4),
        (3, 4),
        (4, 4),
    ]
    expected_invalid_coords = [
        (4, 0),
        (4, 3),
        (3, 1),
        (1, 0),
        (4, 2),
        (3, 0),
        (2, 1),
        (3, 2),
        (4, 1),
        (2, 0),
    ]

    assert expected_valid_coords == frame.valid_coords
    assert expected_invalid_coords == frame.invalid_coords


def test_get_existing_data(frame: NetClassClearanceMatrix):
    dru_file = frame.project.name + ".kicad_dru"
    dru_path = os.path.join(frame.project.path, dru_file)
    expected_class_val_dict = {("BAT-", "LED"): "5.0mm"}

    # Check the correct data is read
    assert expected_class_val_dict == frame.class_val_dict

    # Check that if not file is found it returns 1
    new_dru_file = frame.project.name + ""
    new_dru_path = os.path.join(frame.project.path, new_dru_file)
    os.rename(dru_path, new_dru_path)
    assert frame.get_existing_data() == 1
    os.rename(new_dru_path, dru_path)

    f_read = open(dru_path, "r")
    file_contents = f_read.read()
    f_read.close()

    # Check that if it's an empty file it returns 1
    f_write = open(dru_path, "w")
    f_write.write("")
    f_write.close()
    assert frame.get_existing_data() == 1

    # Write the original data to it again
    f_write = open(dru_path, "w")
    f_write.write(file_contents)
    f_write.close()


def test_check_cells(frame: NetClassClearanceMatrix):
    frame.check_cells(wx.grid.EVT_GRID_CELL_CHANGED)
    expected_coord_val_dict = {(2, 3): 5.0}

    assert expected_coord_val_dict == frame.coord_val_dict


def test_update_custom_rules(frame: NetClassClearanceMatrix):
    dru_file = frame.project.name + ".kicad_dru"
    dru_path = os.path.join(frame.project.path, dru_file)

    f_read = open(dru_path, "r")
    file_contents_before_test = f_read.read()
    f_read.close()

    frame.check_cells(wx.grid.EVT_GRID_CELL_CHANGED)
    frame.update_custom_rules(wx.EVT_BUTTON)

    f_read = open(dru_path, "r")
    file_contents_after_test = f_read.read()
    f_read.close()

    assert file_contents_before_test.strip() == file_contents_after_test.strip()

    os.remove(dru_path)
    frame.update_custom_rules(wx.EVT_BUTTON)

    f_read = open(dru_path, "r")
    file_contents_after_test = f_read.read()
    f_read.close()

    assert file_contents_before_test.strip() == file_contents_after_test.strip()


def test_remove_from_custom_rules(frame: NetClassClearanceMatrix):
    dru_file = frame.project.name + ".kicad_dru"
    dru_path = os.path.join(frame.project.path, dru_file)

    f_read = open(dru_path, "r")
    file_contents_before_test = f_read.read()
    f_read.close()

    # Not sure how to suppress the dialogue from showing here
    frame.remove_from_custom_rules(wx.EVT_BUTTON)

    f_read = open(dru_path, "r")
    file_contents_after_test = f_read.read()
    f_read.close()

    f_write = open(dru_path, "w")
    f_write.write(file_contents_before_test)
    f_read.close()

    assert file_contents_after_test.strip() == r"(version 1)"

    for valid_coords in frame.valid_coords:
        assert frame.gridNCCM.GetCellValue(valid_coords) == ""


def test_convert_to_float():
    assert convert_to_float("0.1234567") == 0.123456
    assert convert_to_float("999999999") == MAX
    assert convert_to_float("-0.1234567") == MIN
    assert convert_to_float("test") == MIN
