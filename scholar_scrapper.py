from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import re
import requests
import uuid
from requests.exceptions import Timeout
from app import db_makale_ekle, db_makale_kontrol
from pdf_parser import anahtar_kelime_bul, doi_bul, kaynakca_bul, ozet_bul, pdf_to_text


pool1 = ThreadPoolExecutor(4)


cookies = {
    'AEC': 'Ae3NU9PBA-8IBGNV-hTHyKa1AdESfcQr0n0pjnJZn-ej0D_pw7RohxaKUw',
    #'1P_JAR': '2024-03-09-14',
    'NID': '512=CaiWNGFvCHjK-6vbehLwfXdPZqK6UuepKXRgYFGChN_v79a1Q9LjLru075R-_ObvtwYHg1slM6fWkNw18JVigxq_6hroOrTK2jpJ62aMmX8VxojrOI8DRZ0GQ42awAm66oiDEeTpxu7Lu2gaijQiWdTn_AP5aYuWsc6dR3Akyq-4PhzFJPsBacr7ovjeaKhX8F23HhdYezI9IZO9riPeNLJK0SSUb54pY8EA',
    'GSP': 'A=_lNGWw:CPTS=1710000170:LM=1710000170:S=MAfDVCEzORLIlyHd'
}


def google_scrapper(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }

    response = requests.get(url,cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    #print(str(soup))
    input_element = soup.find('input', {'id': 'gs_hdr_tsi'})
    search_query = input_element['value']
    search_query=search_query[0:(len(search_query)-13)]

    articles = []

    for item in soup.select('[data-lid]'):
        # print("* makale kodu: "+item.select('a')[0]['data-clk-atid'])
        #article_g_id=item.select('a')[0]['data-clk-atid']  
        related_articles_link = item.select_one('a[href*=related]')
        kod=related_articles_link['href']
        article_g_id=kod[19:kod.find("scholar.google")-1]
        print(article_g_id)
        title = item.select('h3')[0].get_text()
        print(title)
        title_clear= title.replace("[HTML][HTML] ", "").replace("[KİTAP][B] ", "").replace("[PDF][PDF] ", "").replace("[ALINTI][C] ", "")
        page_link = item.select('a')[1]['href']
        article_link = item.select('a')[0]['href']
        description = item.select('.gs_rs')[0].get_text().replace("… ","").replace("… ","")
        info= item.select('.gs_a')[0].get_text()


        print("ALTTADİR--------------------")
        yazar=""

        if "-" in info:
            yazar = (info[0:info.find("-")])
        else:
            yazar=info
        

        yazar=yazar.replace("…","")

        if yazar[-1]==" ":
            yazar=yazar[:-1]

        
        print("yazar:")
        print(yazar)

        print("yil:")
        yil=[""]
        temp_yil= re.findall(r'\b\d{4}\b', info)
        if temp_yil:
            yil=temp_yil
        
        yayin_yili=str(yil[0])
        print(yayin_yili)

        dergi=""
        

        if "-" in info:
            dergi_temp = (info[info.find("-")+2:])

        ti1=dergi_temp.rfind(",")

        print("temP"+dergi_temp+"temP")


        if ti1 !=-1:
            dergi=dergi_temp[0:ti1].replace("… ","").replace(" …","").replace("…","")
        else:
            dergi=""


        print("islenmemis dergi:"+dergi+":")


        if len(dergi)>0:
            dergi=dergi.rstrip()



        


        print("dergi")
        print(":"+dergi+":")
        print("ÜSTTEDİR------------------------")


        cites_link = item.select_one('.gs_fl.gs_flb a[href*=cites]')
        citation_count = cites_link.get_text() if cites_link else "0"
        citation_count_clear = ''.join([harf for harf in citation_count if harf.isdigit()])

        articles.append({
            "gid":article_g_id,
            "başlık": title_clear,
            "yazar": yazar.rstrip(),
            "dergi":dergi,
            "yil":yayin_yili,
            "sayfa linki": page_link,
            "makale linki": article_link,
            "açıklama": description,
            "bilgi":info,
            "alıntı sayısı": citation_count_clear,
            "arama sorgusu":search_query
        })

    pool1.submit(google_downloader, articles)

    return articles




def google_downloader(articles):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    for article in articles:
        try:

            if db_makale_kontrol(article["gid"]) and (article["makale linki"].startswith("htt") or article["makale linki"].startswith("ww")):
                response = requests.get(article["makale linki"],headers=headers, timeout=6)
                if (response.content.startswith(b'%PDF')):
                    _filename="pdf/" + article["başlık"] + "-" + str(uuid.uuid4()) + ".pdf"
                    with open(_filename, 'wb') as f:
                        f.write(response.content)

                    article["indirme linki"]=_filename
                    metin=pdf_to_text(_filename)
                    article["kaynakca"]=kaynakca_bul(metin)
                    article["doi"]=doi_bul(metin)
                    article["ozet"]=ozet_bul(metin)
                    article["anahtar"]=anahtar_kelime_bul(metin)
                    db_makale_ekle(article)
                else:
                    print(f"%PDF ile URL başlamıyor: {article['makale linki']}")
        except requests.Timeout:
            print(f"İstek zaman aşımına uğradı: {article['makale linki']}")
        except Exception as e:
            print(f"Hata oluştu: {e}")






