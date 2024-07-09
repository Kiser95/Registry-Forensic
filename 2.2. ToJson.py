import json
import os

# Исключения по полям ValueName и ValueData, для удаления
with open("value_name_to_remove.txt", "r") as file:
    value_name_to_remove = [line.strip() for line in file.readlines()]

with open("value_data_to_remove.txt", "r") as file:
    value_data_to_remove = [line.strip() for line in file.readlines()]

def remove_fields(data): # Удаление ненужных полей "DataRaw" и "Slack", если они присутствуют
    if isinstance(data, dict):
        data.pop("DataRaw", None)
        data.pop("Slack", None)
        for key, value in data.items():
            data[key] = remove_fields(value)
    elif isinstance(data, list):
        data = [remove_fields(item) for item in data]
    return data

def remove_values(data):# Удаление ненужных значений и оставление нужных (в которых может быть путь/файл)
    value_types_to_keep = ["RegSz", "RegExpandSz", "RegMultiSz"]  # Указанные типы значения оставляем
    if "Values" in data:
        values = data["Values"]
        filtered_values = [value for value in values if ((value["ValueType"] in value_types_to_keep) and (not value["ValueName"] in value_name_to_remove) and (not value["ValueData"] in value_data_to_remove) and (not (value["ValueData"].isdigit() or not value["ValueData"]))) or value["ValueName"].endswith(".sdb")]
        data["Values"] = filtered_values
    return data

def is_empty(data):    # Удаление пустых значений "Values"
    return "Values" in data and not data["Values"]

def process_json(json_data): # Исправление многовложенности словаря
    json_data = remove_fields(json_data)
    json_data = remove_values(json_data)
    
    # Если есть SubKeys, обработаем их
    if 'SubKeys' in json_data:
        subkeys = json_data['SubKeys']
        del json_data['SubKeys']
        yield json_data

        for subkey in subkeys:
            yield from process_json(subkey)

def flatten_json(data): # Убирание словарей внутри ndjson
    if "Values" in data:
        values = data["Values"]
        if len(values) == 1:
            # Если только один набор значений в Values, вставляем его в родительский словарь
            value = values[0]
            data["ValueName"] = value["ValueName"]
            data["ValueType"] = value["ValueType"]
            data["ValueData"] = value["ValueData"]
            del data["Values"]
            yield data
        else:
            # Если несколько наборов значений в Values, дублируем родительский словарь для каждого набора
            for value in values:
                new_data = data.copy()
                new_data["ValueName"] = value["ValueName"]
                new_data["ValueType"] = value["ValueType"]
                new_data["ValueData"] = value["ValueData"]
                del new_data["Values"]
                yield new_data

def process_registry_file(input_file): # Основная функция открытия и обработки
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    filtered_data = [entry for entry in process_json(data) if not is_empty(entry)]
    flattened_data = [new_entry for entry in filtered_data for new_entry in flatten_json(entry)]

    return flattened_data

def main(input_directory):
    for dir_name in os.listdir(input_directory): # Перебор поддиректорий в указанной директории (Имена хостов)
        dir_path = os.path.join(input_directory, dir_name)
        if os.path.isdir(dir_path):
            registry_data = [] # Обнуление общего json фрейма

            for root, dirs, files in os.walk(dir_path): # Перебор файлов в текущей поддиректории (Файлы веток реестра)
                for file in files:
                    if file.startswith("Reg-"): # Поиск только файлов с реестром
                        registry_file = os.path.join(root, file)    
                        registry_data_temp = process_registry_file(registry_file) # json фрейм для определенного файла (для корректной замены ROOT)
                        
                        # Замена ROOT на соответствующее значение куста реестра
                        if file.startswith("Reg-Software"):
                            for entry in registry_data_temp:
                                entry["KeyPath"] = entry["KeyPath"].replace("ROOT", "Software")
                        elif file.startswith("Reg-System"):
                            for entry in registry_data_temp:
                                entry["KeyPath"] = entry["KeyPath"].replace("ROOT", "System")                        
                        elif file.startswith("Reg-Ntuser"):
                            username_start = file.find("Reg-Ntuser-") + len("Reg-Ntuser-")
                            username_end = file.find("%5C", username_start)
                            username = file[username_start:username_end]
                            for entry in registry_data_temp:
                                entry["KeyPath"] = entry["KeyPath"].replace("ROOT", f"NTUSER.DAT-{username}") 
                        elif file.startswith("Reg-UsrClass-"):
                            username_start = file.find("Reg-UsrClass-") + len("Reg-UsrClass-")
                            username_end = file.find("%5C", username_start)
                            username = file[username_start:username_end]
                            for entry in registry_data_temp:
                                entry["KeyPath"] = f"UsrClass-{username}-" + entry["KeyPath"]
                        
                        registry_data += registry_data_temp # Добавлнение скорректированного json фрейма в общий
                        os.remove(registry_file) # Удаление обработанных файлов

            output_file = os.path.join(dir_path, "Registry.json") # Создание отдельного Registry.json в директории хоста
            with open(output_file, 'w', encoding='utf-8') as out_file:
                for entry in registry_data:
                    # Запись каждого объекта JSON на новой строке
                    json.dump(entry, out_file, ensure_ascii=False, separators=(',', ':'))
                    out_file.write('\n')

if __name__ == "__main__":
    input_directory = r'E:\temp\ToElastic'  # Папка, в которой находятся файлы для обработки
    main(input_directory)