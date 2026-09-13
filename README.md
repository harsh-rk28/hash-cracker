# Password Security Tool

A Python-based password security tool with two modes:

## Features

### Mode 1 — Hash Cracker
Attempts to crack a hashed password using three strategies in order:
1. **Dictionary attack** — checks against 14 million real leaked passwords from the RockYou data breach (Shows live progress — words tried per second)
2. **Hashcat-style variations** — tries Hashcat-style variations of the passwords from the RockYou data breach (capitalisation, numbers, symbols)
3. **Brute force** — tries every possible character combination using itertools

Optimised performance with **multiprocessing** across 4 parallel CPU processes for faster cracking speed.

### Supported Hash Types
Auto-detected by hash length — no input needed:
- MD5 (32 chars)
- SHA1 (40 chars)  
- SHA256 (64 chars)
- SHA512 (128 chars)
  
### Mode 2 — Password Strength Analyser
Checks if your password:
- Appears in real breach data (RockYou)
- Contains uppercase letters
- Contains numbers
- Contains symbols

Gives a strength score: STRONG / MEDIUM / WEAK with specific feedback.

## Requirements
- Python 3
- Download rockyou.txt separately and place in the same folder

## Usage
```bash
python hash_cracker.py
```
