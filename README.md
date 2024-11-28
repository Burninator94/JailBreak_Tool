JailBreak:
JailBreak is a data forensics tool designed to automate extracting and analyzing hidden/encrypted data within files. The target audience is for penetration testing, data recovery specialists, and the capture of flag participants.

Features:
Automated Dependency Installation - Single command to install full dependency list
Systematic processing: Stegseek -> HashID -> John the Ripper -> pkcrack
Escalating wordlists in rockyou.txt brockyou.txt, betterrockyou.txt, and brockyou++.txt
Autogenerating hashlists
Multiprocessing
User Input Functionality

Installation:
1. Ensure Python is installed on the system
2. Clone the repo
3. ~cd jailbreak
4. ~python jailbreak.py --install

Directory Architecture:
/
  jailbreak/
    Jailhouse/
      steg_result/ (Stores the results of the stegseek tool)
      hashfile/ (Contains hash files processed by the script.)
    wordlist/
      rockyou.txt
      betterrockyou.txt
      brockyou++.txt
    Freedom/ (Intended to hold the results of successful decryption processes)

Scheme of Operation:
  1. Install Python
  2. Install Jailbreak
  3. Load the Jailhouse directory with all targeted files
  4. Run the program
     python jailbreak.py --execute
  5. Input any known values for target files
  6. Wait for the completion message
  7. Open the Freedom directory

Files:
jailbreak.py: Main script to install dependencies and execute the Jailbreak process.

Known Issues:
Ensure the paths for wordlists and plaintext ZIP files are correctly updated in the script.
Permission errors may occur; ensure you have the necessary permissions.

Contributions:
Feel free to fork this project, submit issues, and make pull requests. Contributions are welcome!

License:
This project is licensed under the MIT License. See the LICENSE file for details.

Liability Statement
Disclaimer of Warranties and Limitation of Liability
Jailbreak Program is provided "as is" without any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. 
In no event shall the developers, contributors, or licensors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement 
of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) 
arising in any way out of the use of this software, even if advised of the possibility of such damage.

By using the Jailbreak Program, you acknowledge that you have read, understood, and agreed to this disclaimer and the associated terms and conditions. 
You are solely responsible for any actions taken based on the use of this software. The developers, contributors, and licensors do not assume any responsibility for your actions or the consequences of your actions.

User Responsibility
It is the user's responsibility to ensure compliance with all applicable laws and regulations. The Jailbreak Program is intended for educational and research purposes only. 
Unauthorized use of this software to gain unauthorized access to data or systems is strictly prohibited and may be punishable by law.
The developers, contributors, and licensors are not liable for any illegal use of this software by any user. 
