import hashlib
import time
import string
import itertools
from multiprocessing import Process, Manager

def hash_word(word, algorithm):
    word_bytes = word.encode('utf-8') #coz hashlib speaks bytes

    if algorithm == 'md5':
        return hashlib.md5(word_bytes).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(word_bytes).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(word_bytes).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(word_bytes).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

def generate_variations(word):
    variations = [word]
    
    variations.append(word.capitalize())
    variations.append(word.upper())
    variations.append(word + '123')
    variations.append(word + '1')
    variations.append(word + '!')
    variations.append(word + '@')
    variations.append(word.replace('a', '@'))
    variations.append(word.replace('o', '0'))
    variations.append(word.replace('e', '3'))
    variations.append(word.capitalize().replace('a', '@').replace('o','0').replace('e','3'))
    
    return variations

def worker(chunk, target_hash, algorithm, result, found, counter):
    for word in chunk:
        if found[0]:
            return
        word = word.strip()
        counter[0] += 1
        if hash_word(word, algorithm) == target_hash:
            result[0] = word
            found[0] = True
            return
        for variation in generate_variations(word):
            if hash_word(variation, algorithm) == target_hash:
                result[0] = variation
                found[0] = True
                return
            
# NOT BEING USED ANYWHERE - SO COMMENTED OUT 
# def crack_hash(target_hash, algorithm, wordlist_path):
#     count = 0
#      # Pass 1 - plain words only
#     print("Pass 1: Trying plain words...")
#     with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
#         for line in f:
#             word = line.strip()
#             count += 1
#             if count % 1000000 == 0:
#                 print(f"Tried {count:,} words...")
#             if hash_word(word, algorithm) == target_hash:
#                 print(f"Password found: {word}")
#                 return word

#     # Pass 2 - with variations
#     count = 0
#     print("Pass 2: Trying variations...")
#     with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
#         for line in f:
#             word = line.strip()
#             count += 1
#             if count % 1000000 == 0:
#                 print(f"Tried {count:,} words...")
#             for variation in generate_variations(word):
#                 if hash_word(variation, algorithm) == target_hash:
#                     print(f"Password found: {variation}")
#                     return variation
#     print("Password not found.")
#     return None


def brute_force(target_hash, algorithm, max_length):
    chars = string.ascii_lowercase + string.digits
    for length in range(1, max_length + 1):
        for combo in itertools.product(chars, repeat=length): 
            #itertools.product gives back tuples like ('a','b'). 
            # .join() connects them into a proper string "ab"
            word = ''.join(combo)
            if hash_word(word, algorithm) == target_hash:
                print(f"Password found: {word}")
                return word
    print("Password not found.")
    return None

def multiprocess_crack(target_hash, algorithm, wordlist_path):
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    chunk_size = len(lines) // 4
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    with Manager() as manager:
        result = manager.list([None])
        found = manager.list([False])
        counter = manager.list([0])
        
        processes = []
        for chunk in chunks:
            p = Process(target=worker, args=(chunk, target_hash, algorithm, result, found, counter))
            processes.append(p)
            p.start()
        
        start = time.time()
        while not found[0]:
            if not any(p.is_alive() for p in processes):
                break
            elapsed = time.time() - start
            speed = int(counter[0] / elapsed) if elapsed > 0 else 0
            print(f"\rTried {counter[0]:,} words | {speed:,}/sec    ", end='', flush=True)
            time.sleep(0.1) #chill for 0.1 seconds then check again

        print()
        for p in processes:
            p.terminate()
            p.join()        # join() means wait for this process to finish before moving on
        
        if result[0]:
            print(f"Password found: {result[0]}")
            return result[0]
        
        print("Password not found.")
        return None
    
def crack_hash_mode():
    print("=== Hash Cracker ===")
    target_hash = input("Enter the hash to crack: ")
    if(len(target_hash)==32):
        algorithm = 'md5'
    elif(len(target_hash)==40):
        algorithm = 'sha1'
    elif(len(target_hash)==64):
        algorithm = 'sha256'
    elif(len(target_hash)==128):
        algorithm = 'sha512'
    else:
        print("Unknown hash type")
        return
    wordlist_path = "rockyou.txt"
    
    start = time.time()
    print("Trying dictionary attack...")
    result = multiprocess_crack(target_hash, algorithm, wordlist_path)
    
    if result is None:
        print("Not found in dictionary. Trying brute force...")
        max_length = int(input("Enter max password length to try (recommended 4-6): "))
        brute_force(target_hash, algorithm, max_length)
    
    end = time.time()
    print(f"Time taken: {round(end - start, 2)} seconds")

def analyse_password_mode():
    print("=== Analyse a Password ===")
    password = input("Enter a password to analyse: ")

    print("Checking against known passwords...")
    wordlist_path = "rockyou.txt"
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if password == line.strip():
                print("WARNING: This password is in the known passwords list. It would be cracked instantly.")
                return

    length_ok = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*" for c in password)

    score = sum([length_ok, has_upper, has_digit, has_symbol])

    reasons = []
    if not length_ok:
        reasons.append("too short (use 8+ characters)")
    if not has_upper:
        reasons.append("no uppercase letters")
    if not has_digit:
        reasons.append("no numbers")
    if not has_symbol:
        reasons.append("no symbols")

    if score == 4:
        print("Verdict: STRONG - your password has good complexity")
    elif score >= 2:
        print(f"Verdict: MEDIUM - improve it by fixing: {', '.join(reasons)}")
    else:
        print(f"Verdict: WEAK - issues: {', '.join(reasons)}")


def main():
    print("=== Password Security Tool ===")
    print("1. Crack a hash")
    print("2. Analyse a password")
    choice = input("Choose an option (1/2): ")
    
    if choice == '1':
        crack_hash_mode()
    elif choice == '2':
        analyse_password_mode()
    else:
        print("Invalid option")

if __name__ == '__main__':
    main()