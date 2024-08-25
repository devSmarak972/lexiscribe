import re
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

    # print(avg, file=open(log_file, "w", encoding="utf-8"))

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

    # for line in lines:
    #     if line not in cleaned_lines:
    #         print(line, file=open(log_file, "a", encoding="utf-8"))

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