  
# Job Scraper

This is a simple Flask application that allows users to upload an HTML file containing job listings. The app extracts the job information and allows users to download the data as a CSV file.

## Installation
1.
   ```bash
   git clone https://github.com/TamarFridman/job-scraper.git
   cd job-scraper
   pip install -r requirements.txt

## Run the app:
2.
   ```bash
   python app.py

Open your browser and go to http://127.0.0.1:5000 to use the app.

## Usage:
Upload an HTML file with job listings,the givem Mock is in the project folder with the name 'mock.html'
The app will extract the job data and show it on the results page.
You can download the extracted data as a CSV file.
