import os
from flask import Flask, abort, render_template, request, send_file
from flask_pymongo import PyMongo
from elasticsearch import Elasticsearch



es = Elasticsearch(
    hosts=["http://127.0.0.1:9200"], 
    api_key=""
)

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/pyscrape"
mongo = PyMongo(app)


@app.route('/getir', methods=['GET'])
def get_articles():
    makale_adi = request.args.get('makale_adi')
    yazar = request.args.get('yazar')
    tur = request.args.get('tur')
    yil = request.args.get('yil')
    yayin_yeri = request.args.get('yayin_yeri')
    arama_sorgusu = request.args.get('arama_sorgusu')
    anahtar_kelimeler = request.args.get('anahtar')
    ozet = request.args.get('ozet')
    referanslar = request.args.get('kaynakca')
    alinti_sayisi = request.args.get('alinti_sayisi')
    doi = request.args.get('doi')
    sirala = request.args.get('sirala')

    query = {
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    bayrak=False
    if makale_adi:
        query["query"]["bool"]["must"].append({"match": {"baslik": makale_adi}})
        bayrak=True
    if yazar:
        query["query"]["bool"]["must"].append({"match": {"yazar": yazar}})
        bayrak=True
    if tur:
        query["query"]["bool"]["must"].append({"match": {"tur": tur}})
    if yil:
        query["query"]["bool"]["must"].append({"match": {"yil": yil}})
        bayrak=True
    if yayin_yeri:
        query["query"]["bool"]["must"].append({"match": {"yayin_yeri": yayin_yeri}})
        bayrak=True
    if arama_sorgusu:
        query["query"]["bool"]["must"].append({"match": {"arama_sorgusu": arama_sorgusu}})
        bayrak=True
    if anahtar_kelimeler:
        query["query"]["bool"]["must"].append({"match": {"anahtar": anahtar_kelimeler}})
        bayrak=True
    if ozet:
        query["query"]["bool"]["must"].append({"match": {"ozet": ozet}})
        bayrak=True
    if referanslar:
        query["query"]["bool"]["must"].append({"match": {"kaynakca": referanslar}})
        bayrak=True
    if alinti_sayisi:
        query["query"]["bool"]["must"].append({"match": {"alinti_sayisi": alinti_sayisi}})
        bayrak=True
    if doi:
        query["query"]["bool"]["must"].append({"match": {"doi": doi}})
        bayrak=True

    
    if bayrak!=True:
        query = {
            "query": {
                "match_all": {}  
        },
            "size": 10000 
        }

    print("------------------------------------------------------------------")
    print(query)

    res = es.search(index="search-makale", body=query)

    girdiler = res['hits']['hits']

    return render_template('sonuclar.html', girdiler=girdiler)



@app.route('/bilgi/<str_id>')
def db_makale_kontrol(str_id):
    item = mongo.db.makaleler.find_one({"google_id": str_id})
    if item:
        return render_template('bilgi.html', item=item)
    else:
        return "404"

cursor=0
def db_makale_ekle(article):
    mongo.db.makaleler.insert_one({
    "google_id": article["gid"],
    "baslik": article["başlık"],
    "yazar": article["yazar"],
    "tur": "makale",
    "yil": article["yil"],
    "yayin_yeri": article["dergi"],
    "arama_sorgusu": article["arama sorgusu"],
    "anahtar": article["anahtar"],
    "ozet": article["ozet"],
    "kaynakca": article["kaynakca"],
    "alinti_sayisi": article["alıntı sayısı"],
    "doi": article["doi"],
    "makale_linki": article["makale linki"],
    "indirme_linki": article["indirme linki"],
    "aciklama": article["açıklama"]
    })

def db_makale_kontrol(str_id):
    count = mongo.db.makaleler.count_documents({"google_id": str_id})
    if count>0:
        return False
    else:
        return True



@app.route('/')
def home():
    return render_template('main.html')

@app.route('/ara')
def search_page():
    return render_template('ara.html')

@app.route('/scrape', methods=['GET'])
def kazi_tusu():
    if request.method == 'GET':
        search_query = request.args.get('search_query')

        cursor=request.args.get('cursor')
        
        if search_query:
            from scholar_scrapper import google_scrapper
            articles = google_scrapper(f"https://scholar.google.com/scholar?start={cursor}&q={search_query} filetype:pdf")
            return render_template('main.html', articles=articles, cursor=cursor,search_query=search_query)
        else:
            return render_template('main.html', articles=None)
    else:
        return "Unsupported request method"
    

@app.route('/pdf/<variable>')
def generate_pdf(variable):
    file_path = f'pdf/{variable}'
    if not os.path.exists(file_path):
        return "Böyle bir dosya yok"
    return send_file(file_path, as_attachment=False)


if __name__ == "__main__":
    
    app.run(debug=True)
