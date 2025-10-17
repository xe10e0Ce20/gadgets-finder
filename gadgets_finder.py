import pandas as pd
import re

try:
    file_path = input("Input disas.csv name(default:_disas.csv): ")
    if not file_path:
        file_path = "_disas.csv"
    maxlen = input("Max length(default:2): ")
    if not maxlen:
        maxlen = 2
    else:
        maxlen = int(maxlen)

    use_re = input("Use regular expression?(y/n): ") == "y" 
    ignore_B_command = input("Ignore B, BL, BC AL command?(y/n, default=n): ") == "y"
    ignore_BC_command = input("Ignore BC command?(y/n, default=y: ") != "n"
    command_to_find = []

    while True:
        inputed = input("search for command(s): ")
        if inputed:
            command_to_find.append(inputed)
        else:
            break

    disas = pd.read_csv(file_path, header=None, index_col=False)
except Exception as e:
    print(e)

def flatten_deep_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            # 如果是列表，则递归调用自身，并将结果添加到 flat_list
            flat_list.extend(flatten_deep_list(item))
        else:
            # 否则，直接添加元素
            flat_list.append(item)
    return flat_list


def toint16(string:str):
    return int(string, 16)

def tostr(int16:int):
    return f"{int16:05x}".upper()

def add2(addr:str):
    addr16 = toint16(addr)
    addr16 += 2
    addr = tostr(addr16)
    return addr

def match(tar, input):
    if use_re:
        return bool(re.fullmatch(input, tar))
    else:
        return tar == input

def getcommand(df:pd.DataFrame, addr:str):
    try:
        result = df[df.iloc[:, 0] == addr].iloc[0, 2]
        return result
    except IndexError:
        print(f"Warning: Found command jumping to {addr}, but the address does not exist seemingly")
        return None

def getbaddr(command:str):
    if command.startswith("BC"):
        addr = command[-6:-1]
    elif not "R" in command:
        addr = f"{command[-9]}{command[-5:-1]}"
    return addr

def append(df, addr, command):
    new_row = pd.DataFrame({0:[addr], 1:[command]})
    return pd.concat([df, new_row], ignore_index=True)

class gadgetfinder():
    def __init__(self, maxlen):
        self.bl_list = []
        self.maxlen = maxlen

    def find_gadget(self, address:str, parent_df:pd.DataFrame = pd.DataFrame(columns=[0, 1])):
        addr = address
        maxlen = self.maxlen
        output = []
        df = parent_df
        while True:
            if len(df)>=maxlen:
                break
            
            command:str = getcommand(disas, addr)
            if not command: break
            df = append(df, addr, command)
            if command == "POP  PC" or command == "RT":
                output.append(df)
                break
            elif command.startswith("BC") and not command.startswith("BC  AL"):
                if ignore_BC_command: break
                baddr = getbaddr(command)
                if not baddr in self.bl_list:
                    self.bl_list.append(baddr)
                    children = self.find_gadget(baddr, df)
                    for item in children:
                        output.append(children)
                
                add2(addr)
            elif command.startswith("B") and not "R" in command:
                if ignore_B_command: break
                baddr = getbaddr(command)
                if not baddr in self.bl_list:
                    self.bl_list.append(baddr)
                    addr = baddr
            else:
                addr = add2(addr)
        return output


def findcommandaddr(pattern:str):
    result = []
    for index, row in disas.iterrows():
        command = row[2]
        if match(command, pattern):
            result.append(row[0])
    return result

def check_ggtmatch(gadget:pd.DataFrame):
    commands = gadget.iloc[:, 1]
    i = 0
    match_count = 0
    while True:
        if i>=len(commands):  
            return False  
        if match(commands[i], command_to_find[match_count]):
            match_count+=1
        if match_count>=len(command_to_find):
            return True
        i+=1

def main():
    ggtfnder = gadgetfinder(maxlen)

    addrs = findcommandaddr(command_to_find[0])
    gadgets:list[pd.DataFrame] = []
    for addr in addrs:
        output = ggtfnder.find_gadget(addr)
        output = flatten_deep_list(output)
        for item in output:
            gadgets.append(item)



    final_gadgets = []
    for gadget in gadgets:
        if check_ggtmatch(gadget):
            final_gadgets.append(gadget)

    empty_row = pd.DataFrame({0:["", ""], 1:["", ""]})

    concatenated_list = []
    for gadget in final_gadgets:
        concatenated_list.append(gadget)
        concatenated_list.append(empty_row)

    if len(concatenated_list)>0:
        result = pd.concat(concatenated_list[:-1], ignore_index=True)

        result.to_csv("result.csv", index=False, header=False)
        print("Result output in result.csv")

    else:
        print("No gadgets found.")

if __name__ == "__main__":
    main()
