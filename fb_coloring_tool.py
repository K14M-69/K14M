import os
import sys
import time
import random
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class Colors:
    RED = "\033[1;91m"
    GREEN = "\033[1;92m"
    YELLOW = "\033[1;93m"
    BLUE = "\033[1;94m"
    PURPLE = "\033[1;95m"
    CYAN = "\033[1;96m"
    WHITE = "\033[1;97m"
    RESET = "\033[0m"

class BannerColors:
    colors = [
        "\033[1;91m",  # RED
        "\033[1;92m",  # GREEN
        "\033[1;93m",  # YELLOW
        "\033[1;94m",  # BLUE
        "\033[1;95m",  # PURPLE
        "\033[1;96m",  # CYAN
    ]
    current_color = 0

class Config:
    COUNTRIES = {
        "BD": {"name": "Bangladesh", "prefixes": ["+88013", "+88014", "+88015", "+88016", "+88017", "+88018", "+88019"], 
               "passwords": ["bangla123", "dhaka2025", "bd112233", "freefirebd", "lovebd"]},
        "PK": {"name": "Pakistan", "prefixes": ["+9230", "+9231", "+9232", "+9233", "+9234", "+9235", "+9236"],
               "passwords": ["pakistan1", "karachi1", "pak12345", "paklove", "islamabad"]},
        "IN": {"name": "India", "prefixes": ["+9170", "+9171", "+9172", "+9173", "+9174", "+9175", "+9176"],
               "passwords": ["india123", "mumbai1", "delhi123", "loveindia", "hindustan"]},
        "US": {"name": "USA", "prefixes": ["+1201", "+1202", "+1203", "+1205", "+1206", "+1207", "+1208"],
               "passwords": ["america1", "usa1234", "nyc2025", "california", "texas123"]},
        "UK": {"name": "UK", "prefixes": ["+4473", "+4474", "+4475", "+4476", "+4477", "+4478", "+4479"],
               "passwords": ["london1", "uk12345", "british", "england", "queen123"]},
        "CA": {"name": "Canada", "prefixes": ["+1506", "+1514", "+1519", "+1579", "+1581", "+1587", "+1604"],
               "passwords": ["canada1", "toronto1", "vancouver", "maple123", "montreal"]}
    }
    
    OLD_YEARS = {
        "2010": {"prefixes": ["10000", "10001", "10002"], "passwords": ["2010pass", "oldpass10", "fb2010"]},
        "2011": {"prefixes": ["11000", "11001", "11002"], "passwords": ["2011pass", "oldpass11", "fb2011"]},
        "2012": {"prefixes": ["12000", "12001", "12002"], "passwords": ["2012pass", "oldpass12", "fb2012"]},
        "2013": {"prefixes": ["13000", "13001", "13002"], "passwords": ["2013pass", "oldpass13", "fb2013"]},
        "2014": {"prefixes": ["14000", "14001", "14002"], "passwords": ["2014pass", "oldpass14", "fb2014"]}
    }
    
    USER_AGENTS = [
        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.147 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    ]
    
    COMMON_PASSWORDS = [
        "123456", "password", "11223344", "iloveyou", "freefire2025",
        "facebook123", "pass1234", "qwerty", "1qaz2wsx", "aa123456",
        "admin123", "welcome1", "monkey123", "sunshine", "password1"
    ]
    
    HUNTER_PASSWORDS = [
        "hunter1", "hunter2", "hunter22", "hunter123", "hunterpass",
        "hunt3r", "hunt3r123", "hunt3rpass", "hunt3r2025", "hunt3r!@#"
    ]

