
from scrapy.http.request import Request

class LimitRequestsMiddleware(object):

    def process_spider_output(self, response, result, spider):
        """
        Queues requests if the number of active selenium requests
        excedes the configured number. Only schedules requests that will
        use selenium in their callbacks. Therefore is important to call
        create requests with alaSpider.selenium_request

        :param response:
        :param result:
        :param spider:
        :return:
        """
        for item in result:
            if not isinstance(item, Request):
                yield item
            else:
                if 'uses_selenium' in item.meta:
                    if spider.active_sel_requests<spider.max_sel_requests:
                        yield item
                        spider.active_sel_requests+=1 #TODO: if the response
                        # fails we will never decrement the value and will
                        # continue scraping with one less browser
                    else:
                        spider.request_queue.put(item)
                else:
                    yield item
