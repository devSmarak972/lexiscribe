import os, re

cases = ["0a4ab450_0b9f_429d_9693_956c370985d5", "0a49e62c_d808_4d8d_8118_98b73ee18845", "e6e988fe_7cd5_4959_b838_81b3527c184b", "e3a91f85_455f_4866_92cf_b3cbbf580fbf", "01e32f3a_e197_4a19_951c_1370a6434d4a", "2c0bdd9d_e2e7_4da4_a86a_35a5d739ce3a", "0f0ae707_883a_4234_b87c_022cf59ddf27", "1f7dbbd2_b964_4acd_8209_1c63aef1fae5", "3f729b61_8ca7_4376_a562_e5d6319b72c7", "3f4e14c5_ad5d_434a_b84e_c53223d19304", \
        "2dec21cd_70df_418b_8174_2aa8b6f5d3aa", "d1016d0f_4a8a_4a44_bdbd_192f29e63e2e", "d497d9c2_dcff_4d54_be60_2a4689ffaa2a", "cb7abcf9_f74f_442c_a62c_1d0c1e361d6b", "ca3d0e1a_499d_4f69_a47b_f18f0028a873", "c65653f7_35ae_4a05_88a5_4d93f20bc7b7"]

log_file = "../test_logs/average_num_chars.txt"

whitelist_regex = [r"^[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]$", r"^[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]\.$", r'^IPC\.', r'^FIR\.']

def check_upper_lower(line):
    non_space_line = line.replace(" ", "")

    # count number of uppercase characters, lowercase characters, digits and special characters
    num_upper = sum(1 for char in non_space_line if char.isupper())
    num_lower = sum(1 for char in non_space_line if char.islower())
    num_digits = sum(1 for char in non_space_line if char.isdigit())
    num_special = len(non_space_line) - num_upper - num_lower - num_digits

    is_whitelisted = False

    # if upper+special > lower+digit, ignore the line from cleaned judgement
    if (num_upper + num_special) > (num_lower + num_digits):
        # print(f"{non_space_line} # {num_upper} + {num_special} > {num_lower} + {num_digits}")

        for regex in whitelist_regex:
            if re.search(regex, non_space_line):
                is_whitelisted = True
                break
    elif num_lower == 0:
        # print(f"{non_space_line} # {num_lower} == 0, {num_upper}, {num_special}, {num_digits}")
        for regex in whitelist_regex:
            if re.search(regex, non_space_line):
                # print(f"Whitelisted: {non_space_line} for regex {regex}")
                is_whitelisted = True
                break
    else:
        is_whitelisted = True

    return is_whitelisted

def clean_by_average(judg):
    lines = judg.split('\n')
    cleaned_lines = []
    avg = 0
    num_lines = 0
    for line in lines:
        # skip empty lines
        if len(line.strip()) == 0:
            continue

        avg += len(line.replace(" ", ""))
        num_lines += 1

    avg = avg / num_lines
    avg = int(avg)

    print(avg, file=open(log_file, "w", encoding="utf-8"))

    isPrevIncluded = False

    temp_lines = []

    for line in lines:
        # skip empty lines
        if len(line.strip()) == 0:
            continue

        # if line is too short
        if len(line.replace(' ', '')) < avg:
            if isPrevIncluded:
                cleaned_lines.append(line)
                isPrevIncluded = False
            else:
                if check_upper_lower(line):
                    temp_lines.append(line)
        else:
            if len(temp_lines) > 0:
                for l in temp_lines:
                    cleaned_lines.append(l)
                temp_lines = []

            cleaned_lines.append(line)
            isPrevIncluded = True

    for line in lines:
        if line not in cleaned_lines:
            print(line, file=open(log_file, "a", encoding="utf-8"))

    cleaned_judg = "\n".join(cleaned_lines)
    return cleaned_judg

