"""
BPJS AUTOMATION - AUTO SETUP
Jalankan file ini sekali saja untuk setup
"""

import os
import sys

def main():
    print("="*50)
    print("BPJS AUTOMATION - AUTO SETUP")
    print("="*50)
    
    # Install dependencies
    print("\n1. Installing dependencies...")
    os.system(f"{sys.executable} -m pip install kivy pyjnius")
    
    # Create folders
    print("\n2. Creating folders...")
    folders = ["logs", "exports", "backups"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"   Created: {folder}/")
    
    # Check config
    print("\n3. Checking configuration...")
    if os.path.exists("config.py"):
        with open("config.py", "r") as f:
            content = f.read()
            if "sipp.bpjs.go.id" in content:
                print("   ⚠️  URL masih default, edit di config.py jika perlu")
            else:
                print("   ✅ URL sudah dikustomisasi")
    else:
        print("   ❌ config.py tidak ditemukan")
    
    # Final message
    print("\n" + "="*50)
    print("SETUP SELESAI!")
    print("\nNEXT STEPS:")
    print("1. Edit URL di config.py (jika perlu)")
    print("2. Jalankan: python main.py")
    print("3. Input KPJ, klik START, export CSV")
    print("="*50)

if __name__ == "__main__":
    main()