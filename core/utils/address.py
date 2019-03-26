"""
Functions to standardize address strings
in HPD contacts data
"""
import re

STREETS = [
    (r'(?<= )AVE(NUE)?$', 'AVENUE'),
    (r'(?<= )(STREET|STR|(ST\.?))', 'STREET'),
    (r'(?<= )PL(ACE)?$', 'PLACE'),  # plaza / place?
    (r'(?<= )(ROAD|(?<!\d)RD\.?)', 'ROAD'),
    (r'(?<= )(LA(NE)?|LN)', 'LANE'),
    (r'(?<= )CT|CRT', 'COURT'),
    (r'(?<= )DR(IVE)?$', 'DRIVE'),
    (r'(?<= )(BOULEVARD|BLVD)', 'BOULEVARD'),
    (r'(?<= )(PKWY|PARKWY)', 'PARKWAY'),
    (r'(?<= )PK$', 'PARK'),
    (r'(?<= )BCH$', 'BEACH'),
    (r'(?<= )TERR(ACE)?$', 'TERRACE'),
    (r'(^|(?<= ))(BDWAY|BDWY|BROAD WAY)', 'BROADWAY')
]


# Look for direction abbrivation as the start of the string or a space, but NOT 'AVENUE '
# this is to avoid lettered avenues such as "AVENUE W"
DIR_START = "(^|(?<=[ ]))(?<!AVENUE )"
DIR_END = "((?=[ ])|$)"


def dir_regex(x): return DIR_START + x + DIR_END


DIRECTIONS = [
    (dir_regex(r'N\.?'), 'NORTH'),
    (dir_regex(r'SO?\.?'), 'SOUTH'),
    (dir_regex(r'E\.?'), 'EAST'),
    (dir_regex(r'W\.?'), 'WEST')
]

ALIASES = [
    ('ADAM CLAYTON POWELL( JR)?( (BLVD|BOULEVARD))?', 'ADAM CLAYTON POWELL JR BOULEVARD'),
    ('AVENUE OF( THE)? AMERICAS', 'AVENUE OF THE AMERICAS'),
    (r'COLLEGE PT\.? (BLVD|BOULEVARD)', 'COLLEGE POINT BOULEVARD'),
    ('CO-OP CITY', 'COOP CITY')
]

REMOVE = [
    ('(BKLYN|BROOKLYN|QUEENS|BRONX|MANHATTAN|NEW YORK|NYC|SI)$', ''),
    ('(BENSONHURST|CORONA)$', ''),
    (r'\(.+\)$', '')
]

REGEX_REPLACEMENTS = STREETS + DIRECTIONS + REMOVE

# Str, Str -> Lambda


def number_to_text(number):
    if number == '1':
        suffix = 'ST'
    elif number == '2':
        suffix = 'ND'
    elif number == '3':
        suffix = 'RD'
    elif number == '11':
        suffix = 'TH'
    elif number == '12':
        suffix = 'TH'
    elif number == '13':
        suffix = 'TH'
    elif len(number) == 1:
        suffix = 'TH'
    elif len(number) >= 2 and number[-1:] == '1':
        suffix = 'ST'
    elif len(number) >= 2 and number[-1:] == '2':
        suffix = 'ND'
    elif len(number) >= 2 and number[-1:] == '3':
        suffix = 'RD'
    else:
        suffix = 'TH'

    return number + suffix


def replace_func(pattern, replacement):
    return lambda s: re.sub(pattern, replacement, s)


ALIASES_FUNCS = list(map(lambda x: replace_func(*x), ALIASES))
REGEX_FUNCS = list(map(lambda x: replace_func(*x), REGEX_REPLACEMENTS))

WORD_NUMBERS = ['0TH', '1ST', '2ND', '3RD',
                '4TH', '5TH', '6TH', '7TH',
                '8TH', '9TH', '10TH']
SUFFIXES = {
    '0': 'TH',
    '1': 'ST',
    '2': 'ND',
    '3': 'RD',
    '4': 'TH',
    '5': 'TH',
    '6': 'TH',
    '7': 'TH',
    '8': 'TH',
    '9': 'TH'
}


