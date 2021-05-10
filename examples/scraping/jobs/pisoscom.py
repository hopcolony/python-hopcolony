from hopcolony import jobs
import time, re, json
from selenium.webdriver import ActionChains

class PisosComJob(jobs.Job):
    name = "pisos.com"
    page = 1
    count = 0
    base_url = "https://www.pisos.com/venta/{zone}/{page}"
    
    def __init__(self, *args, **kwargs):
        super(PisosComJob, self).__init__(*args, **kwargs)
        self.entrypoint = self.base_url.format(zone = self.zone, page=self.page)

    def parse(self, response):
        length = len(response.xpath("//div[contains(@class, 'row') and contains(@class, 'clearfix') and @data-listado-row='true']"))

        for prop in response.xpath("//div[contains(@class, 'row') and contains(@class, 'clearfix') and @data-listado-row='true']"):
            detail = prop.xpath("@data-navigate-ref").get()
            response.follow(detail, self.parse_property)

        nxt = response.xpath("//a[@id='lnkPagSig']/@href").get()
        if nxt:
            response.follow(nxt)

    def get_location(self, response, id):
        location = {}

        params = {
            "idPiso": id,
            "ispromotion": response.xpath("//span[@id='dvGuardarFavoritos']/@data-internal-fv-ispromotion").get(),
            "isAggregator": "false",
            "origen": "Pisos",
            "isPrivadoOrRevisarView": "false",
            "cu": "es"
        }
        try:
            r = response.get(f"{response.base}/LazyLoading/MapaSituacion", params = params)
            location_data = r.xpath("//input[@id='staticGoogleMaps']/@value").get().split("/")[-1]
            match = re.match(r"^.*_(?P<radius>.+)_(?P<latitude>.+)@(?P<longitude>.+?)_.+\.gif$", location_data)
            if match:
                location = {
                    "lat": match.group("latitude"),
                    "lon": match.group("longitude")
                }
        except Exception as e:
            pass
        
        return location

    def get_features(self, response):
        features = []
        
        for item in response.xpath("//ul[@class='charblock-list charblock-basics']/li"):
            try:
                [key, value] = item.xpath("span")
            except:
                if "exterior" in item.xpath("span/@class").get():
                    features.append({"key": "exterior", "value": True})
                continue
            key = key.xpath("@class").get()
            value = value.xpath("text()").get().strip()[2:]
            try:
                if "superficieconstruida" in key:
                    key = "built-surface"
                    value = int(value.split()[0])
                elif "superficieutil" in key:
                    key = "useful-surface"
                    value = int(value.split()[0])
                elif "superficiesolar" in key:
                    key = "solar-surface"
                    value = int(value.split()[0])
                elif "numhabitaciones" in key:
                    key = "rooms"
                    value = int(value.split()[0])
                elif "numbanos" in key:
                    key = "bathrooms"
                    value = int(value.split()[0])
                elif "planta" in key:
                    key = "floor"
                    value = value.replace("ª", "")
                elif "estadoconservacion" in key: key = "state"
                elif "tipocasa" in key: key = "type"
                elif "antiguedad" in key: key = "age"
                elif "gastosdecomunidad" in key: key = "community-expenses"
                elif "referencia" in key: key = "reference"
                else: continue
            except:
                continue
            features.append({"key": key, "value": value})
        return features

    def parse_property(self, response):
        self.write(response.raw)
        id = response.xpath("//input[@name='idAnuncio']/@value").get()
        try:
            data = json.loads(response.xpath("//script[@type='application/ld+json']/text()").get(), strict=False)
        except Exception as e:
            name = response.xpath("//div[@class='maindata-info']/h1/text()").get()
            description = response.xpath("//div[@class='description-container description-body']/text()").get().strip()
            price = response.xpath("//div[@class='priceBox-price']/span/text()").get().strip()
            splitted = price.split()
            currency = "UNKNOWN"
            if splitted and splitted[1] == "€":
                currency = "EUR"
            if splitted and price != "A consultar":
                price = int(splitted[0].replace(".", "").replace(",", ""))
            else:
                price = -1
            data = {
                "name": name,
                "description": description,
                "offers": {
                    "price": price,
                    "priceCurrency": currency
                }
            }

            if data["offers"]["price"] is None:
                print(data)

        client_data = response.xpath("//div[@class='owner-data']")
        photos = response.xpath("//input[@id='PhotosPath']/@value").get().split('#,!')
        doc = {
            "clientAlias": client_data.xpath("div[@class='owner-data-info']/a/@title").get(),
            "clientUrl": client_data.xpath("div[@class='owner-data-logo']/a/@href").get(),
            "clientLogo": client_data.xpath("//img[@class='logo']/@data-lazy-img").get(),
            "lastUpdated": client_data.xpath("//div[@class='updated-date']/text()").get().strip(),
            "description": data["description"],
            "detail": response.xpath("//input[@id='hdnUrlAnuncio']/@value").get(),
            "id": id,
            "name": data["name"],
            "location": self.get_location(response, id),
            "features": self.get_features(response),
            "multimedia": [{"type": "image", "src": photo} for photo in photos],
            "phone": response.xpath("//span[@class='number one']/text()").get(),
            "rawPrice": data["offers"]["price"],
            "currency": data["offers"]["priceCurrency"]
        }
        
        self.count += 1
        yield {"index": "pisos.com.properties", "source": doc, "id": id, "count": self.count}
