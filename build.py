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
    ]  + [main_script]

    # Print command for debugging
    print("Running command:", " ".join(pyinstaller_command))

    # Adjusting command execution based on OS
    if platform.system() == 'Windows':
        # In Windows, directly pass the command list
        subprocess.run(pyinstaller_command)
    elif platform.system() in ['Darwin', 'Linux']:
        # Unix-like systems, need to use shell=True
        subprocess.run(' '.join(pyinstaller_command), shell=True, check=True, executable='/bin/bash')
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    build()
