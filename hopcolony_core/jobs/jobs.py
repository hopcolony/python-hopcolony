import logging, requests, re
from urllib.parse import urlparse
from parsel import Selector

class Job:
    entrypoint = None
    def __init__(self, *args, **kwargs):
        # Set the input args as attributes to the job
        self.__dict__.update(kwargs)

        self.logger = logging.getLogger(self.name)
        logging.basicConfig(level=logging.INFO, format='%(message)s')

class Engine:
    last_get = None

    def __init__(self, job, pipelines):
        self.job = job
        self.pipelines = pipelines
        assert job.entrypoint, "Please provide an entrypoint"
    
    def get(self, url, callback = None):
        assert self.last_get != url, f"You're trying to follow an url you have just visited: {url}"
        self.last_get = url

        parse_callback = self.job.parse
        if callback:
            parse_callback = callback
        
        try:
            data = requests.get(url)
        except requests.exceptions.ConnectionError:
            self.job.logger.error(f"Could not get a connection with \"{url}\"")
            return
            
        response = JobResponse(self, data)
        try:
            for item in parse_callback(response):
                # Send to pipelines
                for pipeline in self.pipelines:
                    item = pipeline.process_item(item, self.job)
        except TypeError as e:
            # Probably returning nothing from parse method
            pass
        
    def start(self):
        response = self.get(self.job.entrypoint)

class JobResponse:
    def __init__(self, engine, response):
        self.engine = engine
        self.url = response.url
        parsed_uri = urlparse(self.url)
        self.base = f"{parsed_uri.scheme}://{parsed_uri.netloc}/"
        self.status = response.status_code
        self.raw = response.text
        self.selector = Selector(text=self.raw)
        
    def css(self, query):
        return self.selector.css(query)

    def xpath(self, query):
        return self.selector.xpath(query)
        
    def follow(self, endpoint, callback):
        url = self.base + endpoint
        if re.match(r"http.*", endpoint):
            url = endpoint
        self.engine.get(url, callback)
