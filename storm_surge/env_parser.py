import sys
import os
import struct
import numpy as np

def swap16(i):												# switch endianness of 16-bit integer
    return struct.unpack("<H", struct.pack(">H", i))[0]
def swap32(i):												# switch endianness of 32-bit integer
    return struct.unpack("<I", struct.pack(">I", i))[0]

def main():
    print("Starting parsing.")
    bytes_per_data = 2										# each data point takes 2 bytes
    script_dir = os.path.dirname(__file__) 					# absolute path of the script
    rel_path = sys.argv[1]									# relative path of the envelope file
    abs_file_path = os.path.join(script_dir, rel_path)		# absolute path of the envelope file
    input_file = open(abs_file_path,'rb').read()			# read in as raw bytes

    env_message = input_file[8:168]							# get environment message
    print("Environment message: " + env_message)

    jmxb = swap32(int(input_file[4:8].encode('hex'), 16))	# get jmxb (num columns)
    imxb = swap32(int(input_file[0:4].encode('hex'), 16))	# get imxb (num rows)
    num_data_points = jmxb * imxb
    print("jmxb: " + repr(jmxb))
    print("imxb: " + repr(imxb))
    print("num_data_points: " + repr(num_data_points))
    
    starting_byte = 168										# data points start at byte 168

    array = np.zeros(shape=(imxb,jmxb))						# declare numpy array

    for j in range(0, jmxb): 								# iterate over all columns
    	jmxbOffset = (j * imxb * bytes_per_data)
    	for i in range(0, imxb):							# iterate over all rows
    		start = starting_byte + jmxbOffset + (i*2)
    		upto = starting_byte + jmxbOffset + (i*2) + 2
    		data_point = swap16(int(input_file[start:upto].encode('hex'), 16))
    		array[i][j] = data_point

    print("Done parsing.")
    print array

if __name__ == '__main__':
    main()