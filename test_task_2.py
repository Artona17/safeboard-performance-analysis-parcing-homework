import pytest
import task_2 as task


def test_empty():
    cmd_empty = task.CmdReading()
    assert cmd_empty.do_get_params('') == 'Передайте аргументы соответственно Readme.'


def test_cpu_init_with_non_existent_file():
    assert task.CpuInfo('non-existent.csv') == 'FileNotFoundError'


def test_cpu_top():
    cpu = task.CpuInfo("test_cpu.csv")
    assert cpu.top(lim_processes=1, lim_libs=2) == ([['assflame.dll', 'assflame1.dll']], ['DarkSouls3.exe'])


def test_file_io_top():
    file_io_info = task.FileIOInfo("test_file_io.csv")
    assert file_io_info.top(lim=1) == ['MicrosoftEdgeUpdate.exe (17548)']

#def test_reporter_cpu():
#
#def test_reporter_file_io():