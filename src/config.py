import utils

N = 365 # Number of days to consider
A = 100000 # number of addresses
P = 20 # the number of addresses to analyze in parallel

startTime, endTime = utils.start_end_time()
index = [10**3*(int(startTime) + i*24*60**2) for i in range(N)]
api_key = utils.get_key()["AMBERDATA_API_KEY"]