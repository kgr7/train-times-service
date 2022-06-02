import json
import aiohttp
import logging
from datetime import datetime
import azure.functions as func
from bs4 import BeautifulSoup as soup

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    arr = req.params.get("arr")
    dep = req.params.get("dep")
    headers = {"Content-Type": "application/json"}

    if not arr or not dep:
        error_response = {"Error": "Bad Request: param arr or dep missing"}
        return func.HttpResponse(json.dumps(error_response), headers=headers, status_code=400)

    ddmmyy = datetime.now().strftime("%d%m%y")
    hhmm = datetime.now().strftime("%H%M")

    async with aiohttp.ClientSession() as client:
        async with client.get(f"https://ojp.nationalrail.co.uk/service/timesandfares/{dep}/{arr}/{ddmmyy}/{hhmm}/dep") as response:
            page_soup = soup(await response.text(), "html.parser")
            trip_json_tags = page_soup.find_all("td", {"class": "fare"})
            trips_json = [json.loads(trip.script.text.strip()) for trip in trip_json_tags]

            response = []
            for trip in trips_json:
                dep = trip["jsonJourneyBreakdown"]["departureStationCRS"]
                arr = trip["jsonJourneyBreakdown"]["arrivalStationCRS"]
                dep_time = trip["jsonJourneyBreakdown"]["departureTime"]
                response.append({"dep": dep, "arr": arr, "dep_time": dep_time})

            return func.HttpResponse(json.dumps(response), headers=headers, status_code=200)
