import urllib.request

url = "https://letsencrypt.org/certs/isrgrootx1.pem"
save_path = r"C:\Users\Midhun\Documents\certs\isrgrootx1.pem"

try:
    print("Downloading fresh certificate...")
    urllib.request.urlretrieve(url, save_path)
    print("Successfully downloaded and replaced clean certificate!")
    with open(save_path, "r") as f:
        print("File Preview (First line):", f.readline().strip())
except Exception as e:
    print("Error saving certificate:", str(e))