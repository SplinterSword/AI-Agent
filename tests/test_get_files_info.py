import sys
import os   
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.get_files_info import get_files_info

print(get_files_info("calculator", "."))
print("========================================")
print(get_files_info("calculator", "pkg"))
print("========================================")
print(get_files_info("calculator", "/bin"))
print("========================================")
print(get_files_info("calculator", "../"))
print("========================================")