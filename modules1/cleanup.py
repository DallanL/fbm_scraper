import re

def mobo_simplified (full_name):
    # Define regex patterns to extract chipsets and form factors
    chipset_pattern = r'((A|B|X|Z|H|P|Q)\d,3{2}m?)'  # Example: B450, X570, Z390
    form_factor_pattern = r'(Extended\s?ATX|E-?ATX|Micro\s?ATX|mATX|uATX|μATX|Mini\s?ITX|ITX|ATX)'  # Example: ATX, Micro ATX, Mini ITX

    # Standardize form factors
    form_factor_map = {
        'Extended ATX': 'EATX',
        'EATX': 'EATX',
        'E-ATX': 'EATX',
        'Micro ATX': 'mATX',
        'mATX': 'mATX',
        'uATX': 'mATX',
        'μATX': 'mATX',
        'Mini ITX': 'ITX',
        'ITX': 'ITX',
        'ATX': 'ATX'
    }

    chipset_match = re.search(chipset_pattern, full_name, re.IGNORECASE)
    if chipset_match:
        chipset = chipset_match.group(1)
        # Check if the chipset ends with 'm' and remove it if present
        if chipset.endswith('m'):
            chipset = chipset[:-1]
            form_factor = 'mATX'
        else:
            form_factor_match = re.search(form_factor_pattern, full_name, re.IGNORECASE)
            if form_factor_match:
                form_factor_raw = form_factor_match.group(1)
                form_factor = form_factor_map.get(form_factor_raw, 'Unknown')
            else:
                form_factor = 'Unknown'
                simple_mobo = chipset
    else:
        chipset = 'Unknown'
        form_factor = 'Unknown'
        simple_mobo = 'Unknown Motherboard'

    return simple_mobo

def gpu_simplified(full_name, brand):   #set brand to "1" to include amd/nvidia/intel
    full_name = re.sub(r'[^A-Za-z0-9]+', ' ', full_name) #replace non-alphanumeric charaters with a single space
    full_name = re.sub(r'\s+', ' ', full_name).upper().strip() # Replace multiple spaces with a single space
    # Define regular expression patterns
    nvidia_pattern = re.compile(r'((?P<series>^|RTX\s?|GTX\s?|\s)(?P<model>([1-4]0[5-9]0)|16[(356]0|(9[7-8]0))\s?(?P<suffix>TI SUPER|TI|SUPER|S|\s|$))', re.IGNORECASE)
    titan_pattern = re.compile(r'((?P<titan>TITAN RTX|TITAN V\b|TITAN X PASCAL|TITAN XP)|(?P<geforce>TITAN X|TITAN BLACK| TITAN Z|TITAN\b))', re.IGNORECASE) #find the nvidia titan cards
    quadro_pattern = re.compile(r'(?P<model>(QUADRO)?\s?(RTX\sA?[1-8]000|P2200)\s?(SFF ADA|ADA)?)', re.IGNORECASE)
    old_nvidia_pattern = re.compile(r'GT\s?\d{3,4}|\s?\d{3,4}\s?GT|GEFORCE\s?\d{3,4}|GTX\s?\d{3,4}', re.IGNORECASE) #catch the old nvidia GPUs
    old_amd_pattern = re.compile(r'R(3|5|7|9)\s\d{3}|HD\s?\d{4}', re.IGNORECASE) #catch the old amd GPUs
    amd_pattern = re.compile(r'((^|RADEON\s?RX|RADEON\s?|RX\s?|\s)(?P<model>(([5-7][5-9][05]0)|([45][5-9]0)|VII|VEGA 64|VEGA 56))\s?(?P<suffix>XTX|XT|GRE)?)', re.IGNORECASE)
    amd_pro_pattern = re.compile(r'(?P<model>FIREPRO [DMRSW]\d{3,4}|RADEON PRO WX?\s?\d{4})', re.IGNORECASE)
    intel_pattern = re.compile(r'((INTEL)?\s?(ARC)?\s?(?P<model>A\d{3}))', re.IGNORECASE)
    generic_pattern = re.compile(r'graphics? card|gpu|rtx|video card|geforce|gtx|gaming card', re.IGNORECASE) #terms to ID a gpu of some kind with a really bad titles
    legacy_nvidia_pattern = re.compile(r'GEFORCE|\sGT\s|NVIDIA', re.IGNORECASE)
    tesla_pattern = re.compile(r'TESLA', re.IGNORECASE)

    titan_match = titan_pattern.search(full_name)
    old_nvidia_match = old_nvidia_pattern.search(full_name)
    old_amd_match = old_amd_pattern.search(full_name)
    nvidia_match = nvidia_pattern.search(full_name)
    amd_match = amd_pattern.search(full_name)
    amd_pro_match = amd_pro_pattern.search(full_name)
    intel_match = intel_pattern.search(full_name)
    legacy_nvidia_match = legacy_nvidia_pattern.search(full_name) #to make sure amd cards aren't actually old nvidia like 6800 GT
    quadro_match = quadro_pattern.search(full_name)
    tesla_match = tesla_pattern.search(full_name)
    generic_match = generic_pattern.search(full_name) #to find the worst GPU titles
    if nvidia_match:
        model_number = nvidia_match.group('model') or ''
        suffix = nvidia_match.group('suffix') or ''
        
        # Determine series based on model number
        if re.match(r'[2-4]0[5-9]0', model_number):
            series = "RTX"
        else:
            series = "GTX"

        if brand == "1":
            simple_gpu = f"NVIDIA {series} {model_number} {suffix}".strip()
        else:
            simple_gpu = f"{series} {model_number} {suffix}".strip()
        return simple_gpu
    elif titan_match and generic_match:
        if titan_match.group('titan'):

            simple_gpu = titan_match.group('titan')
        else:
            model = titan_match.group('geforce')
            simple_gpu = f"GTX {model}".strip()

        if brand == "1":
            simple_gpu = f"NVIDIA {simple_gpu}".strip()
        else:
            simple_gpu = simple_gpu.strip()
        return simple_gpu
    elif amd_match and not legacy_nvidia_match:
        model_number = amd_match.group('model') or ''
        suffix = amd_match.group('suffix') or ''
        if model_number == "VII":
            series = "RADEON"
        else:
            series = "RX"

        if brand == "1":
            simple_gpu = f"AMD {series} {model_number} {suffix}".strip()
        else:
            simple_gpu = f"{series} {model_number} {suffix}".strip()
        return simple_gpu
    elif quadro_match:
        model = quadro_match.group('model')
        if brand == "1":
            simple_gpu = f"NVIDIA {model}".strip()
        else:
            simple_gpu = f"{model}".strip()
        return simple_gpu
    elif amd_pro_match:
        model = amd_pro_match.group('model')
        if brand == "1":
            simple_gpu = f"AMD {model}".strip()
        else:
            simple_gpu = f"{model}".strip()
        return simple_gpu

    elif intel_match:
        series = "ARC"
        model_number = intel_match.group('model') or ''
        
        if brand == "1":
            simple_gpu = f"INTEL {series} {model_number}".strip()
        else:
            simple_gpu = f"{series} {model_number}".strip()
        return simple_gpu
    elif old_nvidia_match or old_amd_match:
        simple_gpu = "old"
        return simple_gpu
    elif tesla_match:
        simple_gpu = "tesla"
        return simple_gpu
    elif generic_match:
        simple_gpu = "generic"
        return simple_gpu
    else:
        #print(f'item: {full_name} could not be matched to a pattern')
        return None  # Return None if the pattern does not match


