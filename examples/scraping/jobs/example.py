class ExampleJob(jobs.Job):
    name = "example"
    def __init__(self, *args, **kwargs):
        super(ExampleJob, self).__init__(*args, **kwargs)
        self.entrypoint = f"https://news.ycombinator.com/news?p={self.initial_page}"

    def parse(self, response):
        yield from response.css('a.storylink::text').getall()

        next_page = response.css('a.morelink::attr(href)').get()
        if next_page is not None:
            response.follow(next_page)