import collections
import pdfplumber 
import re

    
def find_footnote_bloc(page, main_size, sidetext_size):
    
    # Extract characters with detailed metadata
    characters = page.chars
    
    # Group characters by mcid
    mcid_to_characters = {}
    for char in characters:
        mcid = char["mcid"]
        if mcid is not None:
            if mcid not in mcid_to_characters:
                mcid_to_characters[mcid] = []
            mcid_to_characters[mcid].append(char)
    
    # Filter out groups where not all characters have sizes less than 9
    #print(mcid_to_characters)
    filtered_mcid_to_characters = {
        mcid: chars 
        for mcid, chars in mcid_to_characters.items()
        if all(round(char["size"]) < main_size for char in chars) and not all(round(char["size"], 2) <= sidetext_size for char in chars)}
 
    #print(f"filtered_mcid_to_characters{filtered_mcid_to_characters}")
    if not filtered_mcid_to_characters:
        return None
    mcid_f = sorted(filtered_mcid_to_characters.keys())[0]
    top_position = min(char['top'] for char in filtered_mcid_to_characters[mcid_f])  
    return top_position



def find_blocs(page,top_position,main_size, y_max):
    
    pattern = re.compile(r'\bArt\.')
    arts = page.search(pattern)
    x_middle = 0
    y_s = []

    ### find all the blocs containing "ART. "
    if arts:
        for c in arts:
            #print(c)
            try: 
                if all([c["chars"][i]["fontname"]== 'BCDFEE+TimesNewRomanPS-BoldMT' and c["chars"][i]["size"]==main_size for i in range(len(c["chars"]))]):
                    y_s.append(c["top"])
                    if c["x0"]>x_middle:
                        x_middle = c["x0"]  
            except:
                raise ValueError
            
    ### return a list of y axis value associated with each bloc
    if y_s: 
        y_s.sort()
        blocs = [] 
        for i in range(len(y_s)-1):
            blocs.append((y_s[i], y_s[i+1]))

        if top_position is not None:
            blocs.append((y_s[-1], top_position))
        else:
            if y_s[-1]< y_max: 
                blocs.append((y_s[-1], y_max))  
            else:
                raise ValueError
        
        upper_bloc =  y_s[0]
        return blocs, x_middle, upper_bloc
    else:
        return None, None, None


def extract_bloc(page, blocs, x_middle,x_min, x_max):
    texts = ""
    for bloc in blocs:
        
        left = page.within_bbox((x_min,bloc[0], x_middle, bloc[1]),relative=True, strict=True)
        #print(f"leftbox:{(0,bloc[0],x_A, bloc[1])}")
        #print(f"leftbox text: {left.extract_text()}")
        right = page.within_bbox(( x_middle,bloc[0],x_max, bloc[1]),relative=True, strict=True)
        #print(f"rightbox:{(x_A,bloc[0],x_max, bloc[1])}")
        #print(f"rightbox text: {right.extract_text()}")
        right_text = right.extract_text().strip().split("\n")
        right_text.insert(1, left.extract_text().strip())
        texts+= f"{"\n".join(right_text)} \n"

    return texts


