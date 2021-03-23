from hopcolony_core import jobs
import time, re, json
from selenium.webdriver import ActionChains

class FotocasaJob(jobs.Job):
    name = "fotocasa"
    selenium = True
    page = 1
    base_url = "https://www.fotocasa.es/es/comprar/viviendas/{type}/{zone}/l/{page}"
    
    def __init__(self, *args, **kwargs):
        super(FotocasaJob, self).__init__(*args, **kwargs)
        self.entrypoint = self.base_url.format(type = self.type, zone = self.zone, page=self.page)

    @property
    def next(self):
        self.page += 1
        return self.base_url.format(type = self.type, zone = self.zone, page = self.page)

    def write(self, response):
        with open(f"{self.page}.json", "w") as f:
            f.write(response.raw)

    def get_initial_props(self, response):
        try:
            data = {}
            scripts = response.xpath("//script")
            script = [script.get_attribute("innerText") for script in scripts if bool(re.match(r"^window\.__INITIAL_DATA__.*", script.get_attribute("innerText").strip()))]
            if script:
                data = re.search(r'window\.__INITIAL_PROPS__ = JSON\.parse\("(.*)"\)', script[0].strip())
                data = data.group(1).replace("\\\"", "\"").replace("\\\"", "\"")
                data = json.loads(data)
            return data
        except Exception as e:
            print(e)
            return {}

    def parse(self, response):
        try:
            data = self.get_initial_props(response)

            retries = 0
            while "initialSearch" not in data and retries < 3:
                time.sleep(0.2)
                data = self.get_initial_props(response)
                retries += 1
            if retries >= 3:
                print(f"Not able to parse page {self.page}. Reloading")
                self.write(response)
                # Reload same page until we get the data. We will get an exception if we repeat the
                # same page more than 3 times
                response.follow(response.url)
                return

            properties = data["initialSearch"]["result"]["realEstates"]
            for prop in properties:
                prop["location"] = prop.pop("coordinates")
                prop["location"]["lat"] = prop["location"].pop("latitude")
                prop["location"]["lon"] = prop["location"].pop("longitude")
                prop["location"].pop("accuracy")

                yield {"index": "fotocasa.properties", "source": prop, "id": prop["id"]}

            if properties:
                response.follow(self.next)
                
        except Exception as e:
            print("Exception occurred: " + str(e))
            self.write(response)