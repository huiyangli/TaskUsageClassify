import os
import gzip
import shutil
import csv
import pymysql.cursors
from threading import Thread

def zero_fill(field):
    if not field:
        return '0'
    return field

def handle_file(zip_file):
    connection = pymysql.connect(host='localhost', port=3306, user='admin', password='qgk112358', db='cluster', cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    with open('log.txt', 'r') as log_file:
        log = log_file.read()
        if zip_file in log: 
            return
    with open('log.txt', 'a') as log_file:
        log_file.write(zip_file + ' start\n')
        log_file.close()
    with gzip.open('task_usage/' + zip_file, 'rb') as zipped_file:
        csv_file = csv.reader(zipped_file, delimiter=' ', quotechar=' ')
        collect = []
        for idx,row in enumerate(csv_file):
            table_name = 'job_ids_mod_' + str( int(row[2]) % 2 ) 
            row[0] = str( int( int(row[0]) / 1000 ) )
            row[1] = str( int( int(row[1]) / 1000 ) )
            
            collect.append( [table_name] + map(zero_fill, row[0].split(',')) )
            if( len(collect) >= 5000):
                print 'insert rows from %s idx %s  %s' % (zip_file, idx - 4999, idx)
                cursor.executemany('insert into %s' + 
                    '(start_time,end_time,job_id,task_index,machine_id,cpu_rate,canonical_memory_usage,assigned_memory_usage,' +
                    'unmapped_page_cache,total_page_cache,max_memory_usage,disk_io_time,local_disk_space_usage,max_cpu_rate,' +
                    'max_disk_io_time,cycles_per_instruction,memory_accesses_per_instruction,sample_portion,aggregation_type,sampled_cpu_usage) values' +
                    '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', collect) 
                connection.commit()
                collect = []
    with open('log.txt', 'a') as log_file:
        log_file.write(zip_file + ' end\n')
        log_file.close()

handle_file('part-00000-of-00500.csv.gz')

# zips = os.listdir("task_usage")

# threads = []
# index = 0
# while index < len(zips):
#     thread = Thread(target=handle_file, args=(zips[index], ))
#     thread.start()

# # join all threads
# for thread in threads:
#     thread.join()