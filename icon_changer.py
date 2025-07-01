#!/usr/bin/env python3
"""
Author: Syphonetic
"""
import argparse
import os
import sys
import shutil
import subprocess
from PIL import Image

def convert_to_ico(image_path: str, ico_path: str):
    """Generate a multi-resolution ICO from an image."""
    im = Image.open(image_path)
    sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
    im.save(ico_path, format='ICO', sizes=sizes)
    print(f"[+] Generated ICO: {ico_path}")

def replace_icon(input_exe: str, ico_path: str, output_exe: str, reshack_path: str, mask_value: str):
    """Copy EXE and replace its icon using Resource Hacker, with optional fallback."""
    shutil.copy2(input_exe, output_exe)
    print(f"[+] Copied original binary to: {output_exe}")

    def run_mask(mask):
        cmd = [
            reshack_path,
            "-open", output_exe,
            "-save", output_exe,
            "-action", "addoverwrite",
            "-res", ico_path,
            "-mask", mask
        ]
        print(f"[+] Running Resource Hacker with mask '{mask}': {' '.join(cmd)}")
        subprocess.check_call(cmd)
        print(f"[+] Icon replaced via Resource Hacker CLI using mask '{mask}'")

    try:
        run_mask(mask_value)
    except subprocess.CalledProcessError:
        fallback = None
        if mask_value.startswith("ICONGROUP,1"):
            fallback = mask_value.replace("1", "MAINICON", 1)
        if fallback:
            print("[!] Default mask failed, retrying with PyInstaller stub mask...")
            try:
                run_mask(fallback)
                return
            except subprocess.CalledProcessError as e:
                print(f"[-] Fallback mask also failed: {e}")
        print("[-] Resource Hacker failed to replace icon with any mask.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Post-build icon replacement for Windows PE executables.")
    parser.add_argument('--image', required=True, help='Source image (PNG, JPG)')
    parser.add_argument('--binary', required=True, help='Path to compiled EXE')
    parser.add_argument('--output', help='Patched EXE path (default: <orig>_patched.exe)')
    parser.add_argument('--reshack', help='Path to ResourceHacker.exe (default: ResourceHacker.exe)')
    parser.add_argument('--mask', help='Resource Hacker mask string (default: "ICONGROUP,1,0x0409")')
    args = parser.parse_args()

    for path_attr in ('image', 'binary'):
        path = getattr(args, path_attr)
        if not os.path.isfile(path):
            print(f"[-] {path_attr.capitalize()} not found: {path}")
            sys.exit(1)

    reshack_exe = args.reshack or 'ResourceHacker.exe'
    if not os.path.isfile(reshack_exe):
        print(f"[-] ResourceHacker.exe not found at {reshack_exe}")
        sys.exit(1)

    output_exe = args.output or f"{os.path.splitext(args.binary)[0]}_patched{os.path.splitext(args.binary)[1]}"
    temp_ico = os.path.join(os.path.dirname(output_exe), 'temp_icon.ico')
    mask_value = args.mask or "ICONGROUP,1,0x0409"

    convert_to_ico(args.image, temp_ico)
    replace_icon(args.binary, temp_ico, output_exe, reshack_exe, mask_value)

    try:
        os.remove(temp_ico)
    except OSError:
        pass

if __name__ == '__main__':
    main()
