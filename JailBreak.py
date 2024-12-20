import os
import subprocess
import argparse
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
import requests
import logging

# Configure logging process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Downloaded {url} to {destination}")
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")

def install_dependencies():
    try:
        # Install pip if not already installed
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip"], check=True)
        logging.info("Installed python3-pip")
        
        # Install requests library
        subprocess.run(["pip3", "install", "requests"], check=True)
        logging.info("Installed requests library")
        
        # Install john and hash-id
        subprocess.run(["sudo", "apt-get", "install", "-y", "john", "hash-identifier"], check=True)
        logging.info("Installed john and hash-identifier")
        
        # Install stegseek
        stegseek_repo = "https://github.com/RickdeJager/stegseek"
        subprocess.run(["sudo", "git", "clone", stegseek_repo], check=True)
        os.chdir("stegseek")
        subprocess.run(["sudo", "make"], check=True)
        subprocess.run(["sudo", "make", "install"], check=True)
        os.chdir("..")
        shutil.rmtree("stegseek")
        logging.info("Installed stegseek")
        
        # Install pkcrack
        pkcrack_repo = "https://github.com/keyunluo/pkcrack"
        subprocess.run(["sudo", "git", "clone", pkcrack_repo], check=True)
        os.chdir("pkcrack")
        subprocess.run(["sudo", "make"], check=True)
        subprocess.run(["sudo", "make", "install"], check=True)
        os.chdir("..")
        shutil.rmtree("pkcrack")
        logging.info("Installed pkcrack")
        
        # Create necessary directories
        os.makedirs("Jailbreak/Jailhouse/steg_result", exist_ok=True)
        os.makedirs("Jailbreak/Jailhouse/hashfile", exist_ok=True)
        os.makedirs("Jailbreak/wordlist", exist_ok=True)
        os.makedirs("Jailbreak/Freedom", exist_ok=True)
        logging.info("Created necessary directories")

        # Define the wordlist URLs and filenames
        wordlists = {
            "rockyou.txt": "https://github.com/ohmybahgosh/RockYou2021.txt",
            "betterrockyou.txt": "https://github.com/Leminee/BetterRockyou",
        }

        for filename, url in wordlists.items():
            logging.info(f"Downloading {filename} from {url}")
            download_file(url, filename)
            
            # Move the downloaded wordlist to the wordlist directory
            wordlist_source = filename
            wordlist_destination = f"Jailbreak/wordlist/{filename}"
            shutil.move(wordlist_source, wordlist_destination)
            logging.info(f"Moved {filename} to {wordlist_destination}")
        
        logging.info("Dependencies installed, directories created, and wordlists downloaded and moved successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
    except OSError as e:
        logging.error(f"Failed to create directories or move the wordlists: {e}")

def run_stegseek(filepath, wordlist_path, steg_result_file):
    try:
        subprocess.run(["stegseek", filepath, wordlist_path, "-o", steg_result_file], check=True)
        logging.info(f"Ran stegseek on {filepath} with wordlist {wordlist_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run stegseek on {filepath}: {e}")
        return False

def run_john(hashfile, wordlist_path, john_output_file):
    try:
        subprocess.run(["john", "--wordlist=" + wordlist_path, hashfile, "--pot=" + john_output_file], check=True)
        logging.info(f"Ran john on {hashfile} with wordlist {wordlist_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run john on {hashfile}: {e}")
        return False

def create_plaintext_archive(plaintext_file, plaintext_zip):
    try:
        shutil.make_archive(plaintext_zip, 'zip', os.path.dirname(plaintext_file), os.path.basename(plaintext_file))
        logging.info(f"Created plaintext archive {plaintext_zip}.zip from {plaintext_file}")
        return True
    except OSError as e:
        logging.error(f"Failed to create plaintext archive: {e}")
        return False

def run_pkcrack(encrypted_zip, encrypted_file, plaintext_zip, plaintext_file, decrypted_file):
    try:
        subprocess.run(["pkcrack", "-C", encrypted_zip, "-c", encrypted_file, "-P", plaintext_zip, "-p", plaintext_file, "-d", decrypted_file], check=True)
        logging.info(f"Ran pkcrack on {encrypted_zip} with plaintext {plaintext_file}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run pkcrack on {encrypted_zip}: {e}")
        return False

def extract_files_from_zip(zip_path, extract_dir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logging.info(f"Extracted files from {zip_path} to {extract_dir}")
    except zipfile.BadZipFile as e:
        logging.error(f"Failed to extract files from {zip_path}: {e}")

def process_file(args):
    filename, known_hash, known_encrypt = args['filename'], args['hash'], args['encrypt']
    try:
        filepath = os.path.join("Jailbreak/Jailhouse", filename)
        if os.path.isfile(filepath):
            if zipfile.is_zipfile(filepath):
                extract_dir = f"Jailbreak/Jailhouse/Courtyard/{filename}"
                os.makedirs(extract_dir, exist_ok=True)
                extract_files_from_zip(filepath, extract_dir)

                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        steg_result_file = f"{file_path}_steg_result.txt"
                        hashfile = f"{file_path}_hashfile.txt"
                        john_output_file = f"Jailbreak/Freedom/{file}_cracked.txt"
                        decrypted_file = f"Jailbreak/Freedom/{file}_decrypted.zip"

                        wordlists = ["Jailbreak/wordlist/rockyou.txt", "Jailbreak/wordlist/betterrockyou.txt"]

                        stegseek_success = False
                        for wordlist in wordlists:
                            if run_stegseek(file_path, wordlist, steg_result_file):
                                stegseek_success = True
                                break

                        if stegseek_success or known_hash:
                            if not known_hash:
                                with open(hashfile, "w") as f:
                                    subprocess.run(["hash-identifier", file_path], stdout=f, check=True)
                                    logging.info(f"Identified hash for {file_path}")

                            if known_encrypt:
                                for wordlist in wordlists:
                                    if run_john(hashfile, wordlist, john_output_file):
                                        break

                        if file.endswith(".zip") and not known_encrypt:
                            plaintext_zip = "Jailbreak/known_plaintext/plaintext.zip"  # Update with the actual path to the known plaintext ZIP
                            plaintext_file = "plaintextfile.txt"  # Update with the actual plaintext file name
                            if create_plaintext_archive(plaintext_file, plaintext_zip):
                                run_pkcrack(file_path, plaintext_file, plaintext_zip, plaintext_file, decrypted_file)
            else:
                # Process the file as before
                steg_result_file = f"Jailbreak/Jailhouse/steg_result/{filename}_steg_result.txt"
                hashfile = f"Jailbreak/Jailhouse/hashfile/{filename}_hashfile.txt"
                john_output_file = f"Jailbreak/Freedom/{filename}_cracked.txt"
                decrypted_file = f"Jailbreak/Freedom/{filename}_decrypted.zip"

                wordlists = ["Jailbreak/wordlist/rockyou.txt", "Jailbreak/wordlist/betterrockyou.txt"]

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
                    plaintext_zip = "Jailbreak/known_plaintext/plaintext.zip"  # Update with the actual path to the known plaintext ZIP
                    plaintext_file = "plaintextfile.txt"  # Update with the actual
                    if create_plaintext_archive(plaintext_file, plaintext_zip):
                        run_pkcrack(filepath, plaintext_file, plaintext_zip, plaintext_file, decrypted_file)
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
