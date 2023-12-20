"""Flask app."""
import io
from flask import Flask, jsonify, request, send_file
from sqlalchemy import create_engine
import pandas as pd
from PIL import Image
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import numpy as np

from image_processor import ImageProcessor


# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///colored_images.db'


engine = create_engine('sqlite:///colored_images.db')


def apply_colormap(image_array, cmap_name='plasma') -> np.array:
    """Add colormap to numpy array."""
    normalized_image = Normalize()(image_array)
    colormap = plt.get_cmap(cmap_name)
    image_colored = colormap(normalized_image)
    image_colored = image_colored[:, :, :3]
    return image_colored

# API endpoint to retrieve the last colored image from the database
@app.route('/retrieve_colored_image', methods=['GET'])
def retrieve_colored_image() -> np.array:
    """
    Retrive colored image based min_depth and max_depth.
    """
    # Create a session
    min_depth = request.args.get('min_depth')
    max_depth = request.args.get('max_depth')
    query = f"""
        SELECT *
        FROM image_table
        WHERE depth < {max_depth} AND depth > {min_depth}
    """
    print('WOW' * 10)
    image_df = pd.read_sql(query, con=engine)
    image_array = image_df.drop('depth', axis=1).values
    colored_image = apply_colormap(image_array)
    # Convert image data to BytesIO object
    image_pillow = Image.fromarray((colored_image * 255.).astype(dtype=np.uint8))

    # Convert the Image object to a BytesIO stream
    image_stream = io.BytesIO()
    image_pillow.save(image_stream, format='JPEG')
    image_stream.seek(0)
    image_pillow.save('image.png')
    # Send the image as a response
    return send_file(image_stream, mimetype='image/jpeg', download_name='image.jpg')


if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True)
