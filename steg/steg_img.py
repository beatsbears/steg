'''
steg - steg_img.py
:author: Andrew Scott
:date: 6-25-2018
'''
import os
from steg import common

from PIL import Image as img

class IMG:
    '''
    Class for hiding binary data within select lossless image formats.
    Supported image formats: PNG, TIFF, BMP 

    :param payload_path: The path of the payload (message) that should be hidden.
    :param image_path: The path of the carrier image in which to hide the payload.
    '''
    def __init__(self, payload_path=None, image_path=None):
        self.payload_to_hide = payload_path
        self.carrier_image = image_path
        self.file_type = None
        self.fg = None
        self.image_type = None
        self.max_image_size = 0
        self.image_mode = None
        self.payload = None
        self.common = common.Common(self.payload_to_hide)
        self.supported = ['PNG','TIFF','TIF','BMP','ICO']

        assert self.carrier_image is not None

        # Get the file type from payload path
        self.file_type = self.payload_to_hide.split('.')[-1] if self.payload_to_hide else None
        # Analyze image attributes
        self.analyze_image()

    def analyze_image(self):
        '''
        Opens the carrier image file and gathers details.
        '''
        try:
            # Open the image file using PIL
            self.fg = img.open(self.carrier_image)
            # Get the carrier image name and type from the path
            self.image_type = self.carrier_image.split('.')[-1]
            # Get the total number of pixels that can be manipulated
            self.max_image_size = self.fg.size[1] * self.fg.size[0]
            # Gets the image mode, hopefully this is L, RGB, or RGBA
            self.image_mode = ''.join(self.fg.getbands())
        except Exception as err:
            raise Exception('Error analyzing image: {} - {}'.format(self.carrier_image, str(err)))

    def assign_output_file_type(self):
        '''
        Determines the correct file format.
        '''
        image_type = self.image_type.lower()
        if image_type in ['jpg', 'jpeg']:
            return 'jpeg'
        elif image_type in ['tif', 'tiff']:
            return 'TIFF'
        elif image_type == 'png':
            return 'png'
        elif image_type == 'bmp':
            return 'bmp'
            

    def _use_correct_function_hide(self):
        '''
        Depending on image mode will use the different hiding methods.
        '''
        if self.image_mode == 'L':
            self.L_replace_bits(self.payload_to_hide)
        elif self.image_mode in ['RGB', 'BGR']:
            self.RGB_replace_bits(self.payload_to_hide)
        elif self.image_mode == 'RGBA':
            self.RGBA_replace_bits(self.payload_to_hide)
        elif self.image_mode == '1':
            print("[!] Cannot hide content using an image with a mode of '1'")
        else:
            print("[!] Error determining image mode")

    def _use_correct_function_extract(self):
        '''
        depending on IMG format will use the different Extraction methods
        '''
        if self.image_mode == 'L':
            return self.L_extract_message(self.fg)
        elif self.image_mode in ['RGB', 'BGR']:
            return self.RGB_extract_message(self.fg)
        elif self.image_mode == 'RGBA':
            return self.RGBA_extract_message(self.fg)
        elif self.image_mode == '1':
            print("[!] Cannot extract content using an image with a mode of '1'")
            return '.'
        else:
            print("[!] Error determining image mode")

    def RGB_replace_bits(self, payload):
        '''
        Replace the least-significant bit for RGB images.

        :param payload: This is the path of the payload file.
        '''
        # 3 bytes per pixel should be greater than 2* the binary message length
        if self.max_image_size*3 <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        # create a new empty image the same size and mode as the original
        newIm = img.new("RGB", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    # get the value for each byte of each pixel in the original image
                    fgr,fgg,fgb = self.fg.getpixel((col,row))

                    # get the new lsb value from the bitstream
                    rb = next(bitstream)
                    # modify the original byte with our new lsb
                    fgr = self.common.set_bit(fgr, rb)

                    gb = next(bitstream)
                    fgg = self.common.set_bit(fgg, gb)

                    bb = next(bitstream)
                    fgb = self.common.set_bit(fgb, bb)
                    # add pixel with modified values to new image
                    newIm.putpixel((col, row),(fgr, fgg, fgb))
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('Failed to write new file: {}'.format(str(e)))


    # extract hidden message from RGB image
    def RGB_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in RGB images.

        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgr,fgg,fgb = fg.getpixel((col,row))
                    
                    hidden += bin(fgr)[-1]
                    hidden += bin(fgg)[-1]
                    hidden += bin(fgb)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))

    #LSB steg for Black and white images
    def L_replace_bits(self, payload):
        '''
        Replace the least-significant bit for L images.
        :param payload: This is the path of the payload file.
        '''
        if self.max_image_size <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        newIm = img.new("L", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    fgL = self.fg.getpixel((col,row))

                    nextbit = next(bitstream)
                    fgL = self.common.set_bit(fgL, nextbit)

                    # add pixel to new image
                    newIm.putpixel((col,row),(fgL))
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('Failed to write new file: {}'.format(str(e)))

    # extract hidden message from L image
    def L_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in L images.
        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgL = fg.getpixel((col,row))
                    
                    hidden += bin(fgL)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))

    # replace lest-significant bit for RGBA images
    def RGBA_replace_bits(self, payload):
        '''
        Replace the least-significant bit for RGBA images.
        :param payload: This is the path of the payload file.
        '''
        if self.max_image_size*3 <= 2*self.common.get_payload_size(payload):
            raise Exception('[!] Attempting to hide a message that is too large for the carrier')

        # generate bitstream 
        bitstream = iter(self.common.text_to_binary(payload, self.max_image_size * 3))

        newIm = img.new("RGBA", (self.fg.size[0], self.fg.size[1]), "white") 
        try:
            for row in range(self.fg.size[1]):
                for col in range(self.fg.size[0]):
                    fgr, fgg, fgb, fga = self.fg.getpixel((col, row))

                    redbit = next(bitstream)
                    fgr = self.common.set_bit(fgr, redbit)

                    greenbit = next(bitstream)
                    fgg = self.common.set_bit(fgg, greenbit)

                    bluebit = next(bitstream)
                    fgb = self.common.set_bit(fgb, bluebit)
                    # add pixel to new image
                    newIm.putpixel((col, row),(fgr, fgg, fgb, fga))
            # if our passed in location exists, try saving there
            output_file_type = self.assign_output_file_type()
            newIm.save(str('new.' + output_file_type), output_file_type)
            print('[+] {} created'.format('new.' + output_file_type))
        except Exception as e:
            raise Exception('[!] Failed to write new file: {}'.format(str(e)))

    # extract hidden message from RGBA image
    def RGBA_extract_message(self, fg):
        '''
        Extracts and reconstructs payloads concealed in RGBA images.
        :param fg: This is the PngImageFile of the carrier image.
        '''
        hidden = ''
        try:
            # iterate through each pixel and pull the lsb from each color per pixel
            for row in range(fg.size[1]):
                for col in range(fg.size[0]):
                    fgr, fgg, fgb, fga = fg.getpixel((col, row))
                    
                    hidden += bin(fgr)[-1]
                    hidden += bin(fgg)[-1]
                    hidden += bin(fgb)[-1]
            try:
                returned_file = self.common.reconstitute_from_binary(hidden)
                return returned_file
            except Exception as e:
                raise Exception('Inner failed to extract message: {}'.format(str(e)))
        except Exception as e:
            raise Exception('Outer failed to extract message: {}'.format(str(e)))
    
    def hide(self):
        '''
        Hides a payload within a carrier image. Defaults to outputting the new image into the 
        current directory with the name `new.<file_type>`.
        '''
        self._use_correct_function_hide()

    def extract(self):
        '''
        Extracts a payload from a carrier image if possible. Defaults to output the payload into the
        current directory with the name `hidden_file.<file_type>`.
        '''
        self._use_correct_function_extract()

