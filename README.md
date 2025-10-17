# gadgets-finder
## How to use:
- install pandas
- 2.Use _disas_to_csv to turn _disas.txt to csv
- 3.Run gadgets_finder to serach for gadgets
  - Supports regular expression
- Multi-Instruction Search: Input each instruction sequentially, then press Enter (with no input) to start the search. 
    - e.g.:
```
Input disas.csv name(default:_disas.csv):  
Max length(default:2): 10
Use regular expression?(y/n): y
Ignore B, BL, BC AL command?(y/n, default=n): 
Ignore BC command?(y/n, default=y):         
search for command(s): ^MOV  ER.{1,2}, ER.{1,2}$
search for command(s):

......

Result output in result.csvs
```