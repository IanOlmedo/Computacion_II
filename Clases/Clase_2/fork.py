import os

pid = os.fork()
if pid == 0:
    print("[HIJO] PID:", os.getpid(), "PPID:", os.getppid())
else:
    print("[PADRE] PID:", os.getpid(), "Hijo:", pid)
