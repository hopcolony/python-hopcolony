from hopcolony_core import jobs
import time, re, json
from selenium.webdriver import ActionChains

class SolviaJob(jobs.Job):
    name = "solvia"
    page = 1
    count = 0
    base_url = "https://www.solvia.es/es/oportunidades-inmobiliarias?tipoOperacion={operacion}&idCategoriaTipoVivienda={tipoVivienda}&idProvincia={idProvincia}&viewMode=MAP&numeroPagina=0&registrosPorPagina=30"
    
    def __init__(self, *args, **kwargs):
        super(SolviaJob, self).__init__(*args, **kwargs)
        self.entrypoint = self.base_url.format(operacion = self.operacion, tipoVivienda = self.tipoVivienda, idProvincia = self.idProvincia)

    def get_transfer_state(self, response):
        try:
            data = {}
            scripts = response.xpath("//script")
            for script in scripts:
                if bool(re.match(r"^window\['TRANSFER_STATE'\].*", script.xpath("text()").get())):
                    data = re.search(r"window\['TRANSFER_STATE'\] = (.*)", script.xpath("text()").get())
                    data = json.loads(data.group(1).replace("\\\\", "/"))
                    break
            return data
        except Exception as e:
            print(e)
            return {}

    def parse(self, response):
        data = self.get_transfer_state(response)
        # The only way to get the lat and lon is to look at the map points and then query the property by it's id.
        for prop in data["POST-/api/inmuebles/v2/buscarInmueblesGeolocalizados-1-null-null"]["propiedades"]:
            # self.write(prop, extension="json")
            try:
                print(self.count)
                self.count+=1
                # r = response.post("https://www.solvia.es/api/inmuebles/v1/buscarInmuebles", json = {"idVivienda": prop["idVivienda"]})
                # data = json.loads(r.raw.replace("\\\\", "/"))["resultado"]
                # prop = data[0]
                # print(prop)

                # self.write(data, extension="json")
            except Exception as e:
                print(e)
            # return
