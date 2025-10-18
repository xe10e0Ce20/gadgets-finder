import pandas as pd
import re
import copy

try:
    file_path = input("Input disas.csv name(default:_disas.csv): ")
    if not file_path:
        file_path = "_disas.csv"
    maxlen = input("Max length(default:2): ")
    if not maxlen:
        maxlen = 2
    else:
        maxlen = int(maxlen)

    use_re = input("Use regular expression?(y/n, default=n): ") == "y" 
    ignore_B_command = input("Ignore B, BL, BC AL command?(y/n, default=n): ") == "y"
    ignore_BC_command = input("Ignore BC command?(y/n, default=y): ") != "n"
    command_to_find = []

    while True:
        inputed = input("search for command(s): ")
        if inputed:
            command_to_find.append(inputed)
        else:
            break

    disas_df = pd.read_csv(file_path, header=None, index_col=False)

    # 1. 仅保留地址和指令列
    temp = disas_df.iloc[:, [0, 2]]

    # 2. 将第 0 列（地址）设置为索引
    # 3. 将第 2 列（指令）转换为字典
    disas = temp.set_index(temp.columns[0])[temp.columns[1]].to_dict()
    print(f"Succssfully read {file_path}")

except Exception as e:
    print(e)


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

def getcommand(disas:dict[str,str], addr:str):
    try:
        result = disas[addr]
        return result
    except KeyError:
        print(f"Warning: Trying to get command at {addr}, but the address does not exist seemingly")
        return None

def getbaddr(command:str):
    if command.startswith("BC"):
        addr = command[-6:-1]
    elif not "R" in command:
        addr = f"{command[-9]}{command[-5:-1]}"
    return addr


class gadgetfinder():
    def __init__(self, maxlen):
        self.bl_list = []
        self.maxlen = maxlen

    def find_gadget(self, address:str, parent_gadget={}):
        addr = address
        maxlen = self.maxlen
        output = []
        gadget = copy.deepcopy(parent_gadget)
        while True:
   
            command = getcommand(disas, addr)
            if not command: break
            if len(gadget)>=maxlen: break
            gadget[addr] = command
            if command == "POP  PC" or command == "RT":
                output.append(gadget)
                break
            elif command.startswith("BC") and not command.startswith("BC  AL"):
                if ignore_BC_command: break
                else: 
                    baddr = getbaddr(command)
                    if not baddr in self.bl_list:
                        self.bl_list.append(baddr)
                        children = self.find_gadget(baddr, gadget)
                        for item in children:
                            output.append(item)
                    else: pass
                add2(addr)
            elif command.startswith("B") and not "R" in command:
                if ignore_B_command: break
                else:
                    baddr = getbaddr(command)
                    if not baddr in self.bl_list:
                        self.bl_list.append(baddr)
                        addr = baddr
                    else: break
            elif (command.startswith("L") or command.startswith("ST  ")) and "h" in command:
                addr = add2(addr)
                addr = add2(addr)
            else:
                addr = add2(addr)
        return output


def findcommandaddr(pattern:str):
    result = [
        address                     # 想要收集的元素：地址 (address)
        for address, command in disas.items()  # 迭代字典的键值对
        if match(command, pattern)
    ]
    return result

def check_ggtmatch(gadget:dict):
    commands = list(gadget.values())
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
    gadgets:list = []
    for addr in addrs:
        output = ggtfnder.find_gadget(addr)
        for item in output:
            gadgets.append(item)


    final_gadgets = []
    for gadget in gadgets:
        if check_ggtmatch(gadget):
            final_gadgets.append(gadget)

    empty_row = pd.DataFrame({0:["", ""], 1:["", ""]})

    concatenated_list = []
    for gadget in final_gadgets:
        ggt = pd.DataFrame(
            gadget.items(), 
            columns=[0,1]
        )
        concatenated_list.append(ggt)
        concatenated_list.append(empty_row)

    if len(concatenated_list)>0:
        result = pd.concat(concatenated_list[:-1], ignore_index=True)

        result.to_csv("result.csv", index=False, header=False)
        print("Result output in result.csv")

    else:
        print("No gadgets found.")

if __name__ == "__main__":
    main()
