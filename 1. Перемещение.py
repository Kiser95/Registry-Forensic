import os
import shutil
for host_dir in os.scandir(r'E:\temp'): # Обход всех папок хостов
    if host_dir.is_dir():
        # Перемещение Реестра
        src_path = host_dir.path + '\C\Windows\System32\config'
        dst_path = host_dir.path + '\Reg'
        if os.path.exists(src_path):
            os.makedirs(dst_path, exist_ok=True)
            for file in os.scandir(src_path):
                shutil.move(file.path, dst_path)
        # Перемещение NTUSER
        users_folder = host_dir.path + r'\C\Users'
        if os.path.exists(users_folder):
            for user_dir in os.scandir(users_folder):
                if user_dir.is_dir():
                    for file_name in ["NTUSER.DAT", "ntuser.dat.LOG1", "ntuser.dat.LOG2"]:
                        file_path = os.path.join(user_dir.path, file_name)
                        if os.path.exists(file_path):
                            # Перемещаем файл в \NTUSER\
                            dst_folder = host_dir.path + r'\NTUSER'
                            os.makedirs(dst_folder, exist_ok=True)
                            if file_name == "NTUSER.DAT":
                                dst_file = os.path.join(dst_folder, user_dir.name + '.' + file_name.split('.')[-1])
                            else:
                                dst_file = os.path.join(dst_folder, user_dir.name + '.' + file_name.split('.')[-2].upper() + '.' + file_name.split('.')[-1])
                            shutil.move(file_path, dst_file)
        # Перемещение UsrClass
        users_folder = host_dir.path + r'\C\Users'
        if os.path.exists(users_folder):
            for user_dir in os.scandir(users_folder):
                if user_dir.is_dir():                                   
                    for file_name in ["UsrClass.dat", "UsrClass.dat.LOG1", "UsrClass.dat.LOG2"]:
                        file_path = os.path.join(user_dir.path, 'AppData\\Local\\Microsoft\\Windows\\', file_name)
                        if os.path.exists(file_path):
                            # Перемещаем файл в \UsrClass\
                            dst_folder = host_dir.path + r'\UsrClass'
                            os.makedirs(dst_folder, exist_ok=True)
                            if file_name == "UsrClass.dat":
                                dst_file = os.path.join(dst_folder, user_dir.name + '.' + file_name.split('.')[-1])
                            else:
                                dst_file = os.path.join(dst_folder, user_dir.name + '.' + file_name.split('.')[-2].upper() + '.' + file_name.split('.')[-1])
                            shutil.move(file_path, dst_file)