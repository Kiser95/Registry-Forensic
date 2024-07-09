import os
import json
import jsonlines
from datetime import datetime, timedelta

def process_registry_file(file_path):
    updated_data = []
    with jsonlines.open(file_path, 'r') as reader:
        for entry in reader: # Переименование полей для выгрузки в ELK
            entry["reg.key.path"] = entry.pop("KeyPath")
            entry["reg.key.name"] = entry.pop("KeyName")
            timestamp = entry["LastWriteTimestamp"]
            timestamp = int(timestamp[6:-2]) / 1000 # Получение числа секунд из строки времени
            timestamp = datetime.fromtimestamp(timestamp) - timedelta(hours=3) # UTC-3
            entry["@timestamp"] = timestamp.strftime('%Y-%m-%dT%H:%M:%S') # Формат, понятный ELK
            entry.pop("LastWriteTimestamp")
            entry["file.name"] = entry.pop("ValueName")
            entry["file.path"] = entry.pop("ValueData")
            entry.pop("ValueType")
            updated_data.append(entry)
    return updated_data

def split_json_file(input_file, chunk_size): # Разделение на несколько json файлов
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = [json.loads(line) for line in infile]
    total_records = len(data)
    num_chunks = (total_records + chunk_size - 1) // chunk_size # Определение на сколько частей разделять
    for i in range(num_chunks): # Создание ограниченных файлов json
        input_file_temp = input_file.replace('.json', '')
        output_file = f"{input_file_temp}{i + 1}.json"
        start = i * chunk_size
        end = (i + 1) * chunk_size
        chunk_data = data[start:end]
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for item in chunk_data:
                outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

def process_directory(directory_path, chunk_size): # Проверка необходимости разделения на блоки
    for root, dirs, files in os.walk(directory_path): # Поиск всех файлов обработанного реестра
        for filename in files:
            if filename == 'Registry.json':
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    line_count = sum(1 for line in file)
                if line_count > chunk_size: # Нужно ли разделять
                    split_json_file(file_path, chunk_size)
                    os.remove(file_path)

def main(input_directory, chunk_size):
    for root, dirs, files in os.walk(input_directory): # Поиск всех файлов обработанного реестра
        for file in files:
            if file == "Registry.json":
                registry_file = os.path.join(root, file)
                updated_data = process_registry_file(registry_file) # Переименование полей
                with jsonlines.open(registry_file, 'w') as writer:
                    writer.write_all(updated_data)
                process_directory(root, chunk_size) # Разделение на блоки 

if __name__ == "__main__":
    input_directory = r'E:\temp\ToElastic'
    chunk_size = 100000 # По сколько строк разделять json-файлы, для корректной выгрузки в ELK
    main(input_directory, chunk_size)