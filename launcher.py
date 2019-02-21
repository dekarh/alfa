import os, psutil, sys, time,subprocess

has_launcher = False
pid_launcher = os.getpid()

for p in psutil.process_iter():
    if p.name() == 'python3' and 'launcher.py' in ' '.join(p.cmdline()) and p.pid != pid_launcher:
        #print(p.name(), ' '.join(p.cmdline()), p.pid)
        sys.exit()          # проверяем наличие второго launch_abalancer.py, если есть - выходим

abalancer = os.path.join(os.path.dirname(__file__), "abalancer.py")

i = 0
while i == 0:
    has_abalancer = False
    for p in psutil.process_iter():
        if p.name() == 'python3' and 'launcher.py' in ' '.join(p.cmdline()) and p.pid != pid_launcher:
            sys.exit()  # проверяем наличие второго launch_abalancer.py, если есть - выходим
        if ('abalancer.py' in p.name() or 'abalancer.py' in ' '.join(p.cmdline())):
            has_abalancer = True
            break
    if has_abalancer: # если в процессах есть abalancer.py
        time.sleep(0.5)
    else:
        subprocess.Popen([sys.executable, abalancer])



# переместить в abalancer
