#!/usr/bin/env python3
import zipfile
import os
import sys
import itertools
from threading import Thread, Lock
from queue import Queue

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
        print(f"""
{Colors.GREEN}{Colors.BOLD}
    ███████╗██╗  ██╗    ███████╗██╗██████╗
    ██╔════╝██║  ██║    ╚══███╔╝██║██╔══██╗
    █████╗  ███████║      ███╔╝ ██║██████╔╝
    ██╔══╝  ██╔══██║     ███╔╝  ██║██╔═══╝
    ███████╗██║  ██║    ███████╗██║██║
    ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝╚═╝

       Advanced ZIP Suite  — Password Engine v2
       Human-Like Wordlist Generator (REBUILT)
{Colors.END}""")

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

    def main_menu(self):
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

        # ── NEW: common number sequences ──────────────────────────────
        print(f"\n{Colors.YELLOW}[*] Common Number Sequences{Colors.END}")
        print(f"    Enter sequences like 1234, 9876, 0786, 007, 786 — space-separated.")
        print(f"    These will be mixed with every name variation.")
        seq_raw        = ask("Common sequences (e.g. 1234 786 9999 007)")
        user_sequences = [s.strip() for s in seq_raw.split() if s.strip()] if seq_raw else []

        # ── Basic numeric option ───────────────────────────────────
        print(f"\n{Colors.YELLOW}[*] Basic Numeric Passwords{Colors.END}")
        print(f"    Include pure number passwords (12838, 9273219, 167878, 112233 …)")
        print(f"    in the SAME output file alongside name-based passwords.")
        basic_yn   = ask("Include basic numeric list in output? (y/n)")
        basic_flag = basic_yn.lower().startswith('y')

        output_file = ask("Output filename (default: advanced_wordlist.txt)")
        if not output_file:
            output_file = "advanced_wordlist.txt"

        print()
        self.inf("Building name-based password engine\u2026")
        wordlist = self._engine(
            full_name, nickname, birth_year, birth_month, birth_day,
            mobile_number, partner_name, pet_name, custom_info, user_sequences
        )

        if basic_flag:
            self.inf("Building basic numeric engine\u2026")
            basic_list = self._basic_numeric(
                mobile_number, birth_year, birth_month, birth_day, user_sequences
            )
            # merge — deduplicate, keep sort order: name-based first, numeric appended
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

            print(f"\n{Colors.CYAN}[Sample \u2014 first 20 name-based]:{Colors.END}")
            for pwd in wordlist[:20]:
                print(f"  {Colors.GREEN}\u2022 {pwd}{Colors.END}")
            if basic_flag:
                print(f"\n{Colors.CYAN}[Sample \u2014 20 numeric]:{Colors.END}")
                step = max(1, len(numeric_extra)//20)
                for pwd in numeric_extra[::step][:20]:
                    print(f"  {Colors.YELLOW}\u2022 {pwd}{Colors.END}")
            if len(final_list) > 40:
                print(f"  {Colors.YELLOW}  \u2026 {len(final_list):,} total in file{Colors.END}")

        except Exception as e:
            self.err(f"Write error: {e}")

    # ──────────────────────────────────────────────
    # CORE PATTERN ENGINE
    # ──────────────────────────────────────────────

    def _engine(self, full_name, nickname, birth_year, birth_month, birth_day,
                mobile_number, partner_name, pet_name, custom_info, user_sequences):
        """
        Generates every password a real human could plausibly create
        from the supplied personal data.
        """
        passwords = set()
        add = passwords.add

        # ── Derived tokens ───────────────────────────────────────────
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

        # ── Keyword bank ─────────────────────────────────────────────
        # collect all meaningful words; filter empty
        raw_keywords = [
            nickname, fname, lname, partner_name, pet_name, custom_info,
            nickname.lower(), fname.lower(), lname.lower(),
            nickname.capitalize(), fname.capitalize(), lname.capitalize(),
            nickname.upper(), fname.upper(),
        ]
        keywords = list(dict.fromkeys(k for k in raw_keywords if k))

        # ── Special-char sets ────────────────────────────────────────
        SP_LIGHT = ['!', '@', '#', '$', '*', '.', '_', '-', '+', '?']
        SP_PAIR  = ['@@', '##', '$$', '!!', '**', '@#', '#@', '!@', '@!',
                    '#$', '$#', '!#', '#!', '@@@', '###', '!!!', '***',
                    '@@##', '##@@', '!@#', '@!#', '#!@', '!@#$', '@#$!',
                    '##$$', '$$##', '@@!', '!!@@', '@@##!!']
        SP_ALL   = SP_LIGHT + SP_PAIR

        # ── Static number sequences ──────────────────────────────────
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
        # merge user-supplied sequences
        ALL_SEQS = list(dict.fromkeys(STATIC_SEQS + user_sequences))

        # ── Mobile fragments ─────────────────────────────────────────
        MOB_FRAGS = [f for f in [m_last3, m_last4, m_last6, m_first4, m_first6, m_mid4, m_mid3] if f]

        # ── Date fragments ───────────────────────────────────────────
        DATE_FRAGS = [f for f in [by, by2, bm, bd, bm+bd, bd+bm,
                                   by2+bm, bm+by2, bd+by2, by2+bd,
                                   bm+bd+by2, bd+bm+by2, dob_ymd, dob_dmy, dob_dmy2, dob_mdy] if f]

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 1 — bare keywords & case variations
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            add(kw)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 2 — keyword + every number sequence
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            for seq in ALL_SEQS:
                add(kw + seq)
                add(seq + kw)
                add(kw + seq + kw)          # MunNA1234MunNA style

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 3 — keyword + special char
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            for sp in SP_ALL:
                add(kw + sp)
                add(sp + kw)
                add(kw + sp + kw)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 4 — keyword + number sequence + special char
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            for seq in ALL_SEQS:
                for sp in SP_ALL:
                    add(kw + seq + sp)
                    add(kw + sp + seq)
                    add(seq + kw + sp)
                    add(sp + seq + kw)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 5 — keyword + mobile fragment
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            for mf in MOB_FRAGS:
                add(kw + mf)
                add(mf + kw)
                for sp in SP_ALL:
                    add(kw + mf + sp)
                    add(kw + sp + mf)
                    add(mf + kw + sp)
                for seq in ALL_SEQS[:20]:   # top 20 seqs only to avoid explosion
                    add(kw + mf + seq)
                    add(kw + seq + mf)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 6 — keyword + date fragment
        # ═══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 7 — keyword + date + mobile
        # ═══════════════════════════════════════════════════════════════
        for kw in keywords:
            for df in DATE_FRAGS[:6]:       # limit combinatorial
                for mf in MOB_FRAGS[:3]:
                    add(kw + df + mf)
                    add(kw + mf + df)
                    for sp in SP_LIGHT:
                        add(kw + df + mf + sp)
                        add(kw + mf + df + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 8 — two keywords combined
        # ═══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 9 — initials + fragments
        # ═══════════════════════════════════════════════════════════════
        if initials:
            for seq in ALL_SEQS:
                add(initials + seq)
                add(initials.upper() + seq)
            for mf in MOB_FRAGS:
                add(initials + mf)
            for df in DATE_FRAGS:
                add(initials + df)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 10 — mobile fragments + date fragments (no name)
        # ═══════════════════════════════════════════════════════════════
        for mf in MOB_FRAGS:
            for df in DATE_FRAGS[:6]:
                add(mf + df)
                add(df + mf)
                for sp in SP_LIGHT:
                    add(mf + df + sp)
                    add(df + mf + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 11 — full mobile + name + special
        # ═══════════════════════════════════════════════════════════════
        if m_full and len(m_full) >= 10:
            for kw in keywords[:4]:
                add(kw + m_full)
                add(m_full + kw)
                for sp in SP_LIGHT:
                    add(kw + m_full + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 12 — dob full-format strings
        # ═══════════════════════════════════════════════════════════════
        for dob in [dob_dash, dob_dot, dob_ymd, dob_dmy]:
            if not dob: continue
            add(dob)
            for kw in keywords[:4]:
                add(kw + dob)
                add(dob + kw)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 13 — leet-speak on top keywords
        # ═══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 14 — capitalisation variants (Title, UPPER, tOGGLE)
        # ═══════════════════════════════════════════════════════════════
        def toggle(w):
            return "".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(w))

        for kw in unique_kw:
            caps_variants = [kw.lower(), kw.upper(), kw.capitalize(), kw.title(), toggle(kw)]
            for v in caps_variants:
                for seq in ALL_SEQS[:20]:
                    add(v + seq)
                for sp in SP_LIGHT:
                    add(v + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 15 — reverse name
        # ═══════════════════════════════════════════════════════════════
        for kw in unique_kw:
            rev = kw[::-1]
            add(rev)
            for seq in ALL_SEQS[:15]:
                add(rev + seq)
            for sp in SP_LIGHT:
                add(rev + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 16 — keyboard-walk suffixes (very common on BD mobile)
        # ═══════════════════════════════════════════════════════════════
        WALKS = ['qwerty', 'qwerty123', 'zxcvbn', 'asdfgh', '147258', '147258369',
                 'qazwsx', 'qweasd', '12qw', 'q1w2', 'q1w2e3', 'q1w2e3r4',
                 '1q2w3e', '1q2w3e4r', 'qwertyui', 'qwertyuiop']
        for kw in unique_kw:
            for wk in WALKS:
                add(kw + wk)
                add(wk + kw)

        for wk in WALKS:
            add(wk)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 17 — name repeated / doubled
        # ═══════════════════════════════════════════════════════════════
        for kw in unique_kw:
            add(kw * 2)
            add(kw.capitalize() + kw.lower())
            add(kw.lower() + kw.upper())

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 18 — common suffix words + keyword
        # ═══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 19 — user-supplied sequences standalone + combined
        # (dedicated block so user sequences get full treatment)
        # ═══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 20 — pure special + seq combos (no name)
        # (catches lazy passwords: @@1234, 1234!!, etc.)
        # ═══════════════════════════════════════════════════════════════
        for sp in SP_PAIR:
            for seq in ALL_SEQS[:30]:
                add(sp + seq)
                add(seq + sp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 21 — keyword + FULL 4-digit range (0000–9999)
        # covers: Munna2638, Munna8734, munna0091, MUNNA5500 …
        # ═══════════════════════════════════════════════════════════════
        for kw in unique_kw:
            kv_lo  = kw.lower()
            kv_cap = kw.capitalize()
            kv_up  = kw.upper()
            for n in range(10000):
                num4 = f"{n:04d}"          # zero-padded: 0000..9999
                # bare combos
                add(kv_lo  + num4)
                add(kv_cap + num4)
                add(kv_up  + num4)
                add(num4   + kv_lo)
                add(num4   + kv_cap)
                # + light special suffix (most common real-world pattern)
                add(kv_cap + num4 + '@')
                add(kv_cap + num4 + '!')
                add(kv_cap + num4 + '#')
                add(kv_cap + num4 + '@@')
                add(kv_cap + num4 + '##')
                add(kv_cap + num4 + '@#')

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 22 — keyword + full mobile number + double specials
        # covers: Munna8801712345678##@@, Munna8801712345678@@##
        # ═══════════════════════════════════════════════════════════════
        DOUBLE_SP = [
            '##', '@@', '!!', '$$', '**',
            '##@@', '@@##', '##!!', '!!##', '@@!!', '!!@@',
            '##@@!!', '@@##!!', '@@!!##', '!!@@##',
            '!@#', '@!#', '#@!', '!#@',
            '##$$', '$$##', '@@$$', '$$@@',
            '@@##@@', '##@@##',
        ]
        if m_full:
            for kw in unique_kw:
                kv_lo  = kw.lower()
                kv_cap = kw.capitalize()
                kv_up  = kw.upper()
                for dsp in DOUBLE_SP:
                    # name + full_mobile + double_special
                    add(kv_lo  + m_full + dsp)
                    add(kv_cap + m_full + dsp)
                    add(kv_up  + m_full + dsp)
                    # double_special + name + full_mobile
                    add(dsp + kv_cap + m_full)
                    add(dsp + kv_lo  + m_full)
                    # name + double_special + full_mobile
                    add(kv_cap + dsp + m_full)
                    add(kv_lo  + dsp + m_full)
                # also: name + last6 + double special (shorter mobile variant)
                if m_last6:
                    for dsp in DOUBLE_SP[:10]:
                        add(kv_cap + m_last6 + dsp)
                        add(kv_lo  + m_last6 + dsp)
                        add(kv_up  + m_last6 + dsp)

        # ═══════════════════════════════════════════════════════════════
        # PATTERN GROUP 23 — pure numeric sequences (no name)
        # covers: 11223, 80665, 11223344, repeating / sequential patterns
        # ═══════════════════════════════════════════════════════════════

        # a) repeating digits: 11, 22, 111, 222 … 11223344 style
        for d in '0123456789':
            for rep in range(2, 7):           # 11, 111, 1111, 11111, 111111
                add(d * rep)

        # b) double-digit pairs: 1122, 2233, 3344 … 11223344, 00112233
        for start in range(10):
            pair = ""
            for i in range(start, start + 5):
                pair += str(i % 10) * 2
                if len(pair) >= 4:
                    add(pair)

        # c) ascending / descending runs of length 4-8
        digits = '0123456789'
        for length in range(4, 9):
            for start in range(10):
                asc  = "".join(str((start + i) % 10) for i in range(length))
                desc = "".join(str((start - i) % 10) for i in range(length))
                add(asc)
                add(desc)

        # d) 5-digit and 6-digit all-same + near-sequential (80665, 11223…)
        for a in range(10):
            for b in range(10):
                for c in range(10):
                    n5 = f"{a}{a}{b}{b}{c}"
                    n6 = f"{a}{a}{b}{b}{c}{c}"
                    add(n5)
                    add(n6)

        # e-pre) FULL standalone numeric ranges — covers 80665, 11223, any 4-5 digit pure number
        for n in range(1000, 100000):        # 1000 → 99999 (4-digit and 5-digit complete)
            add(str(n))

        # e) common Bangladeshi short-codes & religious numbers standalone
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
            # also: name + this standalone number
            for kw in unique_kw:
                add(kw.capitalize() + sn)
                add(kw.lower()      + sn)
                add(sn + kw.capitalize())

        # f) user-supplied sequences as pure standalones with length variations
        for us in user_sequences:
            add(us)
            add(us * 2)
            add(us + us[-1])    # 1234 → 12344
            add(us[0] + us)     # 1234 → 11234
            if len(us) >= 2:
                add(us[::-1])   # reverse: 4321
            for sp in DOUBLE_SP[:8]:
                add(us + sp)
                add(sp + us)

        # ── Cleanup: remove blanks & very short (< 4 chars) ──────────
        passwords.discard("")
        passwords = {p for p in passwords if len(p) >= 4}

        return sorted(passwords)

    # ──────────────────────────────────────────────
    # BASIC NUMERIC WORDLIST ENGINE
    # ──────────────────────────────────────────────

    def _basic_numeric(self, mobile_number, birth_year, birth_month,
                       birth_day, user_sequences):
        """
        Pure number-only password list.
        Covers: 4-digit, 5-digit, 6-digit, 7-digit, 8-digit ranges,
        all repeating/sequential patterns, mobile-derived numerics,
        date-derived numerics, user sequences, and combinations of these.
        """
        nums = set()
        add  = nums.add

        # ── mobile fragments ─────────────────────────────────────────
        mob = mobile_number.replace(" ","").replace("-","")
        mob_frags = []
        for length in range(3, len(mob)+1):
            mob_frags.append(mob[-length:])   # last N digits
            mob_frags.append(mob[:length])    # first N digits
        mob_frags = [f for f in mob_frags if f]

        # ── date fragments ───────────────────────────────────────────
        by  = birth_year
        by2 = by[-2:] if by and len(by)>=2 else ""
        bm  = birth_month.zfill(2) if birth_month else ""
        bd  = birth_day.zfill(2)   if birth_day   else ""
        date_frags = [f for f in [by, by2, bm, bd,
                                   bm+bd, bd+bm, by2+bm, bm+by2,
                                   bd+by2, by2+bd,
                                   bm+bd+by, bd+bm+by, by+bm+bd,
                                   bm+bd+by2, bd+bm+by2] if f]

        # ── RANGE 1: all numbers 0 – 9999 (4-digit complete) ─────────
        for n in range(10000):
            add(f"{n:04d}")   # zero-padded: 0000..9999
            add(str(n))       # no padding:  0..9999

        # ── RANGE 2: 10000 – 99999 (5-digit complete) ────────────────
        for n in range(10000, 100000):
            add(str(n))

        # ── RANGE 3: 100000 – 999999 (6-digit complete) ─────────────
        for n in range(100000, 1000000):
            add(str(n))

        # ── RANGE 4: 1000000 – 9999999 (7-digit complete) ──────────────
        for n in range(1000000, 10000000):
            add(str(n))

        # ── RANGE 5: 8-digit — pattern-based only (90M entries too large) ──

        # ── PATTERN: repeating single digit  11, 111, 1111 … ─────────
        for d in "0123456789":
            for rep in range(2, 9):
                add(d * rep)

        # ── PATTERN: repeating digit pairs  1122, 223344, 11223344 ───
        for a in "0123456789":
            for b in "0123456789":
                pair = a*2 + b*2
                add(pair)            # 4-digit: 1122
                for c in "0123456789":
                    add(pair + c*2)  # 6-digit: 112233
                    add(pair + c*2 + a*2)  # 8-digit: 11223311
                    # 5-digit: 11223
                    add(a*2 + b*2 + c)
                    add(a*2 + b + c*2)

        # ── PATTERN: ascending / descending runs ──────────────────────
        for length in range(3, 9):
            for start in range(10):
                asc  = "".join(str((start+i) % 10) for i in range(length))
                desc = "".join(str((start-i) % 10) for i in range(length))
                add(asc)
                add(desc)

        # ── PATTERN: mirrored / palindrome numbers ────────────────────
        for n in range(10000):
            s = str(n)
            add(s + s[::-1])    # 1234 → 12344321
            add(s[::-1] + s)    # 1234 → 43211234

        # ── PATTERN: mobile combinations ──────────────────────────────
        for frag in mob_frags:
            add(frag)
            for frag2 in mob_frags:
                if frag != frag2 and len(frag+frag2) <= 13:
                    add(frag + frag2)

        # ── PATTERN: date combinations ────────────────────────────────
        for df in date_frags:
            add(df)
            for df2 in date_frags:
                if df != df2 and len(df+df2) <= 10:
                    add(df + df2)

        # ── PATTERN: mobile + date numeric combos ─────────────────────
        for frag in mob_frags[:6]:
            for df in date_frags[:6]:
                if len(frag+df) <= 12:
                    add(frag + df)
                    add(df + frag)

        # ── PATTERN: user sequences standalone + combined ─────────────
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

        # ── PATTERN: common culturally significant numbers (BD) ───────
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

        # ── PATTERN: year-based 6-8 digit (birth year combos) ─────────
        if by:
            for n in range(10000):
                add(by + f"{n:04d}")     # 19980000..19989999
                add(f"{n:04d}" + by)     # 000019980..99991998
            if by2:
                for n in range(1000):
                    add(by2 + f"{n:03d}")
                    add(f"{n:03d}" + by2)

        # cleanup
        nums.discard("")
        nums = {p for p in nums if p.isdigit() and len(p) >= 3}
        return sorted(nums, key=lambda x: (len(x), x))


    # ──────────────────────────────────────────────
    # ZIP CRACKER
    # ──────────────────────────────────────────────

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
        try:   threads_n = int(threads_n)
        except: threads_n = 4

        self.found    = False
        self.password = None
        self.attempts = 0

        q = Queue()
        with open(wl_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip()
                if w:
                    q.put(w)

        total = q.qsize()
        self.inf(f"Loaded {total:,} passwords. Starting {threads_n} threads…\n")

        start = __import__('time').time()

        def worker():
            try:
                zf = zipfile.ZipFile(zip_path)
            except Exception as e:
                self.err(str(e)); return
            while not self.found:
                try:
                    pwd = q.get_nowait()
                except:
                    break
                try:
                    zf.extractall(pwd=pwd.encode())
                    with self.lock:
                        self.found    = True
                        self.password = pwd
                except:
                    pass
                with self.lock:
                    self.attempts += 1
                    if self.attempts % 500 == 0:
                        elapsed = __import__('time').time() - start
                        rate    = self.attempts / elapsed if elapsed > 0 else 0
                        pct     = (self.attempts / total * 100) if total else 0
                        print(f"{Colors.CYAN}[~] {self.attempts:>8,} / {total:,} "
                              f"({pct:5.1f}%)  {rate:,.0f} pwd/s{Colors.END}", end='\r')

        ts = [Thread(target=worker, daemon=True) for _ in range(threads_n)]
        for t in ts: t.start()
        for t in ts: t.join()

        elapsed = __import__('time').time() - start
        print()
        if self.found:
            self.ok(f"PASSWORD FOUND : {self.password}")
            self.ok(f"Attempts       : {self.attempts:,}")
            self.ok(f"Time           : {elapsed:.2f}s")
        else:
            self.err("Password not found in wordlist.")
            self.inf(f"Tried {self.attempts:,} passwords in {elapsed:.2f}s")

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
