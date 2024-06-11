#!/usr/bin/env python3

import os
import subprocess
from requests_tor import RequestsTor

requests = RequestsTor(tor_ports=(9050,), tor_cport=9051)

url = "http://threeamkelxicjsaf2czjyz2lc4q3ngqkxhhlexyfcp2o6raw4rphyad.onion/"
r = requests.get(url)

print(r.text)

save_directory = os.path.expanduser('/mnt/hgfs/tortext')
file_name = 'threeamk.txt' 
file_path = os.path.join(save_directory, file_name)

counter = 1
while os.path.exists(file_path):
    base_name = f"tor_output{counter}.txt"
    file_path = os.path.join(save_directory, base_name)
    counter += 1

with open(file_path, 'w', encoding='utf-8') as file:
    file.write(r.text)

subprocess.run(['subl', file_path])

print(f"'{file_path}' has been opened in Sublime Text.")
