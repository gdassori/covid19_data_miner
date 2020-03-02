from influxdb import InfluxDBClient

from covid_data_miner import settings
from covid_data_miner.repository import InfluxDataRepository
import time

from covid_data_miner.service.csse_points_service import CSSEGISandDataPointsService

csse_points_service = CSSEGISandDataPointsService(settings.GITHUB_API_KEY)
points_repository = InfluxDataRepository(
    InfluxDBClient(host=settings.INFLUXDB_HOST, port=settings.INFLUXDB_PORT)
)

if __name__ == '__main__':
    now = int(time.time()) - 686400*60
    points = csse_points_service.get_points_since(now)
    points_repository.save_historical_points(*points)