def format_number(matchobj):
    n = matchobj.group('number')
    rest = matchobj.group('rest')
    if int(n) < 11:
        return WORD_NUMBERS[int(n)] + rest
    else:
        tens_digit = str(n)[-2:-1]

        if tens_digit == '1':
            return str(n) + 'TH' + rest
        else:
            return n + SUFFIXES[n[-1]] + rest


def replace_number(string):
    return re.sub(r"(^|(?<=[ ]))(?P<number>\d+)(TH|ST|ND|RD)?(?P<rest>(\b|[ ]).*)", format_number, string)


HOLY_SAINTS = ['JOSEPH', 'MARKS', 'LAWRENCE', 'JAMES',
               'NICHOLAS', 'HOLLIS', 'JOHNS', "JOHN's"]

SAINTS_REGEX = r"ST\.?[ ](?P<street_name>({}))".format('|'.join(HOLY_SAINTS))


def saints(s):
    def repl(matchobj): return "SAINT " + matchobj.group('street_name')
    return re.sub(SAINTS_REGEX, repl, s)


STREET_FUNCS = ALIASES_FUNCS + [replace_number, saints] + REGEX_FUNCS

# list(of functions), str -> str


def func_chain(funcs, val):
    if len(funcs) == 0:
        return val
    else:
        return func_chain(funcs[1:], funcs[0](val))


def remove_extra_spaces(s):
    return ' '.join([x for x in s.split(' ') if x != ''])


def prepare(s):
    return remove_extra_spaces(s).strip().upper().replace('"', '').replace('-', '')


def normalize_street(street):
    if street is None:
        return None

    s = prepare(street)

    if s == '':
        return None

    return func_chain(STREET_FUNCS, s).replace('.', '').strip()


# remove dashes or spaces...sorry Queens!
def normalize_street_number(number):
    if number is None or number == '':
        return None
    return re.sub(r'(?<=\d)(-|[ ])(?=\d)', '', number).replace('-', '').strip()


APT_STRINGS_TO_REMOVE = ['.', '_', '#', '{', '}', '/']


def clean_apt_str(s):
    s = prepare(s)
    for char_to_remove in APT_STRINGS_TO_REMOVE:
        s = s.replace(char_to_remove, '')
    return s


APT_NUM = r'(?<=\d)(ST|TH|ND|RD)'
# "12F" becomes 12F
# "12TH F" becomes 12FLOOR
EDGE_CASE_FLOOR = APT_NUM + '[ ]F$'
FLOOR_REGEX = r'(?<=\d)[ ]?((FL(OOR|O|R)?)|FW)$'


def normalize_apartment(string):
    if string is None:
        return None

    s = clean_apt_str(string)

    if s == '':
        return None

    s = re.sub(EDGE_CASE_FLOOR, 'FLOOR', s)
    s = re.sub(APT_NUM, '', s)
    s = re.sub(FLOOR_REGEX, 'FLOOR', s)

    return s.replace(' ', '')


