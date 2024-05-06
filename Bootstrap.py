import urllib.request
from sys import argv


def download_file(url: str, filename: str):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        data = response.read()  # Read the entire response
        out_file.write(data)
    print(f"File downloaded: {filename}")

def main():
    # get args
    url = argv[1]
    filename = argv[2]
    
    print(f"Downloading {url} to {filename}")
    
    download_file(url, filename)
    
if __name__ == "__main__":
    main()