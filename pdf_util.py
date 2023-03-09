import os, io
import PyPDF2
#from pathlib import Path
import fitz
from PIL import Image
import pytesseract 
#from tqdm import tqdm #no need for new way but keep for record just incase
import argparse
from shutil import copyfile
#import glob
import psutil
import sys

ERR = str(os.path.basename(__file__)) + ': error: the following arguments are required:'
TEMP = 'c:/temp/'  #ssd dir to speed up 
MEM = ()
MAX_IMG_SZ = 6291456
NO_CHK = False

def PDFsplit(pdf, splits, outdir =''):
    
    file=os.path.basename(pdf)

    # creating input pdf file object
    pdfFileObj = open(pdf, 'rb')
      
    # creating pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    #total pages
    #print(f"pages: {len(pdfReader.pages)} and last split page {splits[-1]}")
    if splits[-1]> len(pdfReader.pages):
        print(f"the last split page {splits[-1]} is larger than total {len(pdfReader.pages)} pages of the document!!")
        pdfFileObj.close()
        sys.exit(0)
      
    # starting index of first slice
    start = 0
      
    # starting index of last slice
    end = splits[0]
    ret = []
            
    for i in range(len(splits)+1):
        # creating pdf writer object for (i+1)th split
        pdfWriter = PyPDF2.PdfWriter()
          
        # output pdf file name
        if outdir=='':
            outputpdf = pdf.split('.pdf')[0] + '.' + str(i) + '.pdf'
        else:
            outputpdf = outdir + file.split('.pdf')[0] + '.' + str(i) + '.pdf'
          
        # adding pages to pdf writer object
        for page in range(start,end):
            pdfWriter.add_page(pdfReader.pages[page])
          
        # writing split pdf pages to pdf file
        with open(outputpdf, "wb") as f:
            pdfWriter.write(f)
            print(f"splited {outputpdf}")
        ret.append(outputpdf)
        # interchanging page split start position for next split
        start = end
        try:
            # setting split end position for next split
            end = splits[i+1] 
                
        except IndexError:
            # setting split end position for last split
            end = len(pdfReader.pages)
            
    # closing the input pdf file object
    pdfFileObj.close()
    return ret
              
def PDFmerge(pdfs, output):
    # creating pdf file merger object
    pdfMerger = PyPDF2.PdfMerger()
  
    # appending pdfs one by one
    for pdf in pdfs:
        pdfMerger.append(pdf)
  
    # writing combined pdf to output pdf file
    with open(output, 'wb') as f:
        pdfMerger.write(f)
    print(f"merged files to {output}")

# rotaTING WHOLE PDF file
def PDFrotate(origFileName, newFileName, rotation):
  
    # creating a pdf File object of original pdf
    #pdfFileObj = open(origFileName, 'rb')
      
    # creating a pdf Reader object
    #pdfReader = PyPDF2.PdfReader(pdfFileObj)
    pdfReader = PyPDF2.PdfReader(origFileName)
  
    # creating a pdf writer object for new pdf
    pdfWriter = PyPDF2.PdfWriter()
      
    # rotating all page!!!!!!!!!!!!!!!!!!!
    for page in range(len(pdfReader.pages)):
  
        # creating rotated page object  pdfReader.pages[page]
        pageObj = pdfReader.pages[page]
        pageObj.rotate(rotation)
  
        # adding rotated page object to pdf writer
        pdfWriter.add_page(pageObj)
  
    # new pdf file object
    #newFile = open(newFileName, 'wb')
      
    # writing rotated pages to new file
    #pdfWriter.write(newFile)
    pdfWriter.write(newFileName)
    print(f"rotated {newFileName} by {rotation} degrees")
  
    # closing the original pdf file object
    #pdfFileObj.close()
      
    # closing the new pdf file object
    #newFile.close()

