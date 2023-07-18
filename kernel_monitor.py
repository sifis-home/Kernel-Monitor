import os
import signal
import subprocess
import sys
import time
from collections import defaultdict

from send_data import send_data

data_dict = defaultdict(int)
last_update_time = time.time()
p = None  # Variabile globale per il processo subprocess


def handle_timeout(signum, frame):
    # gestione del timeout
    print("Timeout!")
    # os.killpg(os.getpgid(p.pid), signal.SIGINT)


def receive_data(data):
    print("Receiving DATA")
    global last_update_time, data_dict
    data["timestamp"]
    syscall = data["syscall"]
    syscall = syscall.split("(")[0]
    print(syscall)
    print("\n\n")

    if syscall is not None:
        data_dict[syscall] += 1

    if time.time() - last_update_time >= 3 or "+++ exited with" in syscall:
        print(data_dict)
        send_data(data_dict)
        print("Data Sent")

        data_dict = defaultdict(int)
        last_update_time = time.time()

    return "Data received"


def main():
    global p  # Dichiarazione di p come variabile globale
    print("Start Capturing Syscalls\n\n")

    file = os.environ.get("ARGUMENT") or sys.argv[1]
    file = [str(file)]
    print(file)
    for line in file:
        line = line.strip()
        print(f"Capturing syscalls for {line}...")
        signal.signal(
            signal.SIGALRM, handle_timeout
        )  # impostazione dell'handler per il segnale di timeout
        signal.alarm(5)  # timeout di 5 secondi
        # Start the strace command as a subprocess
        if "/" not in line:
            p = subprocess.Popen(
                ["strace", f"/usr/bin/{line}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
        else:
            p = subprocess.Popen(
                ["strace", line],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
        try:
            # Read the output from the subprocess in real-time and send it to the server
            while True:
                output = p.stderr.readline()
                if not output:
                    break
                timestamp = time.time()
                syscall = output.decode("utf-8").strip()
                print(line + ": " + syscall)
                data = {"timestamp": timestamp, "syscall": syscall}
                receive_data(data)
        except KeyboardInterrupt:
            # L'utente ha premuto Ctrl+C, interrompi l'esecuzione
            pass
        except TimeoutError:
            # Si è verificato un timeout, continua l'esecuzione senza chiudere il programma
            pass
        finally:
            signal.alarm(0)  # cancella il timeout
            os.killpg(
                os.getpgid(p.pid), signal.SIGINT
            )  # Invia un segnale di interruzione al gruppo di processi della subprocess
        # Wait for the subprocess to finish and send any remaining output to the server
        remaining_output = p.communicate()[0].decode("utf-8")
        for syscall in remaining_output.split("\n"):
            if syscall:
                timestamp = time.time()
                data = {"timestamp": timestamp, "syscall": syscall}
                receive_data(data)

        print(f"Finished capturing syscalls for {line}")


if __name__ == "__main__":
    main()
