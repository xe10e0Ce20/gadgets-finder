import re

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
        print(f"成功将数据处理并保存到 {output_filename}")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")



input_file = input("Input file name: ")
output_file = input_file.replace(".txt", ".csv")

process_and_convert_to_csv(input_file, output_file)