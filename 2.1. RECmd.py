import os
import subprocess
from pathlib import Path

# Список ключей реестра, которые нужно парсить
registry_keys_software = [
    "Classes",
    "Microsoft\\Active Setup\\Installed Components",
    "Microsoft\\Command Processor\\Autorun",
    "Microsoft\\Ctf\\LangBarAddin",
    "Microsoft\\Internet Explorer\\Extensions",
    "Microsoft\\Netsh",
    "Microsoft\\Office",
    "Microsoft\\Office test\\Special\\Perf",
    "Microsoft\\Windows CE Services\\AutoStartOnConnect\\MicrosoftActiveSync",
    "Microsoft\\Windows CE Services\\AutoStartOnDisconnect\\MicrosoftActiveSync",
    "Microsoft\\Windows NT\\CurrentVersion",
    "Microsoft\\Windows\\CurrentVersion",
    "Microsoft\\Windows\\Windows Error Reporting\\Hangs\\ReflectDebugger",
    "Policies\\Microsoft\\Windows\\Control Panel\\Desktop",
    "Policies\\Microsoft\\Windows\\System\\Scripts",
    "Wow6432Node\\Microsoft\\Windows\\CurrentVersion",
    "Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion"
]

registry_keys_system = [
    "ControlSet001\\Control\\BootVerificationProgram",
    "ControlSet001\\Control\\Lsa\\Notification Packages",
    "ControlSet001\\Control\\Lsa\\OSConfig\\Security Packages",
    "ControlSet001\\Control\\Lsa\\Security Packages",
    "ControlSet001\\Control\\NetworkProvider\\Order",
    "ControlSet001\\Control\\Print\\Environments",
    "ControlSet001\\Control\\Print\\Monitors",
    "ControlSet001\\Control\\SafeBoot\\AlternateShell",
    "ControlSet001\\Control\\ServiceControlManagerExtension",
    "ControlSet001\\Control\\Session Manager",
    "ControlSet001\\Control\\Terminal Server\\Wds\\rdpwd\\StartupPrograms",
    "ControlSet001\\Control\\Terminal Server\\WinStations\\RDP-Tcp\\InitialProgram",
    "ControlSet001\\Services",
    "Setup\\CmdLine"
]

registry_keys_ntuserdat = [
    "Software\\Microsoft",
    "Software\\Policies\\Microsoft\\Windows\\System\\Scripts",
    "Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion",
    "Software\\Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion",
    "System\\CurrentControlSet\\Control",
    "System\\CurrentControlSet\\Services",
    "System\\Setup\\CmdLine",
    "Environment",
    "Control Panel\\Desktop"
]

registry_keys_usrclassdat = [
    "ROOT"
]

base_dir = Path('E:/temp') # Базовая папка, где все лежит
reg_dir_name = 'Reg' # В какой папке искать кусты реестра хоста
ntuser_dir_name = 'NTUSER' # В какой папке искать кусты реестра пользователей
usrclass_dir_name = 'UsrClass'
special_regs = ['SOFTWARE', 'SYSTEM']  # Какие кусты реестра хоста парсить

# Обход поддиректорий базовой директории
for host_dir in base_dir.iterdir(): # подкаталог - имя хоста
    if host_dir.is_dir():
        host_name = host_dir.name
        reg_dir = host_dir / reg_dir_name # Поиск папки кустов реестра хоста
        ntuser_dir = host_dir / ntuser_dir_name # Поиск папки кустов реестра пользователя
        usrclass_dir = host_dir / usrclass_dir_name
        if reg_dir.exists():
            for reg_name in special_regs: # Обход software и system
                reg_file = reg_dir / reg_name 
                if reg_file.exists():
                    output_dir = base_dir / 'ToElastic' / host_name # Определение директории куда сливать результаты (закрепеление за именем хоста)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    if reg_name == "SOFTWARE": # Парсинг Software
                       for key in registry_keys_software: # Только нужные ветки реестра
                            json_file_name = key.replace('\\', '%5C').replace(' ', '') # Замена плохих символов, мешающих работе

                            # Запуск команды RECmd.exe
                            cmd = (
                                f'E:/Scripts/2.Reg/RECmd.exe -f "{str(reg_file)}" --kn "{key}" --details --json "{output_dir}" --jsonf "Reg-Software%5C{str(json_file_name)}.json"'
                            )
                            with open(os.devnull, 'w') as FNULL:
                                subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=FNULL)
                    if reg_name == "SYSTEM": # Аналогично Software
                        for key in registry_keys_system: # Только нужные ветки реестра
                            json_file_name = key.replace('\\', '%5C').replace(' ', '')
                            cmd = (
                                f'E:/Scripts/2.Reg/RECmd.exe -f "{str(reg_file)}" --kn "{key}" --details --json "{output_dir}" --jsonf "Reg-System%5C{str(json_file_name)}.json"'
                            )
                            with open(os.devnull, 'w') as FNULL:
                                subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=FNULL)
        if ntuser_dir.exists(): # Обход кустов реестра пользователей
            for ntuser_file in ntuser_dir.iterdir():
                if ntuser_file.is_file() and not ntuser_file.name.endswith(("LOG1", "LOG2")): # Не обходить требующиеся для парсинга .dat.LOG
                    output_dir = base_dir / 'ToElastic' / host_name # Определение директории куда сливать результаты (закрепеление за именем хоста)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    for key in registry_keys_ntuserdat: # Только нужные ветки реестра
                        json_file_name = f"Reg-Ntuser-{ntuser_file.stem}" # Определение имени нового файла, для сохранения имени пользователя
                        json_file_name = json_file_name.replace('.dat', '') + "%5C"
                        json_file_name += key.replace('\\', '%5C').replace(' ', '')

                        # Запуск команды RECmd.exe
                        cmd = (
                            f'E:/Scripts/2.Reg/RECmd.exe -f "{str(ntuser_file)}" --kn "{key}" --details --json "{output_dir}" --jsonf "{json_file_name}.json"'
                        )
                        with open(os.devnull, 'w') as FNULL:
                            subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=FNULL)

        if usrclass_dir.exists(): # Обход кустов реестра пользователей
            for usrclass_file in usrclass_dir.iterdir():
                if usrclass_file.is_file() and not usrclass_file.name.endswith(("LOG1", "LOG2")): # Не обходить требующиеся для парсинга .dat.LOG
                    output_dir = base_dir / 'ToElastic' / host_name # Определение директории куда сливать результаты (закрепеление за именем хоста)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    for key in registry_keys_usrclassdat: # Только нужные ветки реестра
                        json_file_name = f"Reg-UsrClass-{usrclass_file.stem}" # Определение имени нового файла, для сохранения имени пользователя
                        json_file_name = json_file_name.replace('.dat', '') + "%5C"
                        json_file_name += key.replace('\\', '%5C').replace(' ', '')

                        # Запуск команды RECmd.exe
                        cmd = (
                            f'E:/Scripts/2.Reg/RECmd.exe -f "{str(usrclass_file)}" --kn "{key}" --details --json "{output_dir}" --jsonf "{json_file_name}.json"'
                        )
                        with open(os.devnull, 'w') as FNULL:
                            subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=FNULL)