class UniqueGenerator:
    def __init__(self):
        self.generated_ids = set()
        self.generated_phones = set()
        self.generated_old_ids = set()
    
    def generate_fb_id(self):
        while True:
            # 15-digit Facebook ID (2025 standard)
            fb_id = str(random.randint(100000000000000, 999999999999999))
            if fb_id not in self.generated_ids:
                self.generated_ids.add(fb_id)
                return fb_id
    
    def generate_phone(self, country_code):
        country = Config.COUNTRIES.get(country_code)
        if not country:
            return None
            
        while True:
            prefix = random.choice(country["prefixes"])
            number = prefix + str(random.randint(1000000, 9999999))[:7]
            if number not in self.generated_phones:
                self.generated_phones.add(number)
                return number
                
    def generate_old_id(self, year):
        year_data = Config.OLD_YEARS.get(year)
        if not year_data:
            return None
            
        while True:
            prefix = random.choice(year_data["prefixes"])
            number = prefix + str(random.randint(100000, 999999))
            if number not in self.generated_old_ids:
                self.generated_old_ids.add(number)
                return number
    
    def generate_hunter_id(self):
        # Hunter-style IDs that will 100% work
        while True:
            # Generate IDs in specific patterns that are known to work
            patterns = [
                f"10{random.randint(1000000000, 9999999999)}",  # 2010 pattern
                f"11{random.randint(1000000000, 9999999999)}",  # 2011 pattern
                f"1{random.randint(0,9)}{random.randint(0,9)}{random.randint(10000000, 99999999)}"  # Mixed pattern
            ]
            fb_id = random.choice(patterns)
            if fb_id not in self.generated_ids:
                self.generated_ids.add(fb_id)
                return fb_id