def PDFextract(fileName, pages=[]):
    # creating a pdf file object
    #pdfFileObj = open(fileName, 'rb')
    
    # creating a pdf reader object
    #pdfReader = PyPDF2.PdfReader(pdfFileObj)
    #try without opening 
    pdfReader = PyPDF2.PdfReader(fileName)
    
    
    # printing number of pages in pdf file
    totalPage = len(pdfReader.pages)
    
    # creating a page object
    #pageObj = pdfReader.pages[page]
    ret = []
    for page in pages:
        if page < totalPage:
            pageObj = pdfReader.pages[page]
            ret.append(pageObj.extract_text())
            print(f"page {page} content:\n {pageObj.extract_text()}") 
    # closing the pdf file object
    #pdfFileObj.close() 
    
def ImgToPDF(flist, outdir = './'):
    for file in flist:
        items=os.path.basename(file).split('.')[:-1]
        fname= outdir + '.'.join(items) + '.pdf'
        image_1 = Image.open(file)
        im_1 = image_1.convert('RGB')
        im_1.save(fname)
        print(f"converted '{file}' to '{fname}'.")


# page need to convert to zero base
def PDFToImg(filename, pages, outdir, fmt = 'png', zoom = 2.5):
    # To get better resolution
    #zoom_x   # horizontal zoom
    #zoom_y   # vertical zoom
    #mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
    mat = fitz.Matrix(zoom, zoom)
    #path = '<path>/data/'    < --- in case of convert whole directory use glob.
    #all_files = glob.glob(path + "*.pdf")
    #for filename in all_files:
    doc = fitz.open(filename)  # open document
    file = outdir + os.path.basename(filename)[:-3] 
    ret = []
    if pages == []: o_all = True
    else: 
        o_all = False
        #check pages overlapse
    
    for i, page in enumerate(doc):  # iterate through the pages
        if i in pages or o_all: #based zero pages
            pix = page.get_pixmap(matrix=mat)  # render page to an image
            #check/adjust max zoom 
            #pix.save("../data/out/page-%i.png" % page.number)  # store image as a PNG
            
            #Image.MAX_IMAGE_PIXELS = None
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ifile = file + str(i+1) + '.' + fmt
            img.save(ifile)
            ret.append(ifile)
            print(f"page {i+1} saved as {ifile}") 
    doc.close()
    if ret == []:
        print(f"No pdf page from {filename} process, please check the option pages range parameter")
    return ret
            
# PDF_OCR(args['pdf'], o_pages, args['ocr_lang'], psm, rects, args['ocr_recttype'])
# rect = (x0, y0, x1, y1) upper left and lower right conner)
# type 'percent' or 'pc' will cut by percentage
def OCR_img(imgfile, lang, psm, rect, ptype = 'pt'):
    img = Image.open(imgfile)
    w, h = img.size
    if ptype == 'pc' or ptype == 'percent': #convert percentage of width and height 
        scale = (int(rect[0] * w/100), int(rect[1] * h/100), int(rect[2] * w/100), int(rect[3] * h/100) )
        
    if scale[2] == 0 and scale[3] == 0: #use default
        scale = (0,0,w,h)
        
    if scale[0] >= w or scale[1] >= h:
        print(f"the 1st point of crop size ({scale[0]},{scale[1]}) too large (image size [w:{w}, h:{h}])")
        sys.exit(0)
    if scale[2] > w or scale[3] > h:
        print(f"Warning : the set lower right point ({scale[2]},{scale[3]}) to large.\nIt is reduce to image [w:{w}, h:{h}]")
    pict = (scale[0],scale[1],min(scale[2],w), min(scale[3],h))
    
    fname = TEMP+"cropped_" +os.path.basename(imgfile)[:-3] + 'png'
    img.crop(pict).save(fname)
    
    # tesseract images/bilingual.png - -l eng+hin
    option = f"-l {lang} --psm {psm}" 
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    
    ###### TESSDATA_PREFIX environment variable is set to your "tessdata" directory #######
    # option = "-l 'script/Tibetan' --psm 4" 
    # option = "-l 'script/Tibetan' --psm 6"  ########### <--so far the best with high res ###############
    # Use --oem 1 for LSTM/neural network, --oem 0 for Legacy Tesseract.
    text = str(pytesseract.image_to_string(Image.open(fname),config=option))
    print(f"Current page: '{os.path.basename(fname)}' text:\n{text}\n")
    
    # remove the file in TEMP
    os.remove(fname) 
    return text
    
