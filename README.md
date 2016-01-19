# scrapy-sample
Sample code for scrapy that scrapes an audio book website called Librivox.

Instructions
- Install python libraries in requirements.txt file by command
	pip install -r requirements.txt
- Install mp3val program
	For Linux: sudo apt-get install mp3val
	For Windows: http://mp3val.sourceforge.net/

- After installation is complete, go to project root and do this
	scrapy crawl librivox --logfile librivox.log