import fitz
import re

def pdf_to_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    pdf_document.close()

    return text


def kaynakca_bul(metin):

    kaynakca=""
    i_1=-1
    i_2=-1

    for aranan in ["KAYNAKLAR","Kaynaklar","Kaynakça","KAYNAKÇA","REFERANSLAR","Referanslar" ,"References", "REFERENCES","Références","DİPNOT","Dipnot"]:
        i_1 = metin.rfind(aranan)
        if i_1 != -1:
            i_1 += (len(aranan)+1)
            break

    for add in ["EKLER","Ekler","ÖZGEÇMİŞ"]:
        i_2 = metin.rfind(add)
        if i_2 != -1:
            break
    
    if i_1 != -1:
        kaynakca=metin[i_1:i_2]
    
    return re.sub(r'\n\s*\n', '\n', kaynakca, flags=re.MULTILINE)


def doi_bul(metin):

    doi=""

    doi_pattern = r'10\.\d{4,}/[\w./-]+'

    doi_list = re.findall(doi_pattern, metin)

    if doi_list:
        doi=doi_list[0]

    return doi


def ozet_bul(metin):

    ozet_i1=-1
    ozet_i2=-1
    abst=""

    for aranan in ["Özet: ","Özet:","Özet\n","ÖZET","Öz","ÖZ","Abstract\n","Abstract: ","Abstract:","ABSTRACT"]:
        ozet_i1 = metin.find(aranan)
        if ozet_i1 != -1:
            ozet_i1 =ozet_i1+(len(aranan))
            break

    if ozet_i1>0:
        for aranan in ["Anahtar","ANAHTAR","Keywords","GİRİŞ","Giriş","Introduction","INTRODUCCIÓN"]:
            ozet_i2 = metin.find(aranan)
            if ozet_i2 != -1:
                abst=metin[ozet_i1:ozet_i2]
                break

    return re.sub(r'\n\s*\n', '\n', abst, flags=re.MULTILINE)


def anahtar_kelime_bul(metin):
    ozet_i1=-1
    ozet_i2=-1
    keys=""

    for aranan in ["Anahtar Kelimeler: ","Anahtar kelimeler:","Anahtar kelimeler ","Anahtar Kelimeler ","Keywords: ","Keywords:","Keywords " ,"Keywords"]:
        ozet_i1 = metin.find(aranan)
        if ozet_i1 != -1:
            ozet_i1 =ozet_i1+(len(aranan))
            break


    if ozet_i1>0:
        ozet_i2 = metin.find("\n", ozet_i1)
        keys=metin[ozet_i1:ozet_i2]

    return keys