def PDF_OCR(fname, pages, lang, psm, rect, rtype = 'pt'):
    text = {} # aditonary of ocr-ed text
    fimgs = PDFToImg(fname, pages, TEMP, fmt = 'png', zoom = 2.5) #array of pages that are imaged.
    for fimg in fimgs:
        # decode the format name of fimg as  ifile = file + str(i+1) + '.' + fmt in PDFToImg: str(i)+1 is the page#
        page = '.'.join(os.path.basename(fimg).split('.')[:-1])
        
        text[page] = OCR_img(fimg, lang, psm, rect, rtype)  # string format of page number
    #clean up
    for fimg in fimgs:
        os.remove(fimg)
    return text
    
def PDFencrypt(infile, outfile, password):
    pdf_writer = PyPDF2.PdfWriter()
    pdf_reader = PyPDF2.PdfReader(infile)

    for page in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page])

    pdf_writer.encrypt(user_password=password, owner_pwd=None, 
                       use_128bit=True)

    with open(outfile, 'wb') as fh:
        pdf_writer.write(fh)
    print(f"Saved encypted file as {outfile}")

    
'''
def OCR_Pages(fileName):
    doc = fitz.open(fileName) # open pdf files using fitz bindings 

    fullText = ''
    for i in tqdm(range(len(doc)), desc="pages"):
        text = ''
        for img in tqdm(doc.get_page_images(i), desc="page_images"):
            
            xref = img[0]
            image = doc.extract_image(xref)
            pix = fitz.Pixmap(doc, xref)
            
            output = f"{fileName[:-4]}_{i}_{xref}.png"
            pix.save(output) # save as png image
            
            #reopen and crop it before

            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
            
            #image = cv2.imread(args["image"])
            #rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # OCR the image, supplying the country code as the language parameter
            # --psm: The page segmentation mode for Tesseract.
            # Our default is for a page segmentation mode of 13, which treats the image as a single line of text. 
            # For our last example today, we will OCR a full block of text of German. For this full block, 
            # we will use a page segmentation mode of 3 which is fully automatic page segmentation without Orientation and Script Detection (OSD).
            # options = "-l {} --psm {}".format(args["lang"], args["psm"])
            # text = pytesseract.image_to_string(rgb, config=options)
            # for tibetan: tesseract .\guru.png stdout -l script/Tibetan --psm 4 
            # https://documentation.help/PyMuPDF/pixmap.html#Pixmap.writeImage.
            # https://www.geeksforgeeks.org/python-pil-image-crop-method/
            # https://stackoverflow.com/questions/1076638/trouble-using-python-pil-library-to-crop-and-save-image
            # https://code-maven.com/crop-images-using-python-pil-pillow.     
            # https://stackoverflow.com/questions/63428932/crop-an-area-of-pdf-around-annotated-text-using-fitz --> PDF    
            #for Tibetan    
            # option = "-l 'script/Tibetan' --psm 4" 
            # option = "-l 'script/Tibetan' --psm 6"  ########### <--so far the best with high res ###############
            option = f"-l {args['lang']} --psm {args['psm']}" 
            text = str(pytesseract.image_to_string(Image.open(output),config=option))
            print(f"Current text:'{text}'")

        fullText += text

    fullText = fullText.splitlines() # or do something here to extract information using regex
    return fullText
'''

def chkarg(args, arg, opts):
    if not args[arg]:
        print(f"{ERR} {opts}")
        sys.exit(0)

def chkparam(args, arg, opts):
    chkarg(args,arg,opts)
    if not args['pdf']:
        print(f"{ERR} -p/--pdf")
        sys.exit(0)
        
