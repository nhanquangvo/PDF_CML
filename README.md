# PDF_CML
Fully free command line executable including split, merge, rotate, extract pages, image to pdf, pdf to image, ocr and encrypt pdf. This freeware code is very simple code. You can use it for further learning.

## Requirements & limitation:
The following library of code supposed to be used & installed :
### Hardware & OS: 
1. The code requires at least 8GB RAM, and depended on how much of free-mem of your computer, the bigger file size can be processed.
2. Currently the code run on windows 64-bit platform; however, as far as this code using only standard libraries of Python, nothing prevents you to run it successfully in Linux and OS2. You may have to change minor setting for environmental variable as needed for setting up the requirement software which will be mentioned later in this document.
### Software & other conditions
1. **python**: at least 3.x - currently, the tool was tested with 3.11. This is the crucial. Python is installed "as is" without any modifying its configuration. So, if you set it in your way then please take notes of what changes to adapt for the code to works
2. **tessaract-ocr**: at least version 5.x - currently, the code run on 5.3 with all of it dependcy. You can see it by issue "tesseract --version". Please install full binary/self-compiled version.
Remember, there are some environmental variables you may have to set. The most important ones are:
* Set the `path` value to tessaract-ocr. in my case it is `C:\Program Files\Tesseract-OCR` (please check where your actual tesseract binary actually located)
* Set a new variable named as "TESSDATA_PREFIX" and its value is the path to Tessadata (`C:\Program Files\Tesseract-OCR\tessdata`).
* The tessdata are the palce to store trained data for language recognition. You may have option to replace the original tessdata directory by any legacy/ self-trained tessdata. Currently, the tool was tested with tessdata-best and tessdata-fast. Please use google search and download it. You may also override the `TESSDATA_PREFIX` value to different directories while each directory is the other trained tessdata so the you can choose the best shot for your self-interests. This project uses standard setting at: `C:\Program Files\Tesseract-OCR\tessdata`. But it is replaced by the forementioned trained data.
* Some sample pdf files, pictures inf different formats and pdf e-books. Those ones can be found anywhere or make up yourself. This need in case for modifying the code parameters.
3. Following **Python standard libraries** also required to be installed unarguably by command 'pip install lib_name` 
* `PyPDF2`
* fitz for use with setting up image properties/modifications (lib name: `PyMuPDF`)
* PIL for image editing (lib name: `pillow`)
* `pytesseract` for OCR settings
* `argparse` for command line argument setting
* `shutil` for fast copy file. You can replace it by os command also.
* `psutil` for computer memory check. You can use to check the available of RAM to know what is going on with the large image/file problem
* Optional: `glob` - I am not implement this library; however, for convenience of using wildcards, this is the wonderful choice
* Optional: consider to add `pyinstaller` for conversion from python code to 64-bit binary. This will help you to speed up hugely if you want to use the tool for batching. There are some options for converting the code to executable. In this simple tool, it is kept in single code to avoid complicated binary conversion. Also, remember if you use exit(error) in python, you may consider to use positive 'error' number for exit code (experienced yourself please). Also, the argument to convert to binary also need to be know. E.g., In this code I used: `pyinstaller --onefile --console '.\pdf_util.py'`. If writing for windows option, you may replace the option --console by -w/--windows

### Licensing & deployment: please following exactly (or more strictly) of whatever the required libraries and software that are used in this project. I will not be responsible for any violation of use, abuse, or infringement / copyright you may encounter during using or deployment of this software code.
 

## Disclaimer: 
Another copy of the disclaimer is attached in this project; however it is restated here:

_ _This PDF Command Line Tool (a fully freeware for PDF command line tool) is provided as is without any guarantees or warranty. In association with the product, Nhan Vo, developer of this freeware, makes no warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, of title, or of noninfringement of third party rights. Use of the product by a user is at the user’s risk.
NO REPRESENTATIONS OR WARRANTIES, EITHER EXPRESS OR IMPLIED, OF MERCHANTABILITY, FITNESS FOR A SPECIFIC PURPOSE, THE PRODUCTS TO WHICH THE INFORMATION MENTIONS MAY BE USED WITHOUT INFRINGING THE INTELLECTUAL PROPERTY RIGHTS OF OTHERS, OR OF ANY OTHER NATURE ARE MADE WITH RESPECT TO INFORMATION OR THE PRODUCT TO WHICH INFORMATION MENTIONS. IN NO CASE SHALL THE INFORMATION BE CONSIDERED A PART OF OUR TERMS AND CONDITIONS OF SALE.”_ _

