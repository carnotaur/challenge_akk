"""Process and save image dataset."""
from pathlib import Path
import pandas as pd
from PIL import Image
import numpy as np
from sqlalchemy import create_engine

# Create SQLAlchemy database engine
engine = create_engine('sqlite:///colored_images.db')


class ImageProcessor:
    """Process and save image dataset."""
    data_path = Path('../data/AIQ - Backend Engineer Assignment - Data .csv')
    new_col_width = 150
    def __init__(self):
        df = pd.read_csv(self.data_path)
        self.df = df.dropna()
        self.number_rows = self.df.shape[0]

    def __resize_image(self, image_array):
        image_pillow = Image.fromarray(image_array)
        resized_image_pillow = image_pillow.resize((150, self.number_rows),
                                                   Image.NEAREST)
        resized_image = np.array(resized_image_pillow)
        return resized_image

    def process_and_store_image(self) -> pd.DataFrame:
        """process and save image"""
        image_array = self.df.drop('depth', axis=1).values
        resized_image = self.__resize_image(image_array)
        resized_image_df = pd.DataFrame(resized_image,
                                        columns=[f'col_{idx}' for idx in range(self.new_col_width)])
        resized_image_df['depth'] = self.df['depth']

        # Store the colored image in the database
        resized_image_df.to_sql('image_table', con=engine, index=False, if_exists='replace')
        return resized_image_df


if __name__ == '__main__':
    # Initialize ImageProcessor
    image_processor = ImageProcessor()

    # Process and store the image in the database
    image_processor.process_and_store_image()