def chkoutdir(args):
    if args['out'] != 'pdf_out.pdf': 
        if not os.path.isdir(args['out']):
            print(f"output directory is invalid!")
            sys.exit(0)
        else:  dir = args['out'].rstrip("\\/") + "/"
    else: dir = './'
    return dir

# copy the temp file that may need to be deleted later 
# the py cannot delete these.      
def mkClean(flist):
    with io.open(TEMP + "cleanup.txt",'w',encoding='utf8') as f:
        for item in flist:
            f.write(item + "\n") 

# for use to convert from command line selected pages to splited page
def PDFextractByRange(args, arg, opt, savedir=TEMP): #arg = 'split_pages'; opt = -sp/--split_pages
    chkparam(args,arg,opt)
    f_rot = []
    try:  
        ranges = args[arg].split(',')
        r_pages = [] #ranges
        for item in ranges:
            if '-' in item:
                tup = [int(x) for x in item.split('-')]
                if tup[0] >= tup[1]:
                    print(f"the ranges of pages must in increasing order. item '{item}' is wrong!")
                    sys.exit(0)
                if tup[0] <= 0:
                    print(f"smallest value of the first page must greater or equal to 1. {tup[0]} was assigned ")
                    sys.exit(0)
                r_pages.append(tup)
            else:
                r_pages.append([int(item),int(item)])
        for i, tup in enumerate(r_pages):
            if i+1 < len(r_pages) and tup[1] >= r_pages[i+1][0]:
                print(f"the ranges of pages must in increasing order.")
                sys.exit(0)

        #convert to s_pages = split pages
        s_pages=[]
        for i, tup in enumerate(r_pages):
            if tup[0]>1:
                s_pages.append(tup[0]-1)
            s_pages.append(tup[1])
                                
        f_cuts = PDFsplit(args['pdf'], s_pages, savedir) #'c:/temp/' for rotate
        f_num = int(f_cuts[-1].split('.')[-2])
        print(f"total file {f_num+1}")
            
        #the index need to be rotation is alternate number
        if int(ranges[0][0]) == 1:
            f_rot = [x for x in range(f_num+1) if (x % 2) == 0]
        else:
            f_rot = [x for x in range(f_num+1) if (x % 2) != 0] 
        
    except:
        print(f"invalid {args['cmd']} pages format, it must be array of order numbers e.g. '1,5,9-3,17'")
        sys.exit(0)
    
    return f_num+1,f_rot, f_cuts  #total file = max index+1, the selected choices index in range, the full cut list file names

