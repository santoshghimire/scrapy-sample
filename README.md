# scrapy-sample
Sample code for scrapy that scrapes an audio book website called Librivox.

## Running the scraper
1. Clone this repository.
2. Install requirements `pip install -r requirements.txt`
3. Install mp3val
	a. For Linux: sudo apt-get install mp3val
	b. For Windows: http://mp3val.sourceforge.net/

4. After installation is complete, go to project root and run the crawler
	scrapy crawl librivox --logfile librivox.log