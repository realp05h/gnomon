# GNOMON
A useful OSINT Flask tool for geo-locating images based on the shadows cast from objects

# INSTALLATION

Once you’ve grabbed the repo go ahead and install the required dependencies in your preferred Python environment:

	pip install -r /path/to/requirements.txt 
Get free AWS API creds and create an S3 bucket on AWS (https://aws.amazon.com/s3/). We need a place to upload the images from the app so that the AI has a URL to analyse them from in the final report.  
Generate an API key with Anthropic (https://www.anthropic.com/api) 
Edit the top of the app.py file to include your newly generated creds:
1. aws_access_key_id
2. aws_secret_access_key
3. aws_bucket_name
4. aws_region_name
5. anthropic_api_key

# RUNNING THE FLASK APP	

Now that you have everything in place all you have to do is run the app.py file from the correct directory within your Python environment like so:

	python app.py 	
# USAGE

Once the Flask app is launched, simply navigate here in your browser: http://127.0.0.1:5000

And you will be met with the upload page.

![upload page](https://github.com/realp05h/gnomon/blob/main/example/1.png)
