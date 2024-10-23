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

        # user id
        self.user_id = self.get_config_value("reel", "user_id")

        # proxy
        self.use_proxy = config.getboolean('proxy', 'use_proxy', fallback=False)
        if self.use_proxy:
            self.rotating_proxies = config.getboolean('proxy', 'rotating_proxies', fallback=False)
            if self.rotating_proxies:
                self.host = config.get('proxy', 'host', fallback=None)
                self.port = config.get('proxy', 'port', fallback=None)
                self.proxy_username = config.get('proxy', 'username', fallback=None)
                self.proxy_password = config.get('proxy', 'password', fallback=None)
            else:
                self.proxy_file = config.get('proxy', 'proxy_file', fallback=None)

        # Search properties
        self.use_search = config.getboolean('search', 'use_search', fallback=False)
        if self.use_search:
            self.keywords = config.get('search', 'keywords', fallback=None).split(',')
            self.scroll_time = config.getint('search', 'scroll_time', fallback=None)
            self.profile_name = config.get('search', 'profile_name', fallback=None)

        # Proxy properties
        self.use_proxy = config.getboolean('proxy', 'use_proxy', fallback=False)
        if self.use_proxy:
            self.rotating_proxies = config.getboolean('proxy', 'rotating_proxies', fallback=False)
            if self.rotating_proxies:
                self.host = config.get('proxy', 'host', fallback=None)
                self.port = config.get('proxy', 'port', fallback=None)
                self.proxy_username = config.get('proxy', 'username', fallback=None)
                self.proxy_password = config.get('proxy', 'password', fallback=None)
            else:
                self.proxy_file = config.get('proxy', 'proxy_file', fallback=None)

        # Group Member extracter
        self.group_username = config.get('group', 'username', fallback=None)

        # Check if config is valid
        self.check_config()
    
    def get_config_value(self, section, option):
        value = config.get(section, option, fallback=None)
        return value or None
    
    def check_config(self):
        if self.username and self.livestream_link:
            print("Either Username or Livestream Link can be used")
            self.livestream_link = None

        if self.username and self.user_id:
            print("Either Username or User ID can be used")
            self.username = None

        # if not self.username and not self.livestream_link and not self.user_id:
        #     print("Please Enter Either Username, User ID or Livestream Link")
        #     exit()

        if self.use_csv in ["True", "true", "1", "yes"]:
            self.use_csv = True
            # Get no. of reels from csv
            with open(self.csv_file, "r") as file:
                self.range = len(csv.reader(file))
        else:
            self.use_csv = False
            
        self.likes = self.likes * self.range
        self.comments = self.comments * self.range
        
if __name__ == "__main__":
    config = Config()
    print(config.username)
    print(config.livestream_link)
    print(config.user_id)


