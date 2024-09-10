import pdfplumber
import collections
from llama_index.core import Document
from src.utils import find_footnote_bloc,find_blocs,extract_bloc

class pdf_loader_custom():

    def __init__(self, filename):

        self.filename = filename
        self.most_common_sizes = self.size_dict(self.filename)
        self.main_size = self.most_common_sizes[0][0]
        self.footnote_size = self.most_common_sizes[1][0]
        self.sidetext_size = self.most_common_sizes[2][0]
    
    def size_dict(self, input):
    #with pdfplumber.open("../Downloads/SR-210-01012024-EN.pdf") as pdf:
        with pdfplumber.open(input) as pdf:
            font_sizes = collections.Counter()
            num_pages = len(pdf.pages)
        
            for i in range( num_pages):
                page = pdf.pages[i]
                for char in page.chars:
                    if char["text"] != ' ':
                        size_key = round(char["size"],2)
                        font_sizes[size_key] += 1
            return font_sizes.most_common(3)
    
    def combine_blocs(self, clean_page): 
        x0,y0,x1,y1 = clean_page.layout.x0,clean_page.layout.y0,clean_page.layout.x1, clean_page.layout.y1
        footnote_top = find_footnote_bloc(clean_page,  self.main_size, self.sidetext_size)
        if footnote_top is not None: 
            #print(f"footnote_top:{footnote_top}")
            blocs, x_middle, upper_main = find_blocs(clean_page, footnote_top, self.main_size,y1 )
            ### extract footnote
            footnote = clean_page.within_bbox((x0,footnote_top,x1, y1))
            footnote_bloc_text = footnote.extract_text()

            if blocs is not None:
                ### extract text above the Art. section (no need to combine left and right)
                upperbloc = clean_page.within_bbox((x0, y0, x1, upper_main))
                upperbloc_text = upperbloc.extract_text()
                ### extract the Art. section 
                bloc_text = extract_bloc(clean_page, blocs, x_middle, x0, x1)
                page_text = upperbloc_text + "\n" +bloc_text+ "\n" +footnote_bloc_text  
                
            else:
                upperbloc = clean_page.within_bbox((x0, y0, x1, footnote_top))
                upperbloc_text = upperbloc.extract_text()
                page_text = upperbloc_text + "\n" +footnote_bloc_text
            
                
        ### when there is no footnote
        else:
            blocs, x_middle, upper_bloc =  find_blocs(clean_page, footnote_top, self.main_size,y1 )

            if blocs is not None:
                ### extract text above the Art. section (no need to combine left and right)
                upperbloc = clean_page.within_bbox((x0, y0, x1, upper_bloc))
                upperbloc_text = upperbloc.extract_text()
                ### extract the Art. section 
                bloc_text = extract_bloc(clean_page, blocs, x_middle, x0, x1)
                page_text = upperbloc_text + "\n" +bloc_text
                
            else:
                upperbloc = clean_page.within_bbox((x0, y0, x1, y1))
                upperbloc_text = upperbloc.extract_text()
                page_text =  upperbloc_text

        return page_text
    
    def loader(self):
        documents = []
        with pdfplumber.open(self.filename) as pdf:
            extract_pages= ""
            num_pages = len(pdf.pages)
            for i in range(num_pages):
                #print(f"Page number {i}")
                page = pdf.pages[i]
                clean_page = page.filter(lambda obj: obj["mcid"]!= None)
                text = self.combine_blocs(clean_page) 
                extract_pages += f"{text}  \n"
                
                
            if extract_pages:
                # Ensure `text=` is used to initialize Document
                doc = Document(text=extract_pages)
                documents.append(doc)

        return documents


class pdf_loader():
    def __init__(self, filename):
        self.filename = filename

    def loader(self):
        documents = []
        with pdfplumber.open(self.filename) as pdf:
            extract_pages= ""
            num_pages = len(pdf.pages)
            for i in range(num_pages):
                page = pdf.pages[i]
                text = page.extract_text()
                extract_pages += f"{text}  \n"
                            
            if extract_pages:
                # Ensure `text=` is used to initialize Document
                doc = Document(text=extract_pages)
                documents.append(doc)
        return documents