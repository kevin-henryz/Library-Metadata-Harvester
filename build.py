import os
import platform
import subprocess

def build():
   
    main_script = os.path.join('src', 'app.py')
    src_path = os.path.join(os.getcwd(), 'src')  # Assumes the build script is at the root of the project
    paths_arg = '--paths=' + src_path

    # Base PyInstaller command
    pyinstaller_command = [
        'pyinstaller',
        '--clean',  # Clean PyInstaller cache and remove temporary files before building
        '--onefile',  # Package the app into one file
        '--windowed',  # Windowed mode, no console
        paths_arg, 
        main_script  
    ]

    # Run the command
    if platform.system() in ['Windows', 'Darwin', 'Linux']:
        subprocess.run(pyinstaller_command, shell=True)  # Using subprocess.run for better process handling
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    build()
