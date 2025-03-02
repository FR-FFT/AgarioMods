import os
import glob
import subprocess

# 🔍 Find the first .ipa file in the current directory
ipa_files = glob.glob("*.ipa")

if not ipa_files:
    print("❌ No .ipa files found!")
    exit(1)

ipa_file = ipa_files[0]  # Take the first found .ipa file
print(f"✅ Found IPA file: {ipa_file}")

# 🔄 Rename file (optional, to avoid issues with spaces)
safe_name = "safe.ipa"
os.rename(ipa_file, safe_name)
print(f"🔄 Renamed {ipa_file} → {safe_name}")

# 🛠 Check file type
file_type = subprocess.run(["file", safe_name], capture_output=True, text=True)
print(f"📂 File type: {file_type.stdout.strip()}")

# 📦 Unzip the .ipa file
unzip_result = subprocess.run(["unzip", safe_name], capture_output=True, text=True)

if unzip_result.returncode == 0:
    print("✅ Unzipped successfully!")
else:
    print(f"❌ Unzip failed!\n{unzip_result.stderr}")
    exit(1)
