import os
import subprocess
import argparse
import shutil
from concurrent.futures import ThreadPoolExecutor
import requests

def download_file(url, destination):
    response = requests.get(url, stream=True)
    with open(destination, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def install_dependencies():
    try:
        # Install pip if not already installed
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip"], check=True)
        # Install requests library
        subprocess.run(["pip", "install", "requests"], check=True)
        # Install other necessary dependencies
        subprocess.run(["sudo", "apt-get", "install", "-y", "john", "hash-identifier", "stegseek", "pkcrack"], check=True)

        # Create necessary directories
        os.makedirs("Jailbreak/Jailhouse/steg_result", exist_ok=True)
        os.makedirs("Jailbreak/Jailhouse/hashfile", exist_ok=True)
        os.makedirs("Jailbreak/wordlist", exist_ok=True)
        os.makedirs("Jailbreak/Freedom", exist_ok=True)

        # Define the wordlist URLs and filenames
        wordlists = {
            "rockyou.txt": "https://example.com/path/to/rockyou.txt",
            "betterrockyou.txt": "https://example.com/path/to/betterrockyou.txt",
            "brockyou++.txt": "https://example.com/path/to/brockyou++.txt"
        }

        for filename, url in wordlists.items():
            # Download each wordlist file
            print(f"Downloading {filename}...")
            download_file(url, filename)
            # Move the downloaded wordlist to the wordlist directory
            wordlist_source = filename
            wordlist_destination = f"Jailbreak/wordlist/{filename}"
            shutil.move(wordlist_source, wordlist_destination)
        
        print("Dependencies installed, directories created, and wordlists downloaded and moved successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
    except OSError as e:
        print(f"Failed to create directories or move the wordlists: {e}")
    except requests.RequestException as e:
        print(f"Failed to download wordlists: {e}")

def run_stegseek(filepath, wordlist_path, steg_result_file):
    try:
        subprocess.run(["stegseek", filepath, wordlist_path, "-o", steg_result_file], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_john(hashfile, wordlist_path, john_output_file):
    try:
        subprocess.run(["john", "--wordlist=" + wordlist_path, hashfile, "--pot=" + john_output_file], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_pkcrack(encrypted_zip, plaintext_zip, decrypted_file):
    try:
        subprocess.run(["pkcrack", "-C", encrypted_zip, "-c", "ciphertextname", "-P", plaintext_zip, "-p", "plaintextname", "-d", decrypted_file], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def process_file(args):
    filename, known_hash, known_encrypt = args['filename'], args['hash'], args['encrypt']
    try:
        filepath = os.path.join("Jailbreak/Jailhouse", filename)
        if os.path.isfile(filepath):
            steg_result_file = f"Jailbreak/Jailhouse/steg_result/{filename}_steg_result.txt"
            hashfile = f"Jailbreak/Jailhouse/hashfile/{filename}_hashfile.txt"
            john_output_file = f"Jailbreak/Freedom/{filename}_cracked.txt"
            decrypted_file = f"Jailbreak/Freedom/{filename}_decrypted.zip"

            wordlists = ["Jailbreak/wordlist/rockyou.txt", "Jailbreak/wordlist/betterrockyou.txt", "Jailbreak/wordlist/brockyou++.txt"]

            stegseek_success = False
            for wordlist in wordlists:
                if run_stegseek(filepath, wordlist, steg_result_file):
                    stegseek_success = True
                    break

            if stegseek_success or known_hash:
                if not known_hash:
                    with open(hashfile, "w") as f:
                        subprocess.run(["hash-identifier", filepath], stdout=f, check=True)

                if known_encrypt:
                    for wordlist in wordlists:
                        if run_john(hashfile, wordlist, john_output_file):
                            break

            if filename.endswith(".zip") and not known_encrypt:
                plaintext_zip = "path/to/plaintext.zip"  # Update with the actual path to the plaintext ZIP
                run_pkcrack(filepath, plaintext_zip, decrypted_file)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except OSError as e:
        print(f"OS error: {e}")

def jailbreak():
    try:
        # Clear the Freedom directory
        freedom_path = "Jailbreak/Freedom"
        if os.path.exists(freedom_path):
            shutil.rmtree(freedom_path)
        os.makedirs(freedom_path, exist_ok=True)
        
        filenames = os.listdir("Jailbreak/Jailhouse")
        
        known_info = {}
        for filename in filenames:
            print(f"What do we know about {filename}? (leave blank if unknown)")
            known_hash = input("Hash: ")
            known_encrypt = input("Encryption: ")
            known_info[filename] = {'filename': filename, 'hash': known_hash if known_hash else None, 'encrypt': known_encrypt if known_encrypt else None}

        with ThreadPoolExecutor() as executor:
            executor.map(lambda filename: process_file(known_info[filename]), filenames)
        
        print("Jailbreak process completed successfully.")
    except FileNotFoundError as e:
        print(f"Directory not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except OSError as e:
        print(f"OS error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Jailbreak program")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--execute", action="store_true", help="Execute jailbreak process")

    args = parser.parse_args()

    if args.install:
        install_dependencies()
    elif args.execute:
        jailbreak()

if __name__ == "__main__":
    main()
