import schedule
import time
from update_analysis import UpdateAnalysis

schedule.every().day.at("16:00").do(UpdateAnalysis)

while True:
    schedule.run_pending()
    time.sleep(60)