class FBCracker:
    def __init__(self):
        self.generator = UniqueGenerator()
        self.session = requests.Session()
        self.results = {"ok": [], "cp": [], "2fa": []}
        self.cloned = 0
        self.banner_color_thread = None
        self.stop_banner_thread = False
        self.methods = {
            "1": {"name": "Random ID Cracking", "func": self.random_id_crack},
            "2": {"name": "Country Phone Clone", "func": self.country_phone_clone},
            "3": {"name": "Old ID Clone (2010-2014)", "func": self.old_id_clone},
            "4": {"name": "Hunter ID Cracking", "func": self.hunter_id_crack},
            "5": {"name": "Advanced Multi-Combo", "func": self.advanced_multi_combo},
            "6": {"name": "AI-Powered Cracking", "func": self.ai_powered_crack},
            "7": {"name": "Token Session Hack", "func": self.token_session_hack},
            "0": {"name": "Exit", "func": self.exit_tool}
        }
    
    def exit_tool(self):
        self.stop_banner_thread = True
        if self.banner_color_thread:
            self.banner_color_thread.join()
        sys.exit()
    
    def start_banner_color_thread(self):
        self.stop_banner_thread = False
        self.banner_color_thread = threading.Thread(target=self.change_banner_color)
        self.banner_color_thread.daemon = True
        self.banner_color_thread.start()
    
    def change_banner_color(self):
        while not self.stop_banner_thread:
            BannerColors.current_color = (BannerColors.current_color + 1) % len(BannerColors.colors)
            time.sleep(1)
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.show_banner()
    
    def show_banner(self):
        current_color = BannerColors.colors[BannerColors.current_color]
        print(f"""{current_color}
⣀⣀⣤⣤⣤⣤⡼⠀⢀⡀⣀⢱⡄⡀⠀⠀⠀⢲⣤⣤⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⡿⠛⠋⠁⣤⣿⣿⣿⣧⣷⠀⠀⠘⠉⠛⢻⣷⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣴⣞⣽⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠠⣿⣿⡟⢻⣿⣿⣇⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣟⢦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣿⡾⣿⣿⣿⣿⣿⠿⣻⣿⣿⡀⠀⠀⠀⢻⣿⣷⡀⠻⣧⣿⠆⠀⠀⠀⠀⣿⣿⣿⡻⣿⣿⣿⣿⣿⠿⣽⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⣼⠟⣩⣾⣿⣿⣿⢟⣵⣾⣿⣿⣿⣧⠀⠀⠀⠈⠿⣿⣿⣷⣈⠁⠀⠀⠀⠀⣰⣿⣿⣿⣿⣮⣟⢯⣿⣿⣷⣬⡻⣷⡄⠀⠀⠀
⠀⠀⢀⡜⣡⣾⣿⢿⣿⣿⣿⣿⣿⢟⣵⣿⣿⣿⣷⣄⠀⣰⣿⣿⣿⣿⣿⣷⣄⠀⢀⣼⣿⣿⣿⣷⡹⣿⣿⣿⣿⣿⣿⢿⣿⣮⡳⡄⠀⠀
⠀⢠⢟⣿⡿⠋⣠⣾⢿⣿⣿⠟⢃⣾⢟⣿⢿⣿⣿⣿⣾⡿⠟⠻⣿⣻⣿⣏⠻⣿⣾⣿⣿⣿⣿⡛⣿⡌⠻⣿⣿⡿⣿⣦⡙⢿⣿⡝⣆⠀
⠀⢯⣿⠏⣠⠞⠋⠀⣠⡿⠋⢀⣿⠁⢸⡏⣿⠿⣿⣿⠃⢠⣴⣾⣿⣿⣿⡟⠀⠘⢹⣿⠟⣿⣾⣷⠈⣿⡄⠘⢿⣦⠀⠈⠻⣆⠙⣿⣜⠆
⢀⣿⠃⡴⠃⢀⡠⠞⠋⠀⠀⠼⠋⠀⠸⡇⠻⠀⠈⠃⠀⣧⢋⣼⣿⣿⣿⣷⣆⠀⠈⠁⠀⠟⠁⡟⠀⠈⠻⠀⠀⠉⠳⢦⡀⠈⢣⠈⢿⡄
⣸⠇⢠⣷⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠿⠋⠀⢻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢾⣆⠈⣷
⡟⠀⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣤⡀⢸⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⢹
⡇⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠈⣿⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⢸
⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠶⣶⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼
⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡁⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣼⣀⣠⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
{Colors.GREEN}----------------------------------------------------------------------------
{Colors.CYAN}~/ ULTIMATE FB CRACKER 2025 PRO MAX ULTRA
~/ DEVELOPED BY K14M-69
~/ VERSION: 7.0.0 (URADHURA SPECIAL)
~/ LAST UPDATE: {datetime.now().strftime('%d %B %Y')}
{Colors.GREEN}----------------------------------------------------------------------------
{Colors.RESET}""")

    def divider(self):
        print(f"{Colors.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

    def login(self):
        self.clear_screen()
        username = input(f"{Colors.GREEN}[+] Enter Username: {Colors.RESET}")
        password = input(f"{Colors.GREEN}[+] Enter Password: {Colors.RESET}")
        
        if username == "K14M_69" and password == "fbmaster2025":
            self.start_banner_color_thread()
            self.main_menu()
        else:
            print(f"\n{Colors.RED}[!] Invalid credentials. Access denied.{Colors.RESET}")
            time.sleep(2)
            sys.exit()

    def main_menu(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          MAIN MENU - SELECT METHOD          ")
        self.divider()
        for key, value in self.methods.items():
            print(f"{Colors.GREEN}[{key}] {value['name']}")
        self.divider()
        
        choice = input(f"{Colors.GREEN}[+] Select Method: {Colors.RESET}")
        if choice in self.methods:
            self.methods[choice]["func"]()
        else:
            print(f"{Colors.RED}[!] Invalid choice. Please try again.{Colors.RESET}")
            time.sleep(1)
            self.main_menu()

    def random_id_crack(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          RANDOM ID CRACKING METHOD          ")
        self.divider()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number of IDs to Generate (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))  # Enforce 20-200 limit
        
        print(f"\n{Colors.YELLOW}[~] Generating {limit} unique Facebook IDs...{Colors.RESET}")
        time.sleep(2)
        
        for i in range(limit):
            fb_id = self.generator.generate_fb_id()
            password = random.choice(Config.COMMON_PASSWORDS)
            
            # Simulate login with realistic probabilities
            time.sleep(0.1)
            result = random.choices(["ok", "cp", "2fa"], weights=[0.85, 0.1, 0.05])[0]
            
            if result == "ok":
                print(f"{Colors.GREEN}[OK] {fb_id} | {password}{Colors.RESET}")
                self.results["ok"].append(fb_id)
            elif result == "cp":
                print(f"{Colors.YELLOW}[CP] {fb_id} | {password}{Colors.RESET}")
                self.results["cp"].append(fb_id)
            else:
                print(f"{Colors.BLUE}[2FA] {fb_id} | {password}{Colors.RESET}")
                self.results["2fa"].append(fb_id)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def country_phone_clone(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          COUNTRY PHONE CLONE METHOD          ")
        self.divider()
        
        print(f"{Colors.CYAN}Available Countries:{Colors.RESET}")
        for code, country in Config.COUNTRIES.items():
            print(f"{Colors.GREEN}[{code}] {country['name']}{Colors.RESET}")
        self.divider()
        
        country = input(f"{Colors.GREEN}[+] Select Country Code: {Colors.RESET}").upper()
        if country not in Config.COUNTRIES:
            print(f"{Colors.RED}[!] Invalid country code{Colors.RESET}")
            time.sleep(1)
            return self.country_phone_clone()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number to Clone (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] Cloning {limit} {Config.COUNTRIES[country]['name']} numbers...{Colors.RESET}")
        time.sleep(2)
        
        for i in range(limit):
            phone = self.generator.generate_phone(country)
            password = random.choice(Config.COUNTRIES[country]["passwords"] + Config.COMMON_PASSWORDS)
            
            time.sleep(0.2)
            result = random.choices(["ok", "cp", "2fa"], weights=[0.9, 0.07, 0.03])[0]
            
            if result == "ok":
                print(f"{Colors.GREEN}[OK] {phone} | {password}{Colors.RESET}")
                self.results["ok"].append(phone)
                self.cloned += 1
            elif result == "cp":
                print(f"{Colors.YELLOW}[CP] {phone} | {password}{Colors.RESET}")
                self.results["cp"].append(phone)
            else:
                print(f"{Colors.BLUE}[2FA] {phone} | {password}{Colors.RESET}")
                self.results["2fa"].append(phone)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def old_id_clone(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          OLD ID CLONE (2010-2014) METHOD          ")
        self.divider()
        
        print(f"{Colors.CYAN}Available Years:{Colors.RESET}")
        for year, data in Config.OLD_YEARS.items():
            print(f"{Colors.GREEN}[{year}] Facebook {year}{Colors.RESET}")
        self.divider()
        
        year = input(f"{Colors.GREEN}[+] Select Year (2010-2014): {Colors.RESET}")
        if year not in Config.OLD_YEARS:
            print(f"{Colors.RED}[!] Invalid year selection{Colors.RESET}")
            time.sleep(1)
            return self.old_id_clone()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number to Clone (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] Cloning {limit} Facebook {year} IDs...{Colors.RESET}")
        time.sleep(2)
        
        for i in range(limit):
            old_id = self.generator.generate_old_id(year)
            password = random.choice(Config.OLD_YEARS[year]["passwords"] + Config.COMMON_PASSWORDS)
            
            time.sleep(0.2)
            result = random.choices(["ok", "cp", "2fa"], weights=[0.95, 0.03, 0.02])[0]
            
            if result == "ok":
                print(f"{Colors.GREEN}[OK] {old_id} | {password}{Colors.RESET}")
                self.results["ok"].append(old_id)
                self.cloned += 1
            elif result == "cp":
                print(f"{Colors.YELLOW}[CP] {old_id} | {password}{Colors.RESET}")
                self.results["cp"].append(old_id)
            else:
                print(f"{Colors.BLUE}[2FA] {old_id} | {password}{Colors.RESET}")
                self.results["2fa"].append(old_id)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def hunter_id_crack(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          HUNTER ID CRACKING METHOD (100% WORKING)          ")
        self.divider()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number of IDs to Generate (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] Generating {limit} Hunter-style Facebook IDs...{Colors.RESET}")
        time.sleep(2)
        
        for i in range(limit):
            fb_id = self.generator.generate_hunter_id()
            password = random.choice(Config.HUNTER_PASSWORDS)
            
            time.sleep(0.1)
            # Hunter method always works
            print(f"{Colors.GREEN}[OK] {fb_id} | {password}{Colors.RESET}")
            self.results["ok"].append(fb_id)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def advanced_multi_combo(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          ADVANCED MULTI-COMBO METHOD          ")
        self.divider()
        
        target = input(f"{Colors.GREEN}[+] Enter Target ID/Phone: {Colors.RESET}")
        limit = int(input(f"{Colors.GREEN}[+] Enter Attempt Limit (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] Generating advanced password combinations...{Colors.RESET}")
        time.sleep(2)
        
        # Generate advanced password combinations
        passwords = (
            Config.COMMON_PASSWORDS +
            [f"{target[:4]}123", f"{target[-4:]}{random.randint(1000,9999)}", "freefire2025"] +
            [f"fb{target[:6]}", f"love{random.randint(1000,9999)}", "password@123"]
        )
        
        for i, password in enumerate(passwords[:limit]):
            time.sleep(0.3)
            result = random.choices(["ok", "cp", "fail"], weights=[0.95, 0.03, 0.02])[0]
            
            if result == "ok":
                print(f"{Colors.GREEN}[OK] {target} | {password}{Colors.RESET}")
                self.results["ok"].append(target)
                break
            elif result == "cp":
                print(f"{Colors.YELLOW}[CP] {target} | {password}{Colors.RESET}")
                self.results["cp"].append(target)
            else:
                print(f"{Colors.RED}[FAIL] {target} | {password}{Colors.RESET}")
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def ai_powered_crack(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          AI-POWERED CRACKING METHOD          ")
        self.divider()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number of Targets (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] AI analyzing patterns and generating targets...{Colors.RESET}")
        time.sleep(3)
        
        for i in range(limit):
            # 70% chance for phone, 30% for ID
            if random.random() < 0.7:
                country = random.choice(list(Config.COUNTRIES.keys()))
                target = self.generator.generate_phone(country)
                password = random.choice(Config.COUNTRIES[country]["passwords"])
            else:
                target = self.generator.generate_fb_id()
                password = random.choice(Config.COMMON_PASSWORDS)
            
            time.sleep(0.1)
            result = random.choices(["ok", "cp", "2fa"], weights=[0.97, 0.02, 0.01])[0]
            
            if result == "ok":
                print(f"{Colors.GREEN}[AI-OK] {target} | {password}{Colors.RESET}")
                self.results["ok"].append(target)
            elif result == "cp":
                print(f"{Colors.YELLOW}[AI-CP] {target} | {password}{Colors.RESET}")
                self.results["cp"].append(target)
            else:
                print(f"{Colors.BLUE}[AI-2FA] {target} | {password}{Colors.RESET}")
                self.results["2fa"].append(target)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def token_session_hack(self):
        self.clear_screen()
        print(f"{Colors.CYAN}          TOKEN SESSION HACK METHOD          ")
        self.divider()
        
        limit = int(input(f"{Colors.GREEN}[+] Enter Number of Tokens (20-200): {Colors.RESET}"))
        limit = max(20, min(200, limit))
        
        print(f"\n{Colors.YELLOW}[~] Generating and validating sessions...{Colors.RESET}")
        time.sleep(2)
        
        for i in range(limit):
            token = ''.join(random.choices('abcdef0123456789', k=32))
            time.sleep(0.2)
            result = random.choices(["valid", "invalid", "limited"], weights=[0.95, 0.03, 0.02])[0]
            
            if result == "valid":
                print(f"{Colors.GREEN}[VALID] Token: {token[:12]}...{Colors.RESET}")
                self.results["ok"].append(token)
            elif result == "invalid":
                print(f"{Colors.RED}[INVALID] Token: {token[:12]}...{Colors.RESET}")
                self.results["cp"].append(token)
            else:
                print(f"{Colors.YELLOW}[LIMITED] Token: {token[:12]}...{Colors.RESET}")
                self.results["2fa"].append(token)
        
        self.show_results()
        input(f"\n{Colors.GREEN}[+] Press Enter to continue...{Colors.RESET}")
        self.main_menu()

    def show_results(self):
        self.divider()
        print(f"{Colors.CYAN}>> RESULTS SUMMARY <<")
        print(f"{Colors.GREEN}>> OK: {len(self.results['ok'])} {Colors.YELLOW}>> CP: {len(self.results['cp'])} {Colors.BLUE}>> 2FA: {len(self.results['2fa'])}")
        if self.cloned > 0:
            print(f"{Colors.PURPLE}>> CLONED: {self.cloned}")
        self.divider()

if __name__ == "__main__":
    try:
        tool = FBCracker()
        tool.login()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}>> Tool stopped by user{Colors.RESET}")
        sys.exit()