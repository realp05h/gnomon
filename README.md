# GNOMON
A useful OSINT Flask tool for geo-locating images based on the shadows cast from objects

# INSTALLATION

Once you’ve grabbed the repo go ahead and install the required dependencies in your preferred Python environment:

	pip install -r /path/to/requirements.txt 
Get free AWS API creds and create an S3 bucket on AWS (https://aws.amazon.com/s3/). We need a place to upload the images from the app so that the AI has a URL to analyse them from in the final report. Then go ahead and generate an API key with Anthropic (https://www.anthropic.com/api).

Edit the top of the app.py file to include your newly generated creds:
1. aws_access_key_id
2. aws_secret_access_key
3. aws_bucket_name
4. aws_region_name
5. anthropic_api_key

# RUNNING THE FLASK APP	

Now that you have everything in place, all you have to do is run the app.py file from the correct directory within your Python environment like so:

	python app.py 	
# USAGE

Once the Flask app is launched, simply navigate here in your browser: http://127.0.0.1:5000

And you will be met with the upload page. 

You’ll want to upload images that have a clear and full view of an object (could be a person, lamppost, building, missile on its launchpad… whatever) that’s also casting a clear shadow across as flat a surface as possible. The app results won’t be very accurate if the shadow cast is running down a steep slope or up a hill. Also, it’s preferable if the shadow is as close as possible to a right angle from the object casting it. The app does adjust for acuteness / obtuseness of that angle as perspective from the camera will obviously distort the shadow.  It will normalise the angle to 90°, and in doing so, will lengthen or shorten the values for the shadow’s length relative to the object. If the angle is too extremely acute or obtuse this won’t fully work, though. Play around with photos that have known locations so you can verify the app’s accuracy and so you can get a feel for what kind of images work best.

![gnomon upload page](https://github.com/realp05h/gnomon/blob/main/example/1.png)

Once your file is uploaded, the next to load will be the draw page. 

Follow the instructions to construct your lines.

The example image below was taken on a summer’s day in a deeply rural area of the South West of France (where I was at the time of building this app). It’s a good example for us to use as there is a clear shadow cast at nearly a right angle from the chair. There are also no clearly definable features or landmarks which would  make it easy to identify where this image was taken (we’ll really be putting this app to the test!).

You’ll also need to enter the date and time that the photo was taken as accurately as possible. If you can extract EXIF data from the image, then all good (https://exif.tools/). If you can’t get a time and date for the image, the calculations generated from the shadow will not be accurate and the app’s results will essentially be useless. Although, if you’re pulling the image from certain socials, then in some cases you can be fairly sure that the uplaod time is close to when the image was taken.

Once you have the lines drawn and the date / time entered, go ahead and press ‘Submit’. It can take up to 20s or so to generate the results.

![gnomon draw page](https://github.com/realp05h/gnomon/blob/main/example/2.png)

Now you should be presented with the final results view of the Gnomon app.

The first thing you’ll see is a global projection of possible locations the picture was taken.

![gnomon results page 1](https://github.com/realp05h/gnomon/blob/main/example/3.png)

The app then identifies which countries the ring intersects and sends the image and that country shortlist to Anthropic’s Claude for analysis.

![gnomon results page 2](https://github.com/realp05h/gnomon/blob/main/example/4.png)

