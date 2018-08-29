#!/usr/bin/env python

import argparse
import steg_img

def arguments():
    help_txt = """Steg image hiding/extraction tool.

    To hide an image you must specify a carrier (image) and a payload.
    ex. $ python steg.py -c <carrier> -p <payload>

    To extract a payload from a hidden file, simply omit the payload argument.
    ex. $ python steg.py -c <carrier>"""
    parser = argparse.ArgumentParser(description=help_txt, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', dest='carrier', type=str, default=None, help='Path to the carrier file.')
    parser.add_argument('-p', dest='payload', type=str, default=None, help='Path to the payload file.')
    args = parser.parse_args()
    
    if args.carrier is None:
        print('[!] No carrier supplied.')
        parser.print_help()
        exit(0)
    
    return args

if __name__ == '__main__':
    args = arguments()
    carrier = args.carrier
    payload = args.payload

    try:
        if payload is None:
            s = steg_img.IMG(image_path=carrier)
            s.extract()
        else:
            s = steg_img.IMG(payload_path=payload, image_path=carrier)
            s.hide()
    except Exception as err:
        print(err)
