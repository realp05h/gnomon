#################################################                                              
#    ____   ____   ____   _____   ____   ____   #
#   / ___\ /    \ /  _ \ /     \ /  _ \ /    \  #
#  / /_/  >   |  (  <_> )  Y Y  (  <_> )   |  \ #
#  \___  /|___|  /\____/|__|_|  /\____/|___|  / #
# /_____/      \/             \/            \/  #
#                                               #    
######                 by                  ######
     #                                     #
     #            a8888a  888888P dP       #
     #           d8' ..8b 88'     88       #
     #  88d888b. 88 .P 88 88baaa. 88d888b. #
     #  88'  `88 88 d' 88     `88 88'  `88 #
     #  88.  .88 Y8'' .8P      88 88    88 #
     #  88Y888P'  Y8888P  d88888P dP    dP #
     #  88                                 #
     #  dP                                 #
     #######################################


# REPLACE THESE WITH YOU ACTUAL CREDENTIALS 

#AWS E3 Creds:
aws_access_key_id = ''
aws_secret_access_key = ''
region_name = ''  # Ensure this is the correct region for your bucket eg. 'eu-north-1'
#Anthropic API Key:
anthropic_api_key = ''


from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime
from suncalc import get_position
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import shapefile
from shapely.geometry import shape, Point
from rtree import index
import anthropic
import base64
import httpx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

shp = shapefile.Reader("static/shp/countries/ne_110m_admin_0_countries.shp")
shapes = shp.shapes()
records = shp.records()

idx = index.Index()

country_geometries = []
for i, record in enumerate(records):
    country_name = record['NAME']
    geom = shape(shapes[i])
    country_geometries.append((geom, country_name))
    idx.insert(i, geom.bounds)

def find_possible_locations(object_height, shadow_length, date_time):
    angular_resolution = 0.04
    min_lat, max_lat = -60, 85
    min_lon, max_lon = -180, 180

    lats = np.arange(min_lat, max_lat, angular_resolution)
    lons = np.arange(min_lon, max_lon, angular_resolution)

    lons_grid, lats_grid = np.meshgrid(lons, lats)
    valid_lats = lats_grid.flatten()
    valid_lons = lons_grid.flatten()

    pos_obj = get_position(date_time, valid_lons, valid_lats)
    sun_altitudes = pos_obj['altitude']

    expected_shadow_lengths = object_height / np.tan(sun_altitudes)

    valid_indices = (sun_altitudes > 0) & (np.isfinite(expected_shadow_lengths))

    possible_lats = valid_lats[valid_indices]
    possible_lons = valid_lons[valid_indices]
    expected_shadow_lengths = expected_shadow_lengths[valid_indices]

    matching_indices = np.abs(expected_shadow_lengths - shadow_length) < 1e-2
    matching_lats = possible_lats[matching_indices]
    matching_lons = possible_lons[matching_indices]

    return list(zip(matching_lats, matching_lons))

def plot_locations(locations):
    plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, color='white', edgecolor='black')
    ax.add_feature(cfeature.OCEAN, color='black')
    ax.add_feature(cfeature.LAKES, color='black')
    ax.add_feature(cfeature.RIVERS, color='black')

    for lat, lon in locations:
        plt.plot(lon, lat, color='yellow', linestyle='dashed', marker='o', transform=ccrs.PlateCarree())

    plt.title("Possible Locations for Given Shadow Length and Object Height")
    plt.savefig('static/map.png')
    plt.close()

def get_countries_from_locations(locations):
    countries = set()
    for lat, lon in locations:
        point = Point(lon, lat)

        possible_matches = list(idx.intersection(point.bounds))

        for i in possible_matches:
            geom, country_name = country_geometries[i]
            if geom.contains(point):
                countries.add(country_name)
                break

    return list(countries)

def upload_to_s3(file_path, bucket_name, object_name=None):
    s3 = boto3.client('s3', 
                      region_name=region_name,
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, object_name)
        url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}"
        print(f"Upload successful: {url}")
        return url
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except NoCredentialsError:
        print("AWS credentials are not available. Check your configuration.")
        return None
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Ensure all required fields are set.")
        return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def analyze_image_with_claude(image_url, countries):
    image1_media_type = "image/jpeg"
    image1_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
    
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    message = client.messages.create(
       model="claude-3-5-sonnet-20240620",
       max_tokens=1024,
       messages=[
           {
               "role": "user",
               "content": [
                   {
                       "type": "image",
                       "source": {
                           "type": "base64",
                           "media_type": image1_media_type,
                           "data": image1_data,
                       },
                   },
                   {
                       "type": "text",
                       "text": "Your role is an OSINT geography expert. Taking into consideration everything you see in this image please rank and decide a percentage of likelihood that the image was taken in these countries: "
                       f"{', '.join(countries)}. "
                       "Please just return the three most likely countries and area of those countries with a percentage and rationale. Never reiterate the source url of the image."
                   }
               ],
           }
       ],
   )
    return message.content[0].text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('draw', filename=filename))

@app.route('/draw/<filename>')
def draw(filename):
    return render_template('draw.html', filename=filename)

@app.route('/results', methods=['POST'])
def results():
    object_height = float(request.form['heightLength'])
    shadow_length = float(request.form['shadowLength'])
    date_time_str = request.form['dateTime']
    filename = request.form['filename']

    date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')

    locations = find_possible_locations(object_height, shadow_length, date_time)
    plot_locations(locations)
    countries = get_countries_from_locations(locations)

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_url = upload_to_s3(image_path, "gnomontestbucket")

    if image_url:
        gpt_response = analyze_image_with_claude(image_url, countries)
        calculation_results = {
            "locations": locations,
            "countries": countries,
            "gpt_analysis": gpt_response
        }
    else:
        calculation_results = {
            "locations": locations,
            "countries": countries,
            "gpt_analysis": "Failed to upload image for analysis."
        }

    return render_template('results.html', calculations=calculation_results)

if __name__ == '__main__':
    app.run(debug=True)
