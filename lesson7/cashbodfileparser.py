import shutil
import PyPDF2
from PIL import Image
import time
import pytesseract
import os
from pymongo import MongoClient

target_directory_path = './data'

# create directories to sort files
os.mkdir('only_pdf')
os.mkdir('only_jpg')
os.mkdir('img_from_pdf')
os.mkdir('error-files')

# adjust MongoDb
client = MongoClient('localhost', 27017)
db = client.extracted
collection = db.serial_numbers

# organize files by separating pdf files and jpg files from target directory and putting them in different directories
for (dirpath, dirnames, filenames) in os.walk(target_directory_path):
    for filename in filenames:
        name, extension = os.path.splitext(filename)
        if extension == '.pdf':
            shutil.copy(dirpath + '/' + filename, './only_pdf')
        elif extension == '.jpg':
            shutil.copy(dirpath + '/' + filename, './only_jpg')

# extract images from pdf files and put extracted images in special directory
for (dirpath, dirnames, filenames) in os.walk('./only_pdf'):
    for filename in filenames:
        pdf_file_path = dirpath + '/' + filename

        try:
            pdf_file = PyPDF2.PdfFileReader(open(pdf_file_path, 'rb'), strict=False)

            for page_num in range(0, pdf_file.getNumPages()):
                page = pdf_file.getPage(page_num)
                page_obj = page['/Resources']['/XObject'].getObject()

                if '/Im0' in page_obj:

                    if page_obj['/Im0'].get('/Subtype') == '/Image':
                        size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
                        data = page_obj['/Im0']._data

                        if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB':
                            mode = 'RGB'
                        else:
                            mode = 'p'

                        if page_obj['/Im0']['/Filter'] == '/FlateDecode':
                            file_type = 'png'
                        elif page_obj['/Im0']['/Filter'] == '/DCTDecode':
                            file_type = 'jpg'
                        elif page_obj['/Im0']['/Filter'] == '/JPXDecode':
                            file_type = 'jp2'

                        image = open(
                            f'./img_from_pdf/{pdf_file_path.split("/")[-1]}-{time.time()}-{page_num}.{file_type}', 'wb')
                        image.write(data)
                        image.close()

        except PyPDF2.utils.PdfReadError as e:
            shutil.copy(pdf_file_path, './error-files')


# create function to extract serial number from images
def extract_num_from_images(dir_to_extract, template, error_files_path):
    for (dirpath, dirnames, filenames) in os.walk(dir_to_extract):
        for filename in filenames:

            img = dirpath + '/' + filename

            img_obj = Image.open(img)
            text = pytesseract.image_to_string(img_obj, 'rus')

            if text.lower().find(template) + 1:
                for idx, line in enumerate(text.split('\n')):

                    if line.lower().find(template) + 1:
                        eng_text = pytesseract.image_to_string(img_obj, 'eng').split('\n')[idx]
                        number = eng_text.split(' ')[-1]
                        number.strip()

                        if number:
                            yield {'file': filename, 'serial_number': number}
                        else:
                            shutil.copy(dirpath + '/' + filename, error_files_path)

                    else:
                        shutil.copy(dirpath + '/' + filename, error_files_path)

            else:
                shutil.copy(dirpath + '/' + filename, error_files_path)


# extract serial numbers from images obtained from pdf files and record them in MongoDb
for record in extract_num_from_images('./img_from_pdf', 'заводской (серийный) номер', './error-files'):
    collection.insert_one(record)

# extract serial numbers from images and record them in MongoDb
for record in extract_num_from_images('./only_jpg', 'заводской номер (номера)', './error-files'):
    collection.insert_one(record)

# record files that were failed to handle in MongoDb
for (dirpath, dirnames, filenames) in os.walk('./error-files'):
    for filename in filenames:
        error_file = dirpath + '/' + filename
        collection.insert_one({'error_file': error_file})
