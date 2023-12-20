import streamlit as st
import pandas as pd
import plotly.express as px

from preprocessing import DataLoader


class App:
    """App frontend."""
    # Custom CSS to set the background color to white
    custom_css = """
    <style>
    body {
        background-color: #ffffff; /* White background color */
    }
    </style>
    """
    max_plants = 200

    def run(self):
        """Create frontend for app"""
        df = self.__get_data()
        unique_states = df['state'].unique()

        # Display the custom CSS
        st.markdown(self.custom_css, unsafe_allow_html=True)
        selected_states = st.multiselect(
            'Select State(s)', 
            unique_states,
            default=unique_states
        )
        top_plants = st.slider('Select Top N', min_value=1,
                               max_value=self.max_plants, value=10, step=1)
        filtered_df = df[df['state'].isin(selected_states)].head(top_plants)
        fig = self.__update_scatter_plot(filtered_df)
        st.plotly_chart(fig)

    def __update_scatter_plot(self, filtered_df: pd.DataFrame):
        fig = px.scatter_geo(
            filtered_df,
            lat='lat',
            lon='lon',
            text='name',
            color='state',
            scope='usa',
            hover_data={'Annual net generation (MWh)': ':,.0f',
                        'Annual net federal share (%)': ':,.2%'},
            title='Interactive Map with State Filter'
        )
        fig.update_layout(
            font=dict(color='black')
        )
        return fig

    def __get_data(self):
        if not hasattr(self, 'data'):
            data_loader = DataLoader()
            df = data_loader.get_data()
            setattr(self, 'data', df)
        return getattr(self, 'data')


if __name__ == '__main__':
    app = App()
    app.run()
