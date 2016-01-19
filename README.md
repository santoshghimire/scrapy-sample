# scrapy-sample
Sample code for scrapy that scrapes an audio book website called Librivox.

Instructions
1) Install python libraries in requirements.txt file by command
pip install -r requirements.txt
2) Install mp3val program
For Linux: sudo apt-get install mp3val
For Windows: http://mp3val.sourceforge.net/

3) After installation is complete, go to project root and do this
scrapy crawl librivox --logfile librivox.log