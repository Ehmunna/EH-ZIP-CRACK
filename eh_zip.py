#!/usr/bin/env python3
import zipfile
import os
import sys
import itertools
from threading import Thread, Lock
from queue import Queue, Empty

# ── optional AES-256 support ──────────────────────────────────────────────────
try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False


class Colors:
    GREEN  = '\033[92m'
    CYAN   = '\033[96m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    WHITE  = '\033[97m'
    BOLD   = '\033[1m'
    END    = '\033[0m'


class EHZipSuite:
    def __init__(self):
        self.found    = False
        self.password = None
        self.lock     = Lock()
        self.attempts = 0

    # ──────────────────────────────────────────────
    # UI HELPERS
    # ──────────────────────────────────────────────

    def banner(self):
        import time, sys, os

        # ── clear terminal → new page feel ───────────
        os.system('cls' if os.name == 'nt' else 'clear')

        ascii_lines = [
            "    ███████╗██╗  ██╗    ███████╗██╗██████╗ ",
            "    ██╔════╝██║  ██║    ╚══███╔╝██║██╔══██╗",
            "    █████╗  ███████║      ███╔╝ ██║██████╔╝",
            "    ██╔══╝  ██╔══██║     ███╔╝  ██║██╔═══╝ ",
            "    ███████╗██║  ██║    ███████╗██║██║     ",
            "    ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝╚═╝     ",
        ]

        # ── separator flash ──────────────────────────
        sep = f"{Colors.GREEN}{Colors.BOLD}{'═'*50}{Colors.END}"
        print(sep)
        time.sleep(0.08)

        # ── ASCII art — line by line ──────────────────
        print()
        for line in ascii_lines:
            print(f"{Colors.GREEN}{Colors.BOLD}{line}{Colors.END}")
            time.sleep(0.07)

        # ── tagline — character by character ─────────
        print()
        tagline = "    ⚡  EH ZIP SUITE  |  by @ehmunna999  ⚡"
        sys.stdout.write(f"{Colors.CYAN}{Colors.BOLD}")
        for ch in tagline:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.03)
        sys.stdout.write(Colors.END + "\n")

        # ── bottom separator ─────────────────────────
        time.sleep(0.08)
        print(sep)
        time.sleep(0.15)
        print()

    def sep(self, c='═', n=54):
        print(f"{Colors.GREEN}{Colors.BOLD}{c*n}{Colors.END}")

    def hdr(self, t):
        self.sep()
        print(f"{Colors.CYAN}{Colors.BOLD}▶ {t}{Colors.END}")
        self.sep()

    def ok(self, t):  print(f"{Colors.GREEN}{Colors.BOLD}[+] {t}{Colors.END}")
    def err(self, t): print(f"{Colors.RED}{Colors.BOLD}[-] {t}{Colors.END}")
    def inf(self, t): print(f"{Colors.YELLOW}{Colors.BOLD}[*] {t}{Colors.END}")

    # ──────────────────────────────────────────────
    # MAIN MENU
    # ──────────────────────────────────────────────

    def _open_telegram(self):
        """Open Telegram group on startup — platform-aware, silent fail."""
        url = "https://t.me/ehmunna999"
        import platform, subprocess, threading

        def _launch():
            try:
                sys_name = platform.system()
                if sys_name == "Windows":
                    tg_deep = "tg://resolve?domain=ehmunna999"
                    subprocess.Popen(
                        ["cmd", "/c", "start", "", tg_deep],
                        shell=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                elif sys_name == "Darwin":
                    subprocess.Popen(
                        ["open", url],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.Popen(
                        ["xdg-open", url],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            except Exception:
                try:
                    import webbrowser
                    webbrowser.open(url)
                except Exception:
                    pass

        threading.Thread(target=_launch, daemon=True).start()

    def main_menu(self):
        self._open_telegram()
        self.banner()
        while True:
            self.hdr("MAIN MENU")
            print(f"{Colors.GREEN}1.{Colors.END} {Colors.WHITE}Human-Like Password Generator (ADVANCED){Colors.END}")
            print(f"{Colors.GREEN}2.{Colors.END} {Colors.WHITE}ZIP Brute-Force Cracker{Colors.END}")
            print(f"{Colors.GREEN}3.{Colors.END} {Colors.WHITE}Wordlist Tools (merge / common / pattern){Colors.END}")
            print(f"{Colors.GREEN}0.{Colors.END} {Colors.WHITE}Exit{Colors.END}")
            choice = input(f"\n{Colors.CYAN}[?] Select: {Colors.END}").strip()
            if   choice == '1': self.generate_human_like_passwords()
            elif choice == '2': self.crack_menu()
            elif choice == '3': self.wordlist_menu()
            elif choice == '0': sys.exit(0)
            else: self.err("Invalid option")

    # ──────────────────────────────────────────────
    # HUMAN-LIKE PASSWORD GENERATOR
    # ──────────────────────────────────────────────

    def generate_human_like_passwords(self):
        self.hdr("HUMAN-LIKE PASSWORD GENERATOR  (ADVANCED)")
        print(f"{Colors.WHITE}Provide personal info → engine builds every realistic combo.{Colors.END}")
        print(f"{Colors.YELLOW}Press Enter to skip any optional field.{Colors.END}\n")

        def ask(prompt, required=False):
            while True:
                v = input(f"{Colors.CYAN}[?] {prompt}: {Colors.END}").strip()
                if v or not required:
                    return v
                print(f"{Colors.RED}    (required){Colors.END}")

        full_name      = ask("Full Name (e.g. Muhammad Munna)", required=True)
        nickname       = ask("Nickname / Username (e.g. Munna)",  required=True)
        birth_year     = ask("Birth Year   (e.g. 1998)")
        birth_month    = ask("Birth Month  (e.g. 05)")
        birth_day      = ask("Birth Day    (e.g. 22)")
        mobile_number  = ask("Mobile Number (full, e.g. 8801712345678)")
        partner_name   = ask("Partner / Best-friend name")
        pet_name       = ask("Pet / Favourite word")
        custom_info    = ask("Any other keyword (school, city, team…)")

        print(f"\n{Colors.YELLOW}[*] Common Number Sequences{Colors.END}")
        print(f"    Enter sequences like 1234, 9876, 0786, 007, 786 — space-separated.")
        print(f"    These will be mixed with every name variation.")
        seq_raw        = ask("Common sequences (e.g. 1234 786 9999 007)")
        user_sequences = [s.strip() for s in seq_raw.split() if s.strip()] if seq_raw else []

        print(f"\n{Colors.YELLOW}[*] Basic Numeric Passwords{Colors.END}")
        print(f"    Include pure number passwords (12838, 9273219, 167878, 112233 …)")
        print(f"    in the SAME output file alongside name-based passwords.")
        basic_yn   = ask("Include basic numeric list in output? (y/n)")
        basic_flag = basic_yn.lower().startswith('y')

        output_file = ask("Output filename (default: advanced_wordlist.txt)")
        if not output_file:
            output_file = "advanced_wordlist.txt"

        print()
        self.inf("Building name-based password engine…")
        wordlist = self._engine(
            full_name, nickname, birth_year, birth_month, birth_day,
            mobile_number, partner_name, pet_name, custom_info, user_sequences
        )

        if basic_flag:
            self.inf("Building basic numeric engine…")
            basic_list = self._basic_numeric(
                mobile_number, birth_year, birth_month, birth_day, user_sequences
            )
            combined_set  = set(wordlist)
            numeric_extra = [p for p in basic_list if p not in combined_set]
            final_list    = wordlist + numeric_extra
        else:
            final_list = wordlist

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for pwd in final_list:
                    f.write(pwd + '\n')

            self.ok(f"Name-based passwords      : {len(wordlist):,}")
            if basic_flag:
                self.ok(f"Basic numeric (added)     : {len(numeric_extra):,}")
            self.ok(f"TOTAL in file             : {len(final_list):,}")
            self.ok(f"Saved to                  : {output_file}")

            print(f"\n{Colors.CYAN}[Sample — first 20 name-based]:{Colors.END}")
            for pwd in wordlist[:20]:
                print(f"  {Colors.GREEN}• {pwd}{Colors.END}")
            if basic_flag:
                print(f"\n{Colors.CYAN}[Sample — 20 numeric]:{Colors.END}")
                step = max(1, len(numeric_extra)//20)
                for pwd in numeric_extra[::step][:20]:
                    print(f"  {Colors.YELLOW}• {pwd}{Colors.END}")
            if len(final_list) > 40:
                print(f"  {Colors.YELLOW}  … {len(final_list):,} total in file{Colors.END}")

        except Exception as e:
            self.err(f"Write error: {e}")

    # ──────────────────────────────────────────────
    # CORE PATTERN ENGINE
    # ──────────────────────────────────────────────

    def _engine(self, full_name, nickname, birth_year, birth_month, birth_day,
                mobile_number, partner_name, pet_name, custom_info, user_sequences):
        passwords = set()
        add = passwords.add

        parts     = full_name.split()
        fname     = parts[0]  if parts        else ""
        lname     = parts[-1] if len(parts)>1 else ""
        initials  = "".join(p[0] for p in parts if p)

        mob = mobile_number.replace(" ", "").replace("-", "")
        m_full  = mob
        m_last3 = mob[-3:]  if len(mob)>=3  else mob
        m_last4 = mob[-4:]  if len(mob)>=4  else mob
        m_last6 = mob[-6:]  if len(mob)>=6  else mob
        m_first4= mob[:4]   if len(mob)>=4  else mob
        m_first6= mob[:6]   if len(mob)>=6  else mob
        m_mid4  = mob[3:7]  if len(mob)>=7  else ""
        m_mid3  = mob[3:6]  if len(mob)>=6  else ""

        by   = birth_year
        by2  = by[-2:]  if by and len(by)>=2 else ""

        bm   = birth_month.zfill(2) if birth_month else ""
        bd   = birth_day.zfill(2)   if birth_day   else ""
        dob_dash = f"{bd}-{bm}-{by}"   if (bd and bm and by) else ""
        dob_dot  = f"{bd}.{bm}.{by}"   if (bd and bm and by) else ""
        dob_ymd  = f"{by}{bm}{bd}"     if (bd and bm and by) else ""
        dob_dmy  = f"{bd}{bm}{by}"     if (bd and bm and by) else ""
        dob_dmy2 = f"{bd}{bm}{by2}"    if (bd and bm and by2) else ""
        dob_mdy  = f"{bm}{bd}{by2}"    if (bd and bm and by2) else ""

        raw_keywords = [
            nickname, fname, lname, partner_name, pet_name, custom_info,
            nickname.lower(), fname.lower(), lname.lower(),
            nickname.capitalize(), fname.capitalize(), lname.capitalize(),
            nickname.upper(), fname.upper(),
        ]
        keywords = list(dict.fromkeys(k for k in raw_keywords if k))

        SP_LIGHT = ['!', '@', '#', '$', '*', '.', '_', '-', '+', '?']
        SP_PAIR  = ['@@', '##', '$$', '!!', '**', '@#', '#@', '!@', '@!',
                    '#$', '$#', '!#', '#!', '@@@', '###', '!!!', '***',
                    '@@##', '##@@', '!@#', '@!#', '#!@', '!@#$', '@#$!',
                    '##$$', '$$##', '@@!', '!!@@', '@@##!!']
        SP_ALL   = SP_LIGHT + SP_PAIR

        STATIC_SEQS = [
            '0', '1', '12', '123', '1234', '12345', '123456',
            '0000', '1111', '2222', '3333', '4444', '5555', '6666',
            '7777', '8888', '9999', '1122', '2211', '1221', '2112',
            '1001', '1010', '0101',
            '007', '786', '420', '100', '101', '999', '111',
            '0786', '7860', '8086', '4040', '2020', '2019', '2021',
            '2022', '2023', '2024', '2025',
            '69', '77', '88', '99', '00',
            '786786', '007007', '420420',
            '1234567', '12345678', '123456789',
            '9876', '87654', '987654', '654321',
        ]
        ALL_SEQS = list(dict.fromkeys(STATIC_SEQS + user_sequences))

        MOB_FRAGS = [f for f in [m_last3, m_last4, m_last6, m_first4, m_first6, m_mid4, m_mid3] if f]

        DATE_FRAGS = [f for f in [by, by2, bm, bd, bm+bd, bd+bm,
                                   by2+bm, bm+by2, bd+by2, by2+bd,
                                   bm+bd+by2, bd+bm+by2, dob_ymd, dob_dmy, dob_dmy2, dob_mdy] if f]

        for kw in keywords:
            add(kw)

        for kw in keywords:
            for seq in ALL_SEQS:
                add(kw + seq)
                add(seq + kw)
                add(kw + seq + kw)

        for kw in keywords:
            for sp in SP_ALL:
                add(kw + sp)
                add(sp + kw)
                add(kw + sp + kw)

        for kw in keywords:
            for seq in ALL_SEQS:
                for sp in SP_ALL:
                    add(kw + seq + sp)
                    add(kw + sp + seq)
                    add(seq + kw + sp)
                    add(sp + seq + kw)

        for kw in keywords:
            for mf in MOB_FRAGS:
                add(kw + mf)
                add(mf + kw)
                for sp in SP_ALL:
                    add(kw + mf + sp)
                    add(kw + sp + mf)
                    add(mf + kw + sp)
                for seq in ALL_SEQS[:20]:
                    add(kw + mf + seq)
                    add(kw + seq + mf)

        for kw in keywords:
            for df in DATE_FRAGS:
                add(kw + df)
                add(df + kw)
                for sp in SP_ALL:
                    add(kw + df + sp)
                    add(kw + sp + df)
                    add(df + kw + sp)
                for seq in ALL_SEQS[:20]:
                    add(kw + df + seq)

        for kw in keywords:
            for df in DATE_FRAGS[:6]:
                for mf in MOB_FRAGS[:3]:
                    add(kw + df + mf)
                    add(kw + mf + df)
                    for sp in SP_LIGHT:
                        add(kw + df + mf + sp)
                        add(kw + mf + df + sp)

        kw_pairs = []
        unique_kw = list(dict.fromkeys(
            k for k in [nickname, fname, lname, partner_name, pet_name, custom_info] if k
        ))
        for i, a in enumerate(unique_kw):
            for b in unique_kw[i+1:]:
                kw_pairs.append((a, b))
                kw_pairs.append((a.capitalize(), b))
                kw_pairs.append((a, b.capitalize()))
                kw_pairs.append((a.capitalize(), b.capitalize()))

        for (a, b) in kw_pairs:
            add(a + b)
            add(b + a)
            add(a + '_' + b)
            add(a + '.' + b)
            for seq in ALL_SEQS[:15]:
                add(a + b + seq)
                add(a + seq + b)
            for sp in SP_LIGHT:
                add(a + b + sp)
                add(a + sp + b)

        if initials:
            for seq in ALL_SEQS:
                add(initials + seq)
                add(initials.upper() + seq)
            for mf in MOB_FRAGS:
                add(initials + mf)
            for df in DATE_FRAGS:
                add(initials + df)

        for mf in MOB_FRAGS:
            for df in DATE_FRAGS[:6]:
                add(mf + df)
                add(df + mf)
                for sp in SP_LIGHT:
                    add(mf + df + sp)
                    add(df + mf + sp)

        if m_full and len(m_full) >= 10:
            for kw in keywords[:4]:
                add(kw + m_full)
                add(m_full + kw)
                for sp in SP_LIGHT:
                    add(kw + m_full + sp)

        for dob in [dob_dash, dob_dot, dob_ymd, dob_dmy]:
            if not dob: continue
            add(dob)
            for kw in keywords[:4]:
                add(kw + dob)
                add(dob + kw)

        LEET = {'a':'4','e':'3','i':'1','o':'0','s':'5','t':'7','g':'9','b':'8'}

        def leet(w):
            out = ""
            for c in w.lower():
                out += LEET.get(c, c)
            return out

        for kw in unique_kw:
            l = leet(kw)
            if l != kw.lower():
                add(l)
                for seq in ALL_SEQS[:15]:
                    add(l + seq)
                for sp in SP_LIGHT:
                    add(l + sp)
                for df in DATE_FRAGS[:4]:
                    add(l + df)
                for mf in MOB_FRAGS[:2]:
                    add(l + mf)

        def toggle(w):
            return "".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(w))

        for kw in unique_kw:
            caps_variants = [kw.lower(), kw.upper(), kw.capitalize(), kw.title(), toggle(kw)]
            for v in caps_variants:
                for seq in ALL_SEQS[:20]:
                    add(v + seq)
                for sp in SP_LIGHT:
                    add(v + sp)

        for kw in unique_kw:
            rev = kw[::-1]
            add(rev)
            for seq in ALL_SEQS[:15]:
                add(rev + seq)
            for sp in SP_LIGHT:
                add(rev + sp)

        WALKS = ['qwerty', 'qwerty123', 'zxcvbn', 'asdfgh', '147258', '147258369',
                 'qazwsx', 'qweasd', '12qw', 'q1w2', 'q1w2e3', 'q1w2e3r4',
                 '1q2w3e', '1q2w3e4r', 'qwertyui', 'qwertyuiop']
        for kw in unique_kw:
            for wk in WALKS:
                add(kw + wk)
                add(wk + kw)

        for wk in WALKS:
            add(wk)

        for kw in unique_kw:
            add(kw * 2)
            add(kw.capitalize() + kw.lower())
            add(kw.lower() + kw.upper())

        SUFFIX_WORDS = ['love', 'king', 'queen', 'boss', 'bhai', 'vai', 'apa',
                        'bd', 'ctg', 'dhaka', 'mama', 'bro', 'sis',
                        'pass', 'key', 'root', 'admin', 'net', 'pro']
        for kw in unique_kw:
            for sw in SUFFIX_WORDS:
                add(kw + sw)
                add(kw + sw.capitalize())
                add(kw.capitalize() + sw)
                add(sw + kw)
                add(sw + kw.capitalize())

        for us in user_sequences:
            add(us)
            for kw in unique_kw:
                add(kw + us)
                add(us + kw)
                for sp in SP_ALL:
                    add(kw + us + sp)
                    add(kw + sp + us)
            for df in DATE_FRAGS[:6]:
                add(us + df)
                add(df + us)
            for mf in MOB_FRAGS[:3]:
                add(us + mf)
                add(mf + us)

        DOUBLE_SP = [
            '##', '@@', '!!', '$$', '**',
            '##@@', '@@##', '##!!', '!!##', '@@!!', '!!@@',
            '##@@!!', '@@##!!', '@@!!##', '!!@@##',
            '!@#', '@!#', '#@!', '!#@',
            '##$$', '$$##', '@@$$', '$$@@',
            '@@##@@', '##@@##',
        ]

        for sp in SP_PAIR:
            for seq in ALL_SEQS[:30]:
                add(sp + seq)
                add(seq + sp)

        for kw in unique_kw:
            kv_lo  = kw.lower()
            kv_cap = kw.capitalize()
            kv_up  = kw.upper()
            for n in range(10000):
                num4 = f"{n:04d}"
                add(kv_lo  + num4)
                add(kv_cap + num4)
                add(kv_up  + num4)
                add(num4   + kv_lo)
                add(num4   + kv_cap)
                add(kv_cap + num4 + '@')
                add(kv_cap + num4 + '!')
                add(kv_cap + num4 + '#')
                add(kv_cap + num4 + '@@')
                add(kv_cap + num4 + '##')
                add(kv_cap + num4 + '@#')

        if m_full:
            for kw in unique_kw:
                kv_lo  = kw.lower()
                kv_cap = kw.capitalize()
                kv_up  = kw.upper()
                for dsp in DOUBLE_SP:
                    add(kv_lo  + m_full + dsp)
                    add(kv_cap + m_full + dsp)
                    add(kv_up  + m_full + dsp)
                    add(dsp + kv_cap + m_full)
                    add(dsp + kv_lo  + m_full)
                    add(kv_cap + dsp + m_full)
                    add(kv_lo  + dsp + m_full)
                if m_last6:
                    for dsp in DOUBLE_SP[:10]:
                        add(kv_cap + m_last6 + dsp)
                        add(kv_lo  + m_last6 + dsp)
                        add(kv_up  + m_last6 + dsp)

        for d in '0123456789':
            for rep in range(2, 7):
                add(d * rep)

        for start in range(10):
            pair = ""
            for i in range(start, start + 5):
                pair += str(i % 10) * 2
                if len(pair) >= 4:
                    add(pair)

        digits = '0123456789'
        for length in range(4, 9):
            for start in range(10):
                asc  = "".join(str((start + i) % 10) for i in range(length))
                desc = "".join(str((start - i) % 10) for i in range(length))
                add(asc)
                add(desc)

        for a in range(10):
            for b in range(10):
                for c in range(10):
                    n5 = f"{a}{a}{b}{b}{c}"
                    n6 = f"{a}{a}{b}{b}{c}{c}"
                    add(n5)
                    add(n6)

        for n in range(1000, 100000):
            add(str(n))

        STANDALONE_NUMS = [
            '786', '786786', '007', '007007', '420', '1420', '1999', '2000',
            '01712', '01911', '01812', '01611',
            '11111', '22222', '33333', '44444', '55555', '66666',
            '77777', '88888', '99999', '00000',
            '12321', '23432', '34543', '45654',
            '10101', '01010', '11001', '00110',
            '13579', '24680', '97531', '08642',
            '80085', '31337', '12345', '54321',
            '11223', '22334', '33445', '44556', '55667', '66778', '77889',
            '99887', '88776', '77665', '66554', '55443', '44332', '33221',
            '112233', '223344', '334455', '445566', '556677', '667788', '778899',
            '998877', '887766', '776655', '665544', '554433', '443322', '332211',
            '11223344', '22334455', '33445566', '44556677', '55667788',
            '12233445', '23344556',
        ]
        for sn in STANDALONE_NUMS:
            add(sn)
            for kw in unique_kw:
                add(kw.capitalize() + sn)
                add(kw.lower()      + sn)
                add(sn + kw.capitalize())

        for us in user_sequences:
            add(us)
            add(us * 2)
            add(us + us[-1])
            add(us[0] + us)
            if len(us) >= 2:
                add(us[::-1])
            for sp in DOUBLE_SP[:8]:
                add(us + sp)
                add(sp + us)

        CULTURAL = [
            '786','7860','78600','786786','7867860',
            '007','0070','00700','007007',
            '420','4200','42000','420420',
            '1420','14200','142000',
            '1971','19710326','19711216',
            '01710','01712','01811','01912','01611','01511',
            '9999','99999','999999','9999999',
            '8888','88888','888888','8888888',
            '1234567','12345678','123456789',
            '9876543','87654321','876543210',
            '1111111','2222222','3333333','4444444',
            '5555555','6666666','7777777',
            '0000000','1000000','9000000',
            '13131313','24242424','12121212','21212121',
        ]
        for cn in CULTURAL:
            add(cn)

        if by:
            for n in range(10000):
                add(by + f"{n:04d}")
                add(f"{n:04d}" + by)
            if by2:
                for n in range(1000):
                    add(by2 + f"{n:03d}")
                    add(f"{n:03d}" + by2)

        passwords.discard("")
        passwords = {p for p in passwords if len(p) >= 4}
        return sorted(passwords)

    # ──────────────────────────────────────────────
    # BASIC NUMERIC WORDLIST ENGINE
    # ──────────────────────────────────────────────

    def _basic_numeric(self, mobile_number, birth_year, birth_month,
                       birth_day, user_sequences):
        nums = set()
        add  = nums.add

        mob = mobile_number.replace(" ","").replace("-","")
        mob_frags = []
        for length in range(3, len(mob)+1):
            mob_frags.append(mob[-length:])
            mob_frags.append(mob[:length])
        mob_frags = [f for f in mob_frags if f]

        by  = birth_year
        by2 = by[-2:] if by and len(by)>=2 else ""
        bm  = birth_month.zfill(2) if birth_month else ""
        bd  = birth_day.zfill(2)   if birth_day   else ""
        date_frags = [f for f in [by, by2, bm, bd,
                                   bm+bd, bd+bm, by2+bm, bm+by2,
                                   bd+by2, by2+bd,
                                   bm+bd+by, bd+bm+by, by+bm+bd,
                                   bm+bd+by2, bd+bm+by2] if f]

        for n in range(10000):
            add(f"{n:04d}")
            add(str(n))

        for n in range(10000, 100000):
            add(str(n))

        for n in range(100000, 1000000):
            add(str(n))

        for n in range(1000000, 10000000):
            add(str(n))

        for d in "0123456789":
            for rep in range(2, 9):
                add(d * rep)

        for a in "0123456789":
            for b in "0123456789":
                pair = a*2 + b*2
                add(pair)
                for c in "0123456789":
                    add(pair + c*2)
                    add(pair + c*2 + a*2)
                    add(a*2 + b*2 + c)
                    add(a*2 + b + c*2)

        for length in range(3, 9):
            for start in range(10):
                asc  = "".join(str((start+i) % 10) for i in range(length))
                desc = "".join(str((start-i) % 10) for i in range(length))
                add(asc)
                add(desc)

        for n in range(10000):
            s = str(n)
            add(s + s[::-1])
            add(s[::-1] + s)

        for frag in mob_frags:
            add(frag)
            for frag2 in mob_frags:
                if frag != frag2 and len(frag+frag2) <= 13:
                    add(frag + frag2)

        for df in date_frags:
            add(df)
            for df2 in date_frags:
                if df != df2 and len(df+df2) <= 10:
                    add(df + df2)

        for frag in mob_frags[:6]:
            for df in date_frags[:6]:
                if len(frag+df) <= 12:
                    add(frag + df)
                    add(df + frag)

        for us in user_sequences:
            if us.isdigit():
                add(us)
                add(us * 2)
                add(us + us[-1] if us else us)
                add(us[0] + us if us else us)
                add(us[::-1])
                for df in date_frags[:4]:
                    add(us + df)
                    add(df + us)
                for frag in mob_frags[:3]:
                    add(us + frag)
                    add(frag + us)

        CULTURAL = [
            '786','7860','78600','786786','7867860',
            '007','0070','00700','007007',
            '420','4200','42000','420420',
            '1420','14200','142000',
            '1971','19710326','19711216',
            '01710','01712','01811','01912','01611','01511',
            '9999','99999','999999','9999999',
            '8888','88888','888888','8888888',
            '1234567','12345678','123456789',
            '9876543','87654321','876543210',
            '1111111','2222222','3333333','4444444',
            '5555555','6666666','7777777',
            '0000000','1000000','9000000',
            '13131313','24242424','12121212','21212121',
        ]
        for cn in CULTURAL:
            add(cn)

        if by:
            for n in range(10000):
                add(by + f"{n:04d}")
                add(f"{n:04d}" + by)
            if by2:
                for n in range(1000):
                    add(by2 + f"{n:03d}")
                    add(f"{n:03d}" + by2)

        nums.discard("")
        nums = {p for p in nums if p.isdigit() and len(p) >= 3}
        return sorted(nums, key=lambda x: (len(x), x))


    # ──────────────────────────────────────────────────────────────────────────
    # ZIP CRACKER — FIXED (v3)
    #
    # Bug fixes:
    #   1. Replaced extractall() with zf.read() for reliable password testing.
    #   2. Added encoding fallbacks: utf-8, latin-1, cp1252, utf-16.
    #   3. AES-256 ZIPs now use pyzipper as fallback.
    #   4. Fixed race condition in attempts counter and found flag.
    # ──────────────────────────────────────────────────────────────────────────

    def _detect_encryption(self, zip_path):
        """
        Detects ZIP encryption type.
        Returns: 'aes256', 'zipcrypto', or 'none'
        """
        try:
            with open(zip_path, 'rb') as f:
                data = f.read(4096)
            # AES-256 marker: extra field tag 0x9901
            if b'\x01\x99' in data or b'\x99\x01' in data:
                return 'aes256'
            zf = zipfile.ZipFile(zip_path)
            for info in zf.infolist():
                if info.flag_bits & 0x1:   # encrypted flag
                    return 'zipcrypto'
            zf.close()
            return 'none'
        except Exception:
            return 'zipcrypto'  # safe assumption

    def crack_menu(self):
        self.hdr("ZIP BRUTE-FORCE CRACKER")

        zip_path = input(f"{Colors.CYAN}[?] ZIP file path: {Colors.END}").strip()
        if not os.path.exists(zip_path):
            self.err(f"File not found: {zip_path}")
            return

        wl_path = input(f"{Colors.CYAN}[?] Wordlist path: {Colors.END}").strip()
        if not os.path.exists(wl_path):
            self.err(f"File not found: {wl_path}")
            return

        threads_n = input(f"{Colors.CYAN}[?] Threads (default 4): {Colors.END}").strip()
        try:
            threads_n = int(threads_n)
        except Exception:
            threads_n = 4

        # ── encryption detection ─────────────────────────────────────
        enc_type = self._detect_encryption(zip_path)
        if enc_type == 'aes256':
            if not HAS_PYZIPPER:
                self.err("This ZIP is AES-256 encrypted.")
                self.err("Run:  pip install pyzipper")
                self.err("Then try again.")
                return
            self.inf("AES-256 ZIP detected → using pyzipper.")
        else:
            self.inf("ZipCrypto ZIP detected → using zipfile.")

        # ── find a testable file inside the ZIP ──────────────────────
        try:
            zf_probe = zipfile.ZipFile(zip_path)
            names = [n for n in zf_probe.namelist() if not n.endswith('/')]
            zf_probe.close()
            if not names:
                self.err("ZIP contains no files.")
                return
            test_file = names[0]
            self.inf(f"Test file: {test_file}")
        except Exception as e:
            self.err(f"ZIP open error: {e}")
            return

        # ── reset state ──────────────────────────────────────────────
        self.found    = False
        self.password = None
        self.attempts = 0

        # ── load wordlist into queue ─────────────────────────────────
        q = Queue()
        loaded = 0
        with open(wl_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip()
                if w:
                    q.put(w)
                    loaded += 1

        if loaded == 0:
            self.err("Wordlist is empty.")
            return

        total = loaded
        self.inf(f"Loaded {total:,} passwords. Starting {threads_n} threads…\n")

        import time
        start = time.time()

        # ════════════════════════════════════════════════════════
        # WORKER — ORIGINAL (working)
        # ════════════════════════════════════════════════════════
        def worker():
            # Each thread creates its own ZipFile instance (ZipFile is not thread-safe)
            if enc_type == 'aes256' and HAS_PYZIPPER:
                try:
                    zf = pyzipper.AESZipFile(zip_path)
                except Exception as e:
                    self.err(f"ZIP open error (thread): {e}")
                    return
            else:
                try:
                    zf = zipfile.ZipFile(zip_path)
                except Exception as e:
                    self.err(f"ZIP open error (thread): {e}")
                    return

            # Encoding list — utf-8 first, latin-1 fallback
            ENCODINGS = ('utf-8', 'latin-1', 'cp1252', 'utf-16')

            while True:
                # Exit if password already found
                if self.found:
                    break

                # Get next password from queue
                try:
                    pwd = q.get_nowait()
                except Empty:
                    break

                # Try each encoding
                cracked = False
                for enc in ENCODINGS:
                    if self.found:
                        break
                    try:
                        pwd_bytes = pwd.encode(enc, errors='ignore')
                        # test with read() instead of extractall()
                        zf.read(test_file, pwd=pwd_bytes)
                        # No exception means password is correct
                        with self.lock:
                            if not self.found:
                                self.found    = True
                                self.password = pwd
                        cracked = True
                        break

                    except RuntimeError as e:
                        err_str = str(e).lower()
                        if 'password' in err_str or 'bad' in err_str or 'crc' in err_str:
                            continue
                        continue

                    except zipfile.BadZipFile:
                        self.err("ZIP file corrupted.")
                        return

                    except Exception:
                        continue

                # Update attempt counter
                with self.lock:
                    self.attempts += 1
                    if self.attempts % 500 == 0:
                        elapsed = time.time() - start
                        rate    = self.attempts / elapsed if elapsed > 0 else 0
                        pct     = (self.attempts / total * 100) if total else 0
                        print(
                            f"{Colors.CYAN}[~] {self.attempts:>8,} / {total:,} "
                            f"({pct:5.1f}%)  {rate:,.0f} pwd/s{Colors.END}",
                            end='\r', flush=True
                        )

                q.task_done()

            zf.close()

        # ── launch threads ───────────────────────────────────────────
        ts = [Thread(target=worker, daemon=True) for _ in range(threads_n)]
        for t in ts: t.start()
        for t in ts: t.join()

        elapsed = time.time() - start
        print()  # clear the \r progress line

        if self.found:
            self.ok(f"PASSWORD FOUND : {self.password}")
            self.ok(f"Attempts       : {self.attempts:,}")
            self.ok(f"Time           : {elapsed:.2f}s")
        else:
            self.err("Password not found in wordlist.")
            self.inf(f"Tried {self.attempts:,} passwords in {elapsed:.2f}s")
            self.inf("Suggestions:")
            self.inf("  1. Try a larger wordlist.")
            self.inf("  2. Generate a new wordlist using Option 1 (Generator).")
            if enc_type == 'aes256' and not HAS_PYZIPPER:
                self.inf("  3. Run: pip install pyzipper  (AES-256 support)")

    # ──────────────────────────────────────────────
    # WORDLIST TOOLS
    # ──────────────────────────────────────────────

    def wordlist_menu(self):
        self.hdr("WORDLIST TOOLS")
        print(f"{Colors.GREEN}1.{Colors.END} {Colors.WHITE}Merge & deduplicate wordlists{Colors.END}")
        print(f"{Colors.GREEN}2.{Colors.END} {Colors.WHITE}Generate common passwords{Colors.END}")
        print(f"{Colors.GREEN}3.{Colors.END} {Colors.WHITE}Custom base-word variations{Colors.END}")
        print(f"{Colors.GREEN}4.{Colors.END} {Colors.WHITE}Numbers 0–999999 + word combos{Colors.END}")
        choice = input(f"\n{Colors.CYAN}[?] Select: {Colors.END}").strip()
        if   choice == '1': self._merge_wl()
        elif choice == '2': self._common_wl()
        elif choice == '3': self._pattern_wl()
        elif choice == '4': self._numbers_wl()
        else: self.err("Invalid option")

    def _merge_wl(self):
        merged = set()
        while True:
            p = input(f"{Colors.CYAN}[?] File path (Enter to finish): {Colors.END}").strip()
            if not p: break
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    for ln in f:
                        w = ln.strip()
                        if w: merged.add(w)
                self.ok(f"Loaded: {p}")
            else:
                self.err(f"Not found: {p}")
        if not merged:
            self.err("Nothing to merge"); return
        out = input(f"{Colors.CYAN}[?] Output file: {Colors.END}").strip() or "merged.txt"
        with open(out, 'w', encoding='utf-8') as f:
            for w in sorted(merged): f.write(w+'\n')
        self.ok(f"Merged {len(merged):,} unique passwords → {out}")

    def _common_wl(self):
        common = [
            'password','admin','123456','12345678','qwerty','abc123','monkey',
            'letmein','trustno1','dragon','baseball','111111','iloveyou','master',
            'sunshine','passw0rd','shadow','123123','654321','superman','qazwsx',
            'michael','football','welcome','ninja','mustang','password1',
        ]
        out = input(f"{Colors.CYAN}[?] Output file: {Colors.END}").strip() or "common.txt"
        with open(out, 'w') as f:
            for p in common: f.write(p+'\n')
        self.ok(f"Saved {len(common)} common passwords → {out}")

    def _pattern_wl(self):
        base = input(f"{Colors.CYAN}[?] Base word: {Colors.END}").strip()
        if not base: self.err("Required"); return
        out  = input(f"{Colors.CYAN}[?] Output file: {Colors.END}").strip() or "pattern.txt"
        variants = [
            base, base.capitalize(), base.upper(),
            base+'1', base+'12', base+'123', base+'1234',
            base+'@', base+'!', base+'#', base+'@123',
            base+'2024', base+'2025', '123'+base, base+base,
        ]
        with open(out,'w') as f:
            for v in variants: f.write(v+'\n')
        self.ok(f"Saved {len(variants)} variations → {out}")

    def _numbers_wl(self):
        out = input(f"{Colors.CYAN}[?] Output file: {Colors.END}").strip() or "numbers.txt"
        words = ['admin','root','user','test','pass','data','server','bd']
        with open(out,'w') as f:
            for i in range(1000000): f.write(str(i)+'\n')
            for w in words:
                f.write(w+'\n')
                for i in range(10000): f.write(w+str(i)+'\n')
        self.ok(f"Saved → {out}")


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    suite = EHZipSuite()
    suite.main_menu()