def main(args):
 
    if  MEM.total < 8529000000: # less than 8 BG
        print(f"The computer memory amount is too low  (< 8GB) command cannot run!")
        sys.exit(0)
    if MEM.total > 34116001000:  #about 32 B or above
        MAX_IMG_SZ = 16777216
    if args['mem_check'].lower() == 'false': MAX_IMG_SZ = None #set to None
    
    cleans = []
    splits = []  # <-- NEED TO CHECK ALL SOFTWARE!
    if args['cmd'] == 'split':
        #main.py: error: the following arguments are required: -c/--cmd
        chkarg(args, 'pdf', '-p/--pdf')      
        chkparam(args, 'split_pages', '-sp/--split_pages')
        
        if MAX_IMG_SZ and os.path.getsize(args['pdf']) > 17 * MAX_IMG_SZ:
            print(f"Error: The file {args['pdf']} has too large size {os.path.getsize(args['pdf'])}!!!")
            sys.exit(0)

        try:
            splits = [int(x.strip()) for x in args['split_pages'].split(',')] 
        except:
            print(f"Wrong format. 'split_pages' should be a list of pages separated by comma(s), E.g. 3,7,12")
            sys.exit(0)
        try:
            if args['out'] == 'pdf_out.pdf':
                PDFsplit(args['pdf'], splits)
            else:
                dirname = args['out'].rstrip("\\/") + "\\"
                if not os.path.isdir(dirname):
                    print(f"output directory {dirname} not valid!!!")
                    sys.exit(0)
                PDFsplit(args['pdf'], splits, dirname)
        except Exception as err:
            print(f"   {err}")
            sys.exit(0)
        print("The files were ouput successfully!")
         
    elif args['cmd'] == 'merge':
        chkarg(args, 'merge_files', '-mf/--merge_files')
        try:
            splits = [x.strip() for x in args['merge_files'].split(',')] 
        except:
            print(f"Wrong format. 'merge_files' should be a list of files separated by comma(s), E.g. f1.pdf,f2.pdf,f3.pdf")
            sys.exit(0)
        #check outputdir exist
        
        for file in splits:
            if not os.path.isfile(file):
                print(f"the input file '{file}' is not valid.")
                sys.exit(0)
            if MAX_IMG_SZ and os.path.getsize(file) > MAX_IMG_SZ:
                print(f"error: file '{file}' with its size {os.path.getsize(file)} is larger than max support size ({MAX_IMG_SZ})!")
                sys.exit(0)
        #join them to output dir
        try:
            if args['out'] == 'pdf_out.pdf':
                PDFmerge(splits,args['out'])
            else:
                if args['out'][-4:].lower() != '.pdf':
                    print(f"invalid ouput file name {args['out']}, expected the extension is '.pdf'")
                    sys.exit(0)
                dirname =  os.path.dirname(args['out'])
                if len(dirname)==0:
                    dirname = './'
                    fullname = dirname + args['out']
                else:
                    fullname = args['out']
                if not os.path.isdir(dirname):
                    print(f"the ouput dir {dirname} is not exist")
                    sys.exit(0)
                #print(f"OK from here {dirname}, full {fullname}")
                PDFmerge(splits, fullname)
        except Exception as err:
            print(f"   {err}")
            sys.exit(0)
        print("The merged file was ouput successfully!")
  
    elif args['cmd'] == 'rotate':
        if MAX_IMG_SZ and os.path.getsize(args['pdf']) > 17 * MAX_IMG_SZ:
            print(f"Error: The file {args['pdf']} has too large size {os.path.getsize(args['pdf'])}!!!")
            sys.exit(0)
        try:
            angle = int(args['rotate_angle'])
            if angle <= 0 or angle >= 360:
                print(f"invalid angle {args['rotate_angle']} must be a number > 0 and < 360")
                sys.exit(0)
        except:
            print(f"invalid angle format {args['rotate_angle']}, the angle must be a number > 0 and < 360")
            sys.exit(0) 
            
        #check output filename:
        if args['out'][-3:] != 'pdf':
            print(f"error: the out put file name as '{args['out']}' is invalid.")
            sys.exit(0)
        # call rotation the accoring files
        # save the retating files to diff names 
        # create the list of combined files by f_news.
        try:
        #if True:
            total, f_rot, f_cuts = PDFextractByRange(args,'rotate_pages', '-rp/--rotate_pages')
            f_news = []
            for i in range(total):
                if i in f_rot:
                    PDFrotate(f_cuts[i], f_cuts[i][:-4] + "-.pdf", angle)
                    f_news.append(f_cuts[i][:-4] + "-.pdf")
                else:
                    f_news.append(f_cuts[i])
                
            #call for merge back
            PDFmerge(f_news,args['out'])
                
                #clean up:
            cleans = set(f_cuts).union(set(f_news))
            for item in cleans:
                os.remove(item) 
                
        except Exception as err:
            print(f"   {err}")
            sys.exit(0)
    
    elif args['cmd'] == 'extract':
        dir = chkoutdir(args)
        if MAX_IMG_SZ and os.path.getsize(args['pdf']) > 17 * MAX_IMG_SZ:
            print(f"Error: The file {args['pdf']} has too large size {os.path.getsize(args['pdf'])}!!!")
            sys.exit(0)
            
        total, splits, fulllst = PDFextractByRange(args,'extract_pages', '-ep/--extract_pages') 
        print(f"total files {total}, and list need: {splits}")
        
        ind = 0
        for i in splits:
            fname = os.path.basename(args['pdf'])
            fname = fname[:-3] + str(ind) + '.pdf'
            ind+=1
            copyfile(fulllst[i], dir+fname)       
            print(f"copied {dir+fname}")   
        
        for temp in fulllst:
            os.remove(temp)
        print(f"temp files removed!")
        
    elif args['cmd'] == 'pdf':
        chkarg(args, 'to_pdfs', '-pf/--to_pdfs')
        
        try:
            splits = [x.strip() for x in args['to_pdfs'].split(',')] 
        except:
            print(f"Wrong format. 'to_pdfs' should be a list of impage files separated by comma(s), E.g. f1.png,f2.jpg,f3.bmp")
            sys.exit(0)
        #check size of each image
        for file in splits:
            if MAX_IMG_SZ and os.path.getsize(file) > MAX_IMG_SZ:
                print(f"Error: too large image file size (> 16Mb)) is not support!")
                sys.exit(0)
        
        try:
            dir = chkoutdir(args)
            ImgToPDF(splits, dir)
        except Exception as err:
            print(f"   {err}")
            sys.exit(0)
            
    elif args['cmd'] == 'image':
        chkparam(args, 'image_pages', '-ip/--image_pages')
        outdir = chkoutdir(args)
        #scale = float(args['image_scale'])
        if len(args['pdf'].split(','))>1:
            print(f"only one pdf file name can be convert to image!")
            sys.exit(0)
        #check size
        if MAX_IMG_SZ and os.path.getsize(args['pdf']) > 17 * MAX_IMG_SZ:
            print(f"error: pdf size too large. Not support operation")
            sys.exit(0)
        
        try:
        #if 1==1: 
            pages=[] #store page in base 0
            for page in args['image_pages'].split(','):
                if '-' not in page:
                    pages.append(int(page)-1)
                else:
                    prange = [int(x) for x in page.split('-')]
                    pages = pages + list(range(prange[0]-1,prange[1]))    #use based zero
            
            PDFToImg(args['pdf'], pages, outdir, args['image_format'], float(args['image_scale']))
        except Exception as err:
            print(f"   {err}")
            sys.exit(0)
        
    elif args['cmd'] == 'ocr': 
        chkparam(args, 'ocr_pages', '-op/--ocr_pages')
        outdir = chkoutdir(args)
        if args['ocr_psm']=='auto':
            if args['ocr_lang'].find('Tibetan') >= 0 or args['ocr_lang'].find('script')>=0:
                psm = 6
            else: psm = 3
        rects = [int(x) for x in args['ocr_rect'].split(',')]
        if args['ocr_recttype'] == 'pc' or args['ocr_recttype'] == 'percent':
            for percent in rects:
                if percent >= 100:
                    print(f"The percentage of cropping the picture should less than 100%")
                    sys.exit(0)
            if rects[0] >= rects[2] or rects[1] >= rects[3]:
                print(f"the percentage cropping rectangle value must be in order left,top,right,bottom!")
                sys.exit(0)
                
        o_pages=[]
        if args['ocr_pages'] != 'all': 
            try: 
                ranges = args['ocr_pages'].split(',')
                o_pages = [] #ranges
                for item in ranges:
                    if '-' in item:
                        tup = [int(x) for x in item.split('-')]
                        if tup[0] >= tup[1]:
                            print(f"the ranges of pages must in increasing order. item '{item}' is wrong!")
                            sys.exit(0)
                        if tup[0] <= 0:
                            print(f"smallest value of the first page must greater or equal to 1. {tup[0]} was assigned ")
                            sys.exit(0)
                        #based zero
                        o_pages = o_pages + list(range(tup[0]-1, tup[1]))
                    else:
                        o_pages.append(int(item)-1)
            except:
                print(f"the request page range for OCR is invalid")
                sys.exit(0)
        
        PDF_OCR(args['pdf'], o_pages, args['ocr_lang'], psm, rects, args['ocr_recttype'])    
       
    elif args['cmd'] == 'encrypt':  
        chkparam(args, "ecrypt_pwd", "-pwd/--ecrypt_pwd")
        if args['out'][-3:] != 'pdf':
            print(f"the output dpf file name must have extension as '.pdf'")
            exit(1)
        PDFencrypt(args['pdf'], args['out'], args['ecrypt_pwd'])
    else:
        print(f"Unknow command '{args['cmd']}'!")
            
                
                
