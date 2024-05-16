import subprocess
import sys

script_path = "Worker.py"
num_processes = 4


def run_mpi_script(script_path, num_processes):
    command = ['mpiexec', '--oversubscribe', '-n', str(num_processes), 'python3', script_path]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit()

if __name__ == "__main__":
    run_mpi_script(script_path, num_processes)