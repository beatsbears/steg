# Steg
[![Ochrona](https://img.shields.io/badge/secured_by-ochrona-blue)](https://ochrona.dev)

Steg is a simple python library for hiding and extracting messages from losslessly compressed images using least-significant-bit (LSB) steganography. Current supported image formats include PNG, TIFF, BMP, and ICO.
Steg also includes a command line tool for quick hiding and extraction.

## Installation
```
$ pip install steg
```

## Usage in Code
```
# Import library
from steg import steg_img

# Hiding
# Select your payload and carrier files
s = steg_img.IMG(payload_path=<payload path>, image_path=<carrier path>)
# Create a new image containing your payload
s.hide()

# Extracting
# Select the carrier image
s_prime = steg_img.IMG(image_path=<path of containing hidden payload>)
# Extract the payload
s_prime.extract()
```
## Commandline Usage
1. To hide a payload in an image:
```$ steg -c <your image file> -p <your payload>```
2. To extract a payload from a carrier:
```$ steg -c <your image file>```