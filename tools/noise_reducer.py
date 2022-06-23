from scipy.io import wavfile
import os
import noisereduce as nr

def process_file(file_name):
    """
    A function that process files into training dataset.
    This function reduces noise and then splits each chunks of letters or numbers.
    Then each chunks will be classified by human.
    :param file_name: file name to process
    """
    rate, data = wavfile.read(file_name)
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    noise_reduced_path = os.path.join(os.getcwd(), "noise_reduced")
    try:
        wavfile.write("./noise_reduced/" + file_name, rate, reduced_noise)
    except FileNotFoundError:
        os.mkdir(noise_reduced_path)
        wavfile.write("./noise_reduced/" + file_name, rate, reduced_noise)


import os

directory = os.fsencode(os.getcwd())

for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".wav"): 
         process_file(filename)
         print("[+] Processed : " + filename)
         continue
     else:
         continue
