import pandas as pd


file_path = input("Input file name: ")

str_to_find = []

while True:
    inputed = input("search for command(s):")
    if inputed:
        str_to_find.append(inputed)
    else:
        break

df = pd.read_csv(file_path, header=None, index_col=False)

def toint16(string:str):
    return int(string, 16)

def tostr(int16:int):
    return f"{int16:05x}"

def adr_add1(addr:str):
    addr16 = toint16(addr)
    addr16 += 1
    addr = tostr(addr16)

class gadgetfinder():
    def __init__(self):
        self.bl_list = []

    def find_gadget(self, address:str, last_df:pd.DataFrame):
        address = address
        while True:
            condition = (df.iloc[:, 0] == address)
            result_command = df.loc[condition, df.columns[2]]