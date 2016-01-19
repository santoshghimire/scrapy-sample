# scrapy-sample
Sample code for scrapy that scrapes an audio book website called Librivox.

## Running the scraper
1. Clone this repository.
2. Install requirements `pip install -r requirements.txt`
3. Install mp3val
  1. For Linux: `sudo apt-get install mp3val`
  2. For Windows: http://mp3val.sourceforge.net/

4. Go to project root and run the crawler `scrapy crawl librivox --logfile librivox.log`