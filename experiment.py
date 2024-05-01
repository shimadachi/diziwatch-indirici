from site_interaction import Api
import time


api = Api()
api.go_site()
api.go_series("Jujutsu Kaisen")
links = api.get_episode_links()
api.download_series(links)
# time.sleep(5)
api.driver_quit()
