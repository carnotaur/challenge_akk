"""Class for loading and processing dataset."""
from pathlib import Path
import pandas as pd
import numpy as np


class DataLoader:
    """Class for loading and processing dataset."""
    path = Path('data/eGRID2021_data.xlsx')
    needed_columns = [
        'Plant latitude', 'Plant longitude',
        'Plant name', 'Plant state abbreviation'
    ]

    def get_data(self) -> pd.DataFrame:
        """Loads dataset."""
        gen_df_agg = self.__get_net_output_df()
        location_df = self.__get_location_df()
        df = location_df[self.needed_columns]
        df = (
            df.merge(gen_df_agg,
                     on=['Plant name', 'Plant state abbreviation'],
                     how='left')
              .dropna(subset=['Annual net generation (MWh)',
                              'Annual net federal share (%)'])
        )
        df['Annual net generation (MWh)'] = df['Annual net generation (MWh)'].astype(int)
        df['Annual net federal share (%)'] = df['Annual net federal share (%)'].round(4)
        df = (
            df.sort_values(by='Annual net federal share (%)', ascending=False)
              .rename(
                columns={
                    'Plant latitude': 'lat',
                    'Plant longitude': 'lon',
                    'Plant name': 'name',
                    'Plant state abbreviation': 'state'
                }
            )
        )
        return df

    def __get_net_output_df(self) -> pd.DataFrame:
        gen_df = pd.read_excel(self.path, sheet_name='GEN21')
        gen_df = gen_df.drop(0, axis=0)
        gen_df['Generator annual net generation (MWh)'] = (
            gen_df['Generator annual net generation (MWh)'].astype(float).fillna(0)
        )
        gen_df_agg = (
            gen_df.groupby(['Plant name', 'Plant state abbreviation'])
                ['Generator annual net generation (MWh)']
                .sum()
                .replace(0, np.nan)
                .dropna()
                .reset_index()
                .rename(columns={'Generator annual net generation (MWh)':
                                 'Annual net generation (MWh)'})
        )

        total_output = gen_df_agg['Annual net generation (MWh)'].sum()
        gen_df_agg['Annual net federal share (%)'] = (
            gen_df_agg['Annual net generation (MWh)'] / total_output
        )
        return gen_df_agg

    def __get_location_df(self) -> pd.DataFrame:
        location_df = pd.read_excel(self.path, sheet_name='DEMO21')
        location_df = location_df.drop(0, axis=0)
        location_df['Plant latitude'] = location_df['Plant latitude'].astype(float)
        location_df['Plant longitude'] = location_df['Plant longitude'].astype(float)
        return location_df
