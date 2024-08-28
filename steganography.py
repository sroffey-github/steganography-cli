import argparse
from PIL import Image
import os

EOF_MARKER = '1111111111111110'  # EOF marker used to indicate the end of hidden data

def encrypt_string_in_image(image, text):
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    binary_text += '1111111111111110'  # EOF marker

    data_index = 0
    image_data = image.load()

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = list(image_data[x, y])
            for n in range(3):  # Iterate through R, G, B
                if data_index < len(binary_text):
                    pixel[n] = pixel[n] & ~1 | int(binary_text[data_index])
                    data_index += 1
            image_data[x, y] = tuple(pixel)
            if data_index >= len(binary_text):
                break
        if data_index >= len(binary_text):
            break

    return image

def encrypt_file_in_image(image, file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    binary_data = ''.join(format(byte, '08b') for byte in file_data)
    binary_data += '1111111111111110'  # EOF marker

    data_index = 0
    image_data = image.load()

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = list(image_data[x, y])
            for n in range(3):  # Iterate through R, G, B
                if data_index < len(binary_data):
                    pixel[n] = pixel[n] & ~1 | int(binary_data[data_index])
                    data_index += 1
            image_data[x, y] = tuple(pixel)
            if data_index >= len(binary_data):
                break
        if data_index >= len(binary_data):
            break

    return image

def decrypt_from_image(image, is_file=False):
    image_data = image.load()
    binary_data = ""
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = list(image_data[x, y])
            for n in range(3):  # Iterate through R, G, B
                binary_data += str(pixel[n] & 1)
    
    eof_index = binary_data.find(EOF_MARKER)
    if eof_index != -1:
        binary_data = binary_data[:eof_index]

    if is_file:
        byte_data = bytearray()
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            byte_data.append(int(byte, 2))
        return byte_data
    else:
        chars = [chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)]
        return ''.join(chars)

def main():
    parser = argparse.ArgumentParser(description='Hide a file or string inside an image, or decrypt data from an image.')
    parser.add_argument('-l', '--load', required=True, help='The image filename to load.')
    parser.add_argument('-f', '--file', help='The filename of the file to hide in the image, or to save the decrypted file to (optional).')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt the hidden data from the image.')

    args = parser.parse_args()

    if not os.path.exists(args.load):
        print("Error: Image file does not exist.")
        return
    
    image = Image.open(args.load)

    if args.decrypt:
        if args.file:
            hidden_data = decrypt_from_image(image, is_file=True)
            output_file = args.file
            with open(output_file, "wb") as f:
                f.write(hidden_data)
            print(f"Hidden file extracted and saved as {output_file}")
        else:
            hidden_message = decrypt_from_image(image, is_file=False)
            print(f"Hidden message: {hidden_message}")
    else:
        if args.file:
            if not os.path.exists(args.file):
                print("Error: File to hide does not exist.")
                return

            image = encrypt_file_in_image(image, args.file)
        else:
            text = input("Enter the string you want to encrypt in the image: ")
            image = encrypt_string_in_image(image, text)

        output_extension = os.path.splitext(args.load)[1].lower()
        output_filename = 'output_image' + output_extension
        image.save(output_filename)
        print(f"Output image saved as {output_filename}")

if __name__ == '__main__':
    main()