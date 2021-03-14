"""
steg - common.py
:author: Andrew Scott
:date: 6-25-2018
"""
from binascii import b2a_hex, a2b_hex
from logging import info as log_info
from os.path import getsize
from random import choice

# Constants
###########################################
START_BUFFER = b"EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
END_BUFFER = b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
TAB = b"\t"
###########################################


class StegException(Exception):
    pass


class Common:
    """
    Provides common functions for steg classes.
    Primary function is to convert files into workable binary and provide cryptographic support.
    """

    def __init__(self, file_path):
        self.carrier_file = file_path

        if file_path != None:
            self.file_type = (file_path.split(".")[-1]).upper()

    def text_to_binary(self, file_path, max_size):
        """
        Reads a payload file and converts it to binary with the appropriate buffers.

        :param file_path: The path of the payload file.
        :param max_size: Used to determine how much extra random data should be appended to the end of the message.
        """
        try:
            text_file = open(file_path, "rb")
            hidden_file = file_path.split(".")[-1]
        except Exception as e:
            raise StegException(f"[!] Failed to open target file: {file_path}") from e
        try:
            text = text_file.read()
            text += TAB

            # add buffers and file format
            text += START_BUFFER + TAB
            text += str.encode(hidden_file) + TAB
            text += END_BUFFER
            text_file.close()

            # convert to hex string
            hex_text = b2a_hex(text).decode("ascii")
            # convert hex to binary and fill the rest of the bitstream with random hex
            b = ""
            for ch in hex_text:
                tmp = bin(ord(ch))[2:]
                if len(tmp) < 7:
                    for _ in range(0, (7 - len(tmp))):
                        tmp = "0" + tmp
                b += tmp
            for _ in range(0, (max_size - len(b)), 7):
                b += str(bin(ord(choice("abcdef")))[2:])
            return b
        except Exception as e:
            raise StegException("[!] Text to binary conversion failed!") from e

    def set_bit(self, old_byte, new_bit):
        """
        Takes a byte and alters the least significant bit.

        :param old_byte: The original Byte.
        :param new_bit: New bit value.
        """
        b = list(bin(old_byte))
        b[-1] = new_bit
        return int("".join(b), 2)

    def reconstitute_from_binary(self, raw_bits):
        try:
            # break long string into array for bytes
            b = [raw_bits[i : i + 7] for i in range(0, len(raw_bits), 7)]
            # convert to string
            c = ""
            for i in b:
                c += chr(int(i, 2))
            # if the string length is not even, add a digit
            if len(c) % 2 != 0:
                c += "A"
            # convert back to ascii
            as_ascii = a2b_hex(c[:-10].encode("ascii"))
            # check to see if the buffer is intact still
            buffer_idx = as_ascii.find(START_BUFFER)
            buffer_idx2 = as_ascii.find(END_BUFFER)
        except Exception as e:
            raise StegException("[!] Error reconstituting from binary!") from e

        if buffer_idx != -1:
            fc = as_ascii[:buffer_idx]
        else:
            raise StegException("[!] Failed to find message buffer...")

        if buffer_idx2 != -1:
            payload_file_type = "." + as_ascii[
                buffer_idx + 49 : buffer_idx2 - 1
            ].decode("ascii")
        else:
            raise StegException("[!] Unknown file type in extracted message")

        if (buffer_idx != -1) and (buffer_idx2 != -1):
            try:
                with open(f"hidden_file{payload_file_type}", "wb") as to_save:
                    to_save.write(fc)
                log_info(
                    f"[+] Successfully extracted message: hiddenFile{payload_file_type}"
                )
            except Exception as e:
                raise StegException(
                    f"[!] Failed to write extracted file: hiddenFile{payload_file_type}"
                ) from e
            return f"hidden_file{payload_file_type}"

    def get_payload_size(self, file_path):
        """
        Returns the size of the potential payload.
        """
        return getsize(file_path) * 8
