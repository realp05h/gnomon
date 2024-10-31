# GNOMON
A useful OSINT Flask tool for geo-locating images based on the shadows cast from objects

# INSTALLATION

Once you’ve grabbed the repo go ahead and install the required dependencies in your preferred Python environment:

	pip install -r /path/to/requirements.txt 
Get free AWS API creds and create an S3 bucket on AWS (https://aws.amazon.com/s3/). We need a place to upload the images from the app so that the AI has a URL to analyse them from in the final report. Then go ahead and generate an API key with Anthropic (https://www.anthropic.com/api) 
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

You’ll want to upload images that have a clear and full view of an object (could be a person, lamppost, building, missile on its launchpad… whatever) that’s also casting a clear shadow across as flat a surface as possible. It won’t work if the shadow cast is running down a steep slope or up a hill. Also, it’s preferable if the shadow is as close as possible to a right angle from the object casting it. The app does adjust for acuteness / obtuseness of that angle as perspective from the camera will obviously distort the shadow.  It will normalise the angle to 90°, and in doing so, will lengthen or shorten the values for the shadow’s relative length. If the angle is too extremely acute or obtuse this won’t fully work. Play around with photos that have known locations so you can verify the apps accuracy and so you can get a feel for what kind of images work best.

![gnomon upload page](https://github.com/realp05h/gnomon/blob/main/example/1.png)

Once your file is uploaded, the next to load will be the draw page. 

Follow the instructions to construct your lines.

![gnomon draw page](https://github.com/realp05h/gnomon/blob/main/example/2.png)

