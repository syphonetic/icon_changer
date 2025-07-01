# icon_changer
A tool to convert an image to ICO and replace a Windows PE binary's icon post-build using Resource Hacker CLI.

Dependencies:
  - Pillow: pip install pillow
  - Resource Hacker CLI (ResourceHacker.exe):
      Download from: https://www.angusj.com/resourcehacker/
      Place ResourceHacker.exe in the same folder or provide its path via --reshack.

Usage:
  `python icon_changer.py --image new.png --binary app.exe [--output patched.exe] [--reshack path/to/ResourceHacker.exe] [--mask "ICONGROUP,1,0x0409"]`
  
What it does:
  1. Generates a multi-resolution ICO file (temp_icon.ico) from the provided image.
  2. Copies the original compiled EXE to the output path.
  3. Uses Resource Hacker CLI to overwrite the icon resources (ICONGROUP) in the copied EXE.
     If the default mask fails (common with PyInstaller stubs), it automatically retries with the
     "MAINICON" group name.
  4. Cleans up the temporary ICO file.
