import re

def repl(m):
    return f"MPPT {int(m.group(1)):02d} STG {int(m.group(2)):02d}"

test_str1 = "INV08 - MPPT1_STR01"
test_str2 = "INV08 - MPPT12_STR02"

parts1 = test_str1.split(' - ')
formatted1 = re.sub(r'MPPT(\d+)_STR(\d+)', repl, parts1[1])
parts1[1] = f"{formatted1} A"
print(' - '.join(parts1))

parts2 = test_str2.split(' - ')
formatted2 = re.sub(r'MPPT(\d+)_STR(\d+)', repl, parts2[1])
parts2[1] = f"{formatted2} B"
print(' - '.join(parts2))