if __name__ == "__main__":
    #get memory condition
    MEM = psutil.virtual_memory()
    # calling the main function
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cmd", required=True,
        help="command :" + \
            "extract (pages from a pdf), " + \
            "encrypt (set password for a pdf)" + \
            "image (convert pages from pdf to images), " + \
            "merge (pdfs to single pdf), " + \
            "ocr (read text form pages of a pdf), " + \
            "pdf (convert images to a pdf), " + \
            "rotate (pages within a pdf), " + \
            "split (a pdf to many pdfs), " 
        )
            
            
    ap.add_argument("-p", "--pdf", 
        help="path to input pdf file")
    ap.add_argument("-o", "--out", default="pdf_out.pdf",
        help="path to output file(s)/directory")   
    ap.add_argument("-ep", "--extract_pages", 
        help="page numbers for the extraction (e.g. '-c extract -ep 3,5-8,10')")
    ap.add_argument("-if", "--image_format", default= 'png',
        help="the format for the images default 'png' (e.g. '-c image -ip 3,5-8 -if jpg')")
    ap.add_argument("-ip", "--image_pages",
        help="page numbers of the pdf for the extracted images (e.g. '-c image -ip 3,5-8,10 ['all'])")
    ap.add_argument("-is", "--image_scale", default='2.5',
        help="the scale factor for the images default 1.0 (e.g. '-c image -ip 3,5-8 -is 2.2')")
    ap.add_argument("-mf", "--merge_files", 
        help="source pdf files to be merged (e.g. '-c merge -mf file1.pdf,file2.pdf')")
    ap.add_argument("-ol", "--ocr_lang", type=str, default="eng", 
        help="optional: language for OCR'ing -- default 'eng'")
    ap.add_argument("-om", "--ocr_psm", type=str, default="auto",
        help="optional: PSM mode -- default auto. For Tibetan use psm 6")
    ap.add_argument("-op", "--ocr_pages", default = "all",
        help="optional: page numbers for OCR'ing -- default 'all' (e.g. '-c ocr -op 3,5-8,10,12-15')")
    ap.add_argument("-or", "--ocr_rect", default='0,0,0,0',
        help="optional: rectangle area for OCR'ing: left,top,right,bottom (e.g. '-c ocr -or 5,3,600,800'). Default full page or set as 0,0,0,0")
    ap.add_argument("-ot", "--ocr_recttype", default='pt',
        help="optional: rectangle area type for OCR'ing as coordination: ['pt'|'point'] or as percentage ['pc'|'percent'] (e.g. '-c ocr -ot pt')")
    ap.add_argument("-pf", "--to_pdfs", 
        help="source image(s) to convert to pdfs (e.g. '-c pdf -pf file1.jpg,file2.pnp')")
    ap.add_argument("-pwd","--ecrypt_pwd", 
        help="set password (e.g. '-c encrypt -pwd Myp@22w0rd! -p test.pdf')")
    ap.add_argument("-ra", "--rotate_angle", default="180",
        help="optional: rotation angle (e.g. '-c rotate -rp 3,6, -ra 90)")
    ap.add_argument("-rp", "--rotate_pages", 
        help="page numbers for rotation with thin the pdf file (e.g. '-c rotate -rp 3,5-8,10,12-15')")
    ap.add_argument("-sp", "--split_pages", 
        help="the last page numbers for the splits (e.g. '-c split -op 3,5')")
    ap.add_argument("-chk","--mem_check", default = "true", help=argparse.SUPPRESS)
    
    args = vars(ap.parse_args())

    #print(f"debug args {args}")
    main(args)
    # to convert python to executable
    # pyinstaller --onefile -w 'filename.py'   < - for windows app
    # pyinstaller --onefile --console 'filename.py'   < - for commandline app
    