import os
import logging
import pandas as pd
from flask import Flask, request, render_template, jsonify,session,send_file
from bs4 import BeautifulSoup
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set of the secret key

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s [%(levelname)s] - %(message)s",  
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler("app.log", mode="a")  
    ]
)

# Function that validate the HTML structure
def validate_html(html_content):
    issues = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for the <title> tag
    if not soup.title:
        issues.append("Missing <title> tag in <head>.")
    else:
        logging.info("Title tag found: %s", soup.title.string)
    
    # Check for job listing structure
    job_listings = soup.find("div", class_="job-listings")
    if not job_listings:
        issues.append("Missing <div class='job-listings'> container.")
    else:
        jobs = job_listings.find_all("div", class_="job")
        if not jobs:
            issues.append("No job entries found in <div class='job-listings'>.")
        else:
            for job in jobs:
                if not job.find(class_="title"):
                    issues.append("Job entry missing title.")
                if not job.find(class_="company"):
                    issues.append("Job entry missing company.")
                if not job.find(class_="location"):
                    issues.append("Job entry missing location.")
                if not job.find("a", class_="apply"):
                    issues.append("Job entry missing apply link.")

    # Log the issues
    for issue in issues:
        logging.warning(issue)
    return issues

# Function that extract job data
def extract_job_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    job_listings = soup.find("div", class_="job-listings")
    jobs = []
    
    if job_listings:
        for job in job_listings.find_all("div", class_="job"):
            title = job.find(class_="title").string if job.find(class_="title") else "N/A"
            company = job.find(class_="company").string if job.find(class_="company") else "N/A"
            location = job.find(class_="location").string if job.find(class_="location") else "N/A"
            apply_link = job.find("a", class_="apply")['href'] if job.find("a", class_="apply") else "N/A"
            jobs.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Apply Link": apply_link,
            })
    return jobs

# Route for uploading and processing the file
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Check if the file was uploaded
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        # Ensure that it's an HTML file
        if not file.filename.endswith(".html"):
            return "Invalid file type. Please upload an HTML file.", 400
        
        # I would add check that the html has no syntax errors 

        # Read and process the HTML file
        html_content = file.read().decode("utf-8")
        
        # Validate of the HTML
        validation_issues = validate_html(html_content)

        # Extract job data and convert to pandas df
        job_json=extract_job_data(html_content)
        
        job_df = pd.DataFrame(job_json)
        
        # Render of the table as HTML
        job_table = job_df.to_html(classes="table table-striped custom-table", index=False, escape=False)
        
        session['job_data'] = job_json

        # Render of the results page
        return render_template(
            'results.html', 
            validation_issues=validation_issues, 
            job_table=job_table
        )

    # Render upload form
    return render_template('index.html')


# Route that download CSV from saved json data in session
@app.route("/download_csv")
def download_csv():
    # Retrieve job data from session
    job_data_json = session.get('job_data', None)

    if not job_data_json:
        return "No job data available", 400

    # Convert of JSON to DataFrame
    job_df = pd.DataFrame(job_data_json)
 
    # Creataion of CSV in memory
    csv_output = BytesIO()
    job_df.to_csv(csv_output, index=False)
    csv_output.seek(0)  # Go to the start of the StringIO object

    # Clean of the session
    session.pop('job_data', None)

    # Send the CSV as a response for download
    return send_file(csv_output, mimetype='text/csv', as_attachment=True, download_name='job_data.csv')


if __name__ == "__main__":
    app.run(debug=True)
