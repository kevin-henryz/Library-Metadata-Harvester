import subprocess

pytest_command = ["pytest", "-n", "auto"]  

# Run the command
subprocess.run(pytest_command)