def clean_judgment(judg, clean_by_avg = False):
    if clean_by_avg:
        judg = clean_by_average(judg)

    lines = judg.split('\n')

    cleaned_lines = []

    garbage_line_starters = ["Digitally Signed By", "Digitally signed by",  "Order Date:", "Order Date :", "Neutral Citation No.", "Court No.", "sd/-", "::: Downloaded on -", "Downloaded on -", "Downloaded on :", "Downloaded on", "vps "]
    garbage_line_enders = [".odt", ".ODT", ".DOC", ".doc", ".pdf", ".PDF", ".rtf", ".RTF", ".txt", ".TXT", ".docx", ".DOCX", ".html", ".HTML", ".htm", ".HTM", ".xml", ".XML", "& batch", "| Page", "| page", "| P a g e", "| p a g e"]
    garbage_end_regex = [r'& batch : \d+ :$']


    for i, line in enumerate(lines):
        # Remove lines starting with "Counsel for Someone:"
        # if re.match(r"^Counsel for [A-Za-z .]+:", line):
        #     continue

        is_garbage = False
        # if there is only one unique character in the line, ignore the line from cleaned judgement
        if len(set(line)) == 1:
            is_garbage = True
        
        for starter in garbage_line_starters:
            if line.strip().startswith(starter):
                is_garbage = True
                break
        
        for ender in garbage_line_enders:
            if line.strip().endswith(ender):
                is_garbage = True
                break

        for regex in garbage_end_regex:
            if re.search(regex, line.strip()):
                is_garbage = True
                break

        if line.strip().lower() == "with" or line.strip().lower() == "in":
            is_garbage = True

        if is_garbage:
            print(f"Garbage: {line}")
            continue

        # If line starts with tabs or more than 1 space, ignore the line from cleaned judgement
        if line.startswith("  ") or line.startswith(". ") or line.startswith("\t"):
            print(f"Tabbed: {line}")
            continue

        # If line contains the phrase "Page {\d}+ of {\d}+", line = line after the phrase
        if re.search(r"Page \d+ of \d+", line):
            line = re.split(r"Page \d+ of \d+", line)[1]
        
        if re.search(r"page \d+ of \d+", line):
            line = re.split(r"page \d+ of \d+", line)[1]
        
        if re.search(r'^W\.P\.[\(\)a-zA-Z ]+No.[0-9]+ of [0-9]+$', line):
            line = None

        # if line is empty, ignore the line from cleaned judgement
        if not line:
            continue

        # # count number of uppercase characters, lowercase characters, digits and special characters
        # num_upper = sum(1 for char in line if char.isupper())
        # num_lower = sum(1 for char in line if char.islower())
        # num_digits = sum(1 for char in line if char.isdigit())
        # num_special = len(line) - num_upper - num_lower - num_digits

        # # if upper+special > lower+digit, ignore the line from cleaned judgement
        # if (num_upper + num_special) > (num_lower + num_digits) or num_lower == 0:
        #     print(f"{line}")
        #     continue
        # else:
        #     cleaned_lines.append(line)

        if check_upper_lower(line):
            cleaned_lines.append(line)
        else:
            print(f"{line} rejected")

    cleaned_judg = "\n".join(cleaned_lines)

    return cleaned_judg

results_path = "../result_tests"
order_file_name = "full_judgment.txt"
cleaned_file_name = "cleaned_full_judgment.txt"
avg_cleaned_file_name = "avg_cleaned_full_judgment_new.txt"


for subdir in os.listdir(results_path):
    if subdir != cases[-1]:
        continue

    print(f"Processing {subdir}...")

    subdir_path = results_path + "/" + subdir

    order_path = subdir_path + "/" + order_file_name

    if not os.path.exists(order_path):
        continue

    with open(order_path, 'r', encoding='utf-8') as order_file:
        order = order_file.read()

    # cleaned_judg = clean_judgment(order)
    average_cleaned_judg = clean_judgment(order, clean_by_avg = True)

    # cleaned_order_path = subdir_path + "/" + cleaned_file_name
    avg_cleaned_order_path = subdir_path + "/" + avg_cleaned_file_name

    # with open(cleaned_order_path, 'w', encoding='utf-8') as result_file:
    #     result_file.write(cleaned_judg)

    with open(avg_cleaned_order_path, 'w', encoding='utf-8') as result_file:
        result_file.write(average_cleaned_judg)

