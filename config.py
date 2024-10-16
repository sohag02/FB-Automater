from configparser import ConfigParser
import csv

config = ConfigParser()
config.read("config.ini")

class Config():
    def __init__(self):
        self.username = self.get_config_value("reel", "target_username")
        self.accounts = int(self.get_config_value("options", "accounts"))
        self.watch_time = int(self.get_config_value("options", "watch_time"))
        self.range = int(self.get_config_value("reel", "range"))
        self.interval = int(self.get_config_value("reel", "interval"))
        self.likes = int(self.get_config_value("options", "likes"))
        self.comments = int(self.get_config_value("options", "comments"))
        self.livestream_link = self.get_config_value("livestream", "livestream_link")
        self.csv_file = self.get_config_value("reel", "csv_file")
        self.use_csv = self.get_config_value("reel", "use_csv")
        self.threads = int(self.get_config_value("reel", "threads"))
        self.post_interval = int(self.get_config_value("post", "interval"))
        self.headless = config.getboolean("settings", "headless", fallback=True)

        # Check if config is valid
        self.check_config()
    
    def get_config_value(self, section, option):
        value = config.get(section, option, fallback=None)
        return value if value else None
    
    def check_config(self):
        if self.username and self.livestream_link:
            print("Either Username or Livestream Link can be used")
            exit()

        if not self.username and not self.livestream_link:
            print("Please Enter Either Username or Livestream Link")
            exit()

        if self.use_csv in ["True", "true", "1", "yes"]:
            self.use_csv = True
            # Get no. of reels from csv
            with open(self.csv_file, "r") as file:
                self.range = len(csv.reader(file))
        else:
            self.use_csv = False
            
        self.likes = self.likes * self.range
        self.comments = self.comments * self.range
        



