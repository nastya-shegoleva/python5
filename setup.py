from cx_Freeze import setup, Executable
executable = [Executable('data.ру')]
setup(name='Hello', version='0.0.1', desriptopn='nast', executable=executable)