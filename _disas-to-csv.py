import re
import pandas as pd

def process_and_convert_to_csv(input_filename, output_filename):

    processed_data = []

    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue  # 跳过空行

                original_line = line # 保留原始行用于后续处理

                # --- 步骤 1: 查找并定位前两个分隔符 ---
                
                # 正则表达式用于匹配 2 个或更多空格
                pattern = r' {2,}'
                
                # 查找第一个分隔符
                match1 = re.search(pattern, original_line)
                
                if not match1:
                    print(f"警告: 行 '{original_line}' 没有有效分隔符。跳过。")
                    continue
                
                # 第一次替换后的行（用于定位第二个分隔符）
                temp_line = original_line[:match1.start()] + ',' + original_line[match1.end():]
                
                # 查找第二个分隔符 (从第一个分隔符之后的位置开始)
                search_start_index = match1.start() + 1
                match2 = re.search(pattern, temp_line[search_start_index:])

                if not match2:
                    print(f"警告: 行 '{original_line}' 只有 1 个有效分隔符。跳过。")
                    continue

                # 计算第二个匹配在原行中的真实索引
                start2_in_temp = search_start_index + match2.start()
                end2_in_temp = search_start_index + match2.end()

                # --- 步骤 2: 提取列 ---
                
                # 第1列: 第一个分隔符之前
                col1 = original_line[:match1.start()]
                
                # 第2列: 第一个分隔符之后，第二个分隔符之前（在原行中）
                # 注意：我们必须回到 original_line 中找到第2列的边界
                col2_raw_start = match1.end() 
                col2_raw_end = match2.start() + match1.end() # 这一步需要仔细计算在原行中的位置

                # 由于 temp_line 只是用逗号替换了第一个分隔符，我们可以用 temp_line 的索引来帮助分割
                # Col1 是 temp_line[:match1.start()]
                # Col2 是 temp_line[match1.start() + 1 : start2_in_temp]
                # Col3 是 temp_line[end2_in_temp:]

                col1 = temp_line[:match1.start()]
                col2 = temp_line[match1.start() + 1 : start2_in_temp]
                col3_raw = temp_line[end2_in_temp:]
                col1 = col1[1:]

                # --- 步骤 3: 标准化列 3 的空格 ---
                
                # 替换所有连续两个或更多空格为两个空格
                col3_standardized = re.sub(pattern, '  ', col3_raw)

                # --- 步骤 4: 组装最终的 CSV 行 ---
                
                # 最终第3列用双引号包裹
                col3_quoted = f'"{col3_standardized}"'
                
                # 组装成最终的CSV行 (使用标准逗号分隔)
                csv_line = f"{col1},{col2},{col3_quoted}"
                processed_data.append(csv_line)

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_filename}")
        return

    # 写入最终的CSV文件
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
            for row in processed_data:
                outfile.write(row + '\n')
        print(f"成功将数据初步处理到 {output_filename}")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")

input_file = input("Input file name: ")
output_file = input_file.replace(".txt", ".csv")

process_and_convert_to_csv(input_file, output_file)



def toint16(string:str):
    return int(string, 16)

def tostr(int16:int):
    return f"{int16:05x}".upper()

def add2(addr:str):
    addr16 = toint16(addr)
    addr16 += 2
    addr = tostr(addr16)
    return addr



df = pd.read_csv(output_file, header=None, index_col=False)
commands_dict = dict(zip(df[1], df[2]))



# 用于存储所有新行的列表
new_rows_list = []

# 迭代原始 DataFrame，使用 iterrows() 获取索引和行数据
for index, row in df.iterrows():
    # 步骤 A: 将原始行添加到列表中 (用于保持原有顺序)
    # 使用原始索引作为临时排序键
    new_rows_list.append({
        '_temp_order': index,
        'Col1': row[0],
        'Col2': row[1],
        'Col3': row[2]
    })

    # 步骤 B: 检查第二列的长度条件
    if len(row[1]) > 5:
        # a = Col1, b = Col2
        a = row[0]
        b = row[1]

        # 1. c (新 Col1) = function(a)
        new_col1 = add2(a)

        # 2. d (新 Col2) = b 的最后五个字符
        new_col2 = b[-5:]

        # 3. e (新 Col3) = dict[d], KeyError 则为 "Unknown"
        try:
            new_col3 = commands_dict[new_col2]
        except KeyError:
            new_col3 = "Unknown"

        # 步骤 C: 将新行添加到列表中
        # 使用原始索引 + 0.5 作为临时排序键，确保新行紧跟在原行之后
        new_rows_list.append({
            '_temp_order': index + 0.5,
            'Col1': new_col1,
            'Col2': new_col2,
            'Col3': new_col3
        })

# 步骤 D: 将所有行 (原始行和新行) 转换为新的 DataFrame
result_df = pd.DataFrame(new_rows_list)

# 步骤 E: 按照临时排序键排序，删除临时列，并重置索引
final_df = (
    result_df
    .sort_values(by='_temp_order')
    .drop(columns=['_temp_order'])
    .reset_index(drop=True)
)

final_df.to_csv(output_file, index=False, header=False)

print(f"成功将数据处理并保存到 {output_file}")