def cpu_simplified (full_name):
    # Replace instances of "r\d" with "Ryzen \d"
    full_name = re.sub(r'\br(\d)', r'Ryzen \1', full_name, flags=re.IGNORECASE)

    cpu_pattern = re.compile(r'((?P<series>ryzen\s\d|i\d|xeon (e\d?|w\d?))-?(?P<model_number>\d{4,5})\s?(?P<suffix>x|t|l|p|k|f|s|v\d|\s)*)', re.IGNORECASE) #example ryzen 5 3600, intel i5-10600kf, xeon e5-2667v4
    cpu_match = cpu_pattern.search(full_name)

    if cpu_match:
        series = cpu_match.group(series).upper()
        model_number = cpu_match.group(model_number)
        suffix = cpu_match.group(suffix).upper() if cpu_match.group(suffix) else ""

        if "I" in series or "XEON" in series:
            manufacturer = "INTEL"
        elif "ryzen" in series:
            manufacturer = "AMD"
        else:
            manufacturer = "UNKNOWN" #are you using ARM or risc-v or something?!
        
        simple_cpu = f"{manufacturer} {series} {model_number}{suffix}".strip()
        
        return simple_cpu
    else:
        return None #return None if no pattern match
    
def ram_simplified (full_name):
    ram_pattern = re.compile(r'((?P<capacity>))', re.IGNORECASE) #example 
    ram_match = ram_pattern.search(full_name)

    if ram_match:
        capacity = ram_match.group(capacity).upper().strip()
        speed = ram_match.group(speed).strip()
        type = ram_match.group(type).upper()
        config = ram_match.group(config).upper().strip() if ram_match.group(config) else ""

        if ram_match.group(config):
            simple_ram = f"{capacity} {type} {speed} ({config})"
        else:
            simple_ram = f"{capacity} {type} {speed}".strip()
        
        return simple_ram
    else:
        return None #ram pattern not detected
    
def psu_simplified (full_name):
    psu_pattern = re.compile(r'(?P<wattage>\d{3,4}\s?w?)', re.IGNORECASE) #example "core reactor 750w"
    psu_match = psu_pattern.search(full_name)

    if psu_match:
        wattage = psu_match.group(wattage).upper().strip()

        simple_psu = wattage
        return simple_psu
    else:
        return None #no match on psu, probably a bomb