def clean_number_and_streets(string, include_house_number):
    # Beach
    string = string.upper()
    string = re.sub(r"\bBEAC H\b", 'BEACH', string)
    string = re.sub(r"\bBEA CH\b", 'BEACH', string)
    string = re.sub(r"\bBE ACH\b", 'BEACH', string)
    string = re.sub(r"\bB EACH\b", 'BEACH', string)

    # Street
    string = re.sub(r"\bSTREE T\b", 'STREET', string)
    string = re.sub(r"\bSTR EET\b", 'STREET', string)
    string = re.sub(r"\bST REET\b", 'STREET', string)
    string = re.sub(r"\bSTRE ET\b", 'STREET', string)
    string = re.sub(r"\bS TREET\b", 'STREET', string)
    string = re.sub(r'\bSTREE\b', 'STREET', string)

    # PLACE
    string = re.sub(r"\bPLAC E\b", 'PLACE', string)
    string = re.sub(r"\bPLA CE\b", 'PLACE', string)
    string = re.sub(r"\bPL ACE\b", 'PLACE', string)
    string = re.sub(r"\bP LACE\b", 'PLACE', string)

    # ROAD
    string = re.sub(r"\bROA D\b", 'ROAD', string)
    string = re.sub(r"\bRO AD\b", 'ROAD', string)
    string = re.sub(r"\bR OAD\b", 'ROAD', string)

    # AVENUE
    string = re.sub(r"\bAVENU E\b", 'AVENUE', string)
    string = re.sub(r"\bAVEN UE\b", 'AVENUE', string)
    string = re.sub(r"\bAVE NUE\b", 'AVENUE', string)
    string = re.sub(r"\bAV ENUE\b", 'AVENUE', string)
    string = re.sub(r"\bA VENUE\b", 'AVENUE', string)
    string = re.sub(r"\bAVNUE\b", 'AVENUE', string)
    string = re.sub(r"\bAVENU\b", 'AVENUE', string)
    string = re.sub(r"\bAVENE\b", 'AVENUE', string)
    string = re.sub(r"\bAVNEUE\b", 'AVENUE', string)

    # PARKWAY
    string = re.sub(r"\bP ARKWAY\b", 'PARKWAY', string)
    string = re.sub(r"\bPA RKWAY\b", 'PARKWAY', string)
    string = re.sub(r"\bPAR KWAY\b", 'PARKWAY', string)
    string = re.sub(r"\bPARK WAY\b", 'PARKWAY', string)
    string = re.sub(r"\bPARKWA Y\b", 'PARKWAY', string)
    string = re.sub(r"\bPARKWA\b", 'PARKWAY', string)
    string = re.sub(r"\bPARKWAYY\b", 'PARKWAY', string)
    string = re.sub(r'\bPKW Y\b', 'PARKWAY', string)

    # EXPRESSWAY
    string = re.sub(r'\bEXP RESSWAY\b', 'EXPRESSWAY', string)

    # HIGHWAY
    string = re.sub(r"\bHWY\b", 'HIGHWAY', string)
    # NORTH
    string = re.sub(r"\bN ORTH\b", 'NORTH', string)
    string = re.sub(r"\bNOR TH\b", 'NORTH', string)
    # SOUTH
    string = re.sub(r"\bSOUT H\b", 'SOUTH', string)
    string = re.sub(r"\bS OUTH\b", 'SOUTH', string)
    string = re.sub(r"\bSOU TH\b", 'SOUTH', string)
    # BOULEVARD
    string = re.sub(r"\bBOULEVAR D\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOULEVA RD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOULEV ARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOULE VARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOUL EVARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOU LEVARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bB OULEVARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOUELEVARD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBOULEV\b", 'BOULEVARD', string)

    # BLVD
    string = re.sub(r"\bBLVD\b", 'BOULEVARD', string)
    string = re.sub(r"\bBLV D\b", 'BOULEVARD', string)
    string = re.sub(r"\bBL VD\b", 'BOULEVARD', string)
    string = re.sub(r"\bB LVD\b", 'BOULEVARD', string)

    # TERRACE
    string = re.sub(r"\bTERRAC E\b", 'TERRACE', string)
    string = re.sub(r"\bTERRA CE\b", 'TERRACE', string)
    string = re.sub(r"\bTERR ACE\b", 'TERRACE', string)
    string = re.sub(r"\bTER RACE\b", 'TERRACE', string)
    string = re.sub(r"\bTE RRACE\b", 'TERRACE', string)
    string = re.sub(r"\bT ERRACE\b", 'TERRACE', string)

    # CONCOURSE

    string = re.sub(r'\bCONC OURSE\b', 'CONCOURSE', string)

    # remove double space
    string = string.upper().replace("  ", " ")
    string = string.upper().replace("   ", " ")
    string = string.upper().replace("    ", " ")
    string = string.upper().replace("     ", " ")

    # rmove +
    string = string.upper().replace("+", '')

    # remove all periods
    string = string.upper().replace('.', '')

    # remove space dash space
    string = string.upper().replace(' - ', ' ')

    # FOUND TYPOS
    string = re.sub(r"\bP OLITE\b", "POLITE", string)
    string = re.sub(r"\bDEREIMER\b", "DE REIMER", string)
    string = re.sub(r"\bBAYRIDGE\b", "BAY RIDGE", string)
    string = re.sub(r"\bAVESOUTH\b", "AVE SOUTH", string)
    string = re.sub(r"\bPARKHILL\b", "PARK HILL", string)
    string = re.sub(r"\bSTJOHNS\b", "SAINT JOHNS", string)
    string = re.sub(r"\bSTMARKS\b", "SAINT MARKS", string)
    string = re.sub(r"\bSTNICHOLAS\b", "SAINT NICHOLAS", string)
    string = re.sub(r"\bSTPAULS\b", "SAINT PAULS", string)
    string = re.sub(r"\bSTLAWRENCE\b", "SAINT LAWRENCE", string)
    string = re.sub(r"\bWILLIAMSBRID GE\b", "WILLIAMSBRIDGE", string)
    string = re.sub(r"\bATLANT IC\b", "ATLANTIC", string)
    string = re.sub(r"\bWTREMONT\b", "WEST TREMONT", string)
    string = re.sub(r"\bREVERAND\b", "REV", string)
    string = re.sub(r"\bPENNSYLVAN IA\b", "PENNSYLVANIA", string)
    string = re.sub(r"\bPENNSYLVANI A\b", "PENNSYLVANIA", string)
    string = re.sub(r"\bRID GE\b", "RIDGE", string)
    string = re.sub(r"\bHARDIN G\b", "HARDING", string)
    string = re.sub(r"\bCHESTNU T\b", "CHESTNU T", string)
    string = re.sub(r"\bFRANCIS LEWI S\b", "FRANCIS LEWIS", string)
    string = re.sub(r"\bWASHINGTO\b", "WASHINGTON", string)
    string = re.sub(r"\bPARK WE ST\b", "PARK WEST", string)
    string = re.sub(r"\bTHOMAS SBOYLAND\b", "THOMAS SOUTH BOYLAND", string)
    string = re.sub(r"\bPAEDERGAT\b", "PAERDEGAT", string)
    string = re.sub(r"\bVALENTI NE\b", "VALENTINE", string)
    string = re.sub(r"\bSOUTHE RN\b", "SOUTHERN", string)
    string = re.sub(r"\bKI NG\b", "KING", string)
    string = re.sub(r"\bFTWASHINGTON\b", "FORT WASHINGTON", string)
    string = re.sub(r"\bL OT\b", "LOT", string)
    string = re.sub(r"\bP ARK\b", "PARK", string)
    string = re.sub(r"\bAMSTERD AM\b", "AMSTERDAM", string)
    string = re.sub(r"\bSTR\b", "STREET", string)
    string = re.sub(r"\bSQUAR\b", "SQUARE", string)
    string = re.sub(r"\bEA ST\b", "EAST", string)
    string = re.sub(r"\bWE ST\b", "WEST", string)

    # Replace Street Appreviations
    HOLY_SAINTS = ['FELIX', 'ANDREWS', 'PAULS', 'JOSEPH', 'MARKS', 'LAWRENCE', 'JAMES',
                   'NICHOLAS', 'HOLLIS', 'JOHNS', "JOHN'S", "EDWARDS", "GEORGES", "GEORGE", "OUEN", "MARYS", "THERESA", "LUKES", "JUDE"]

    # replace ST MARKS etc with SAINT MARKS
    for saint in HOLY_SAINTS:
        string = re.sub(r"(?=.*ST {})(\bST {}\b)".format(saint, saint), "SAINT {}".format(saint), string)

    # Abbreviations
    string = re.sub(r"\bFT\b", "FORT", string)
    string = re.sub(r"\bRV\b", "RIVER", string)
    string = re.sub(r"\bCT\b", "COURT", string)
    string = re.sub(r"\bTER\b", "TERRACE", string)
    string = re.sub(r"\bLN\b", "LANE", string)
    string = re.sub(r"\bPL\b", "PLACE", string)
    string = re.sub(r"\bDR\b", "DRIVE", string)
    string = re.sub(r"\bRD\b", "ROAD", string)
    string = re.sub(r"\bAV\b", "AVENUE", string)
    string = re.sub(r"\bAVE\b", "AVENUE", string)
    string = re.sub(r"\bBLVD\b", "BOULEVARD", string)
    string = re.sub(r"\bBDWAY\b", "BROADWAY", string)
    string = re.sub(r"\bBDWY\b", "BROADWAY", string)
    string = re.sub(r"\bPKWY\b", "PARKWAY", string)
    string = re.sub(r"\bPKWAY\b", "PARKWAY", string)
    string = re.sub(r"\bEXPWY\b", "EXPRESSWAY", string)
    string = re.sub(r"\bEXP WY\b", "EXPRESSWAY", string)
    string = re.sub(r"\bEXPR ESSWAY\b", "EXPRESSWAY", string)
    string = re.sub(r"\bTPKE\b", "TURNPIKE", string)
    string = re.sub(r"\bNY\b", "NEW YORK", string)

    string = re.sub(r"(?!{})(?=\bST\b)(\bST\b)".format(
        ".*" + saint + "|" for saint in HOLY_SAINTS), "STREET", string)

    # Join MAC DOUGAL and others into MACDOUGAL

    string = re.sub(r"(\bMAC \b)", r"MAC", string)
    string = re.sub(r"(\bMC \b)", r"MC", string)

    # replace THIRD and similar with 3rd
    string = re.sub(r"\bFIRST\b", "1ST", string)
    string = re.sub(r"\bSECOND\b", "2ND", string)
    string = re.sub(r"\bTHIRD\b", "3RD", string)
    string = re.sub(r"\bFOURTH\b", "4TH", string)
    string = re.sub(r"\bFIFTH\b", "5TH", string)
    string = re.sub(r"\bSIXTH\b", "6TH", string)
    string = re.sub(r"\bSEVENTH\b", "7TH", string)
    string = re.sub(r"\bEIGHTH\b", "8TH", string)
    string = re.sub(r"\bNINTH\b", "9TH", string)
    string = re.sub(r"\bTENTH\b", "10TH", string)
    string = re.sub(r"\bELEVENTH\b", "11TH", string)
    string = re.sub(r"\bTWELTH\b", "12TH", string)

    # Replace Compass appreviations
    string = re.sub(r"\bN\b", "NORTH", string)
    string = re.sub(r"\bE\b", "EAST", string)
    string = re.sub(r"\bS\b", "SOUTH", string)
    string = re.sub(r"\bW\b", "WEST", string)

    if (include_house_number):
        # replace 143 street with 143rd st
        match = re.search(
            r"(?<!^)(?=\s\d+ (DRIVE|ROAD|PLACE|STREET|AVENUE))( \d+ (DRIVE|ROAD|PLACE|STREET|AVENUE))", string)
        if match:
            original = match.group().strip()
            number, rest = original.split(' ', 1)
            match = " ".join([number_to_text(number), rest])
            string = string.upper().replace(original, match)

        # Clean property addresses with weird typo - "1o" instead of "10"
        string = re.sub(r"\b1o\b", "10", string)
        string = re.sub(r"\b-1o\b", "-10", string)
        string = re.sub(r"\b2o\b", "20", string)
        string = re.sub(r"\b-2o\b", "-20", string)
        string = re.sub(r"\b3o\b", "30", string)
        string = re.sub(r"\b-3o\b", "-30", string)
        string = re.sub(r"\b4o\b", "40", string)
        string = re.sub(r"\b-4o\b", "-40", string)
        string = re.sub(r"\b5o\b", "50", string)
        string = re.sub(r"\b6o\b", "60", string)
        string = re.sub(r"\b7o\b", "70", string)
        string = re.sub(r"\b8o\b", "80", string)
        string = re.sub(r"\b9o\b", "90", string)

    else:
        match = re.search(r"(?=\d* (DRIVE|ROAD|PLACE|STREET|AVENUE))(\d+ (DRIVE|ROAD|PLACE|STREET|AVENUE))", string)
        if match:
            original = match.group().strip()
            number, rest = original.split(' ', 1)
            match = " ".join([number_to_text(number).lower(), rest])
            string = string.upper().replace(original, match)

    # remove dashes from street-names-with-dashes (but not 12-14 number dashes)
    string = re.sub(r"(?=[a-zA-Z]*\-[a-zA-Z])\-", " ", string)

    # final formatting - Title Case, except for numbered streets like 10th st (not 10Th st)
    string = string.title()
    street_suffix_pattern = r"\d+(S(T|t)|N(D|d)|R(D|d)|T(H|h))"
    match = re.search(street_suffix_pattern, string)

    if match:
        string = re.sub(street_suffix_pattern, match.group().lower(), string)

    return string
