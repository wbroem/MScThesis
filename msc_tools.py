import pandas as pd
import os
import time

#TODO: make the mast_data_path a parameter in the function call so that other people can use this on their machine
mast_data_path = '/Users/waderoemer/Desktop/MScThesis/MAST_data'

kids_data = pd.read_csv('KiDS_lenses.csv',skiprows=7)

def download_tpf_from_mast(ra,dec):
    curl_cmd = f'curl -O "https://mast.stsci.edu/tesscut/api/v0.1/astrocut?ra={ra}&dec={dec}&y=5&x=5"'
    filename = f'{mast_data_path}/astrocut\?ra={ra}\&dec={dec}\&y=5\&x=5' #absolute path to the file
    
    #fetch the data from MAST using a cURL command
    os.system('cd MAST_data\n' + curl_cmd)
    
    #append '.zip' to the filename, otherwise the computer doesn't know how to handle the file
    os.system(f'mv {filename} {filename}.zip')
    
    #decompress the .zip file
    os.system(f'cd MAST_data\n unzip {filename}.zip')
    time.sleep(3) # let's try not to get blacklisted by MAST... 

    
def get_all_mast_data():
    for i in range(len(kids_data)):
        ra = kids_data['RA'][i]
        dec = kids_data['DEC'][i]
        download_tpf_from_mast(ra,dec)

def remove_zip_files():
    zipfiles = []
    for file in os.listdir(mast_data_path):
        if file.endswith('.zip'):
            zipfiles.append(file)
    for zipfile in zipfiles:
        zipfile = zipfile.replace(r'&',r'\&')
        os.system(f'cd MAST_data\n rm {zipfile}')
        

def rebin_lc(data):
    flux = []
    i = 0
    while i <= len(data['FLUX']):
        flux_i = data['FLUX'][i][2][2] + data['FLUX'][i+1][2][2] + data['FLUX'][i+2][2][2]
        flux.append(flux_i)
        i += 3
        # if len(data['FLUX']) is not of length 3n then we have to drop the last 1-2 values
        if i+3 > len(data['FLUX']):
            break
    return flux


def produce_the_matrix():
    matrix = [] # this will be the array of LCs
    n_bins = 968
    
    for file in os.listdir(mast_data_path):
        try:
            hdu = fits.open(mast_data_path + file)
            data = hdu[1].data
            flux = []
            sector = hdu['PRIMARY'].header['SECTOR']
            if sector >= 27:
                flux = rebin_lc(data)               
                for i in range(len(flux)):
                    flux_i = flux[i]
                    flux.append(flux_i)
                flux = flux / np.max(flux) # normalize each LC
                flux = flux[:n_bins] # trim to 24 days
                matrix += [flux]
                
            else:         
                for i in range(len(data['FLUX'])):
                    flux_i = data['FLUX'][i][2][2] # [frame][row][col]
                    flux.append(flux_i)
                flux = flux / np.max(flux) # normalize each LC
                flux = flux[:n_bins] # trim to 24 days
                matrix += [flux]
            
        except OSError:
            continue
    
    return matrix

