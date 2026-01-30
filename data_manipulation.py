import asyncio

import pandas as pd
import matplotlib.pyplot as plt
import pycountry_convert as pcc


class data_init(object):
    "Ready the dataset from a csv file"

    def __init__(self, csv_data):

        # No preprocessing needed for these 3
        self.processed_df = csv_data[[
            'Rank', 'Cost Index', 'Purchasing Power Index']]

        # Clean country column and insert it in to the new df
        self.processed_df.insert(
            1, 'Country', self.preprocess_country(csv_data['Country']))

        # Add continent labels for each country entry
        self.processed_df.insert(
            2, 'Continent', self.create_continent_list(self.processed_df['Country']))

        # One df for the unmodified data (exluding preprocessing)
        # And one where the monthly in come is at 1:100 scale
        self.chart_df = self.processed_df.copy()
        self.chart_df.insert(
            3, 'Monthly Income', self.preprocess_monthly_income(csv_data['Monthly Income']))

        self.chart_df_scaled = self.processed_df.copy()
        self.chart_df_scaled.insert(
            3, 'Monthly Income 1:100', self.cleaned_income.div(100), True)


    def preprocess_monthly_income(self, csv_data, is_scaled: bool = False):
        "Logic for monthly income column preprocessing"

        self.cleaned_income = csv_data.str.strip(
            "USD").str.replace(',', '').astype(float)

        return self.cleaned_income


    def preprocess_country(self, csv_data):
        "Logic for country column preprocessing"

        cleaned_country = csv_data.str.strip("*")
        cleaned_country = cleaned_country.str.strip(" ")

        return cleaned_country


    def create_continent_list(self, countries):
        "Create a new list with continent labels for each country"

        continent_list = []
        for x in countries:
            try:
                y = pcc.country_name_to_country_alpha2(x)
                continent_list.append(pcc.country_alpha2_to_continent_code(y))
            except:
                continent_list.append("Uncategorised")

        return continent_list


class chart_types(data_init):

    def __init__(self, csv_data):
        super().__init__(csv_data)
        

    def choose_chart_params(self):
        "Set chart parameters"

        # Choose whether or not to use the 1:100 scale monthly income column
        if input("Use scaled dataset? y / n: ") in ('y','Y','yes','Yes'):
            data_source = self.chart_df_scaled
        else:
            data_source = self.chart_df

        if input('Specify continent? y / n: ') in ('y','Y','yes','Yes'):
            data_source = self.format_continent_data(data_source)
        
        # A dictionary used when choosing data sources for each axis
        # Values are the column names in the dataframe
        # Key values stored as string to work with input()
        self.available_columns = {str(key): value for key, value in
                                  zip(range(len(data_source.columns)), data_source.columns)}

        chart_type = input("Choose chart type 'l': line, 's': scatter: ")

        match chart_type:

            case 'l' | 'line' | 'Line':

                # If y axis is not specified all columns get plotted
                if input("Specify Y-axis? y / n: ") in ('y','Y','yes','Yes'):
                    self.set_axis_params(['x', 'y'])
                    self.plot_linechart(data_source, True)
                else:
                    self.set_axis_params(['x'])
                    self.plot_linechart(data_source)

            case 's' | 'scatter' | 'Scatter':

                self.set_axis_params(['x', 'y'])
                self.plot_scatter(data_source)

            case _:

                print('Invalid chart type, defaulting to line chart')
                self.set_axis_params(['x', 'y'])
                self.plot_linechart(data_source)


    def set_axis_params(self, used_axis):
        """
         Set x and y axis sources from the columns in the dataframe.
         If valid column is not provided default to first and second in the dataframe
        """

        # Set x and y axis sources from the columns in the dataframe
        # If valid column is not provided default to first and second in the dataframe
        # To do add some logic to handle cases where there are no (or only 1) columns present
        if 'x' in used_axis:
            try:

                # Access specific column label value {v} with it's key {k} (between 0-n)
                # ''.join(), for loop fuckery just so the format is easier to read. 
                # Simply prints the dict keys & values and adds newline after each item in the dict
                print('Choose X column')
                self.x_axis = self.available_columns[input(''.join(f'{k}: {v} \n' for k,v in self.available_columns.items()))]
            except:
                self.x_axis = list(self.available_columns.values())[0]

        if 'y' in used_axis:
            try:
                print('Choose Y column')
                self.y_axis = self.available_columns[input(''.join(f'{k}: {v} \n' for k,v in self.available_columns.items()))]
            except:
                self.y_axis = list(self.available_columns.values())[1]


    def format_continent_data(self, data_source):
        "If continent is specified create new dataframe with only entries form that specific continent"

        # Dictionary with unique continent labels from the original dataframe
        # Keys are their order of apppearence stored string to work with input()
        continents = {str(key): value for key, value in
                                zip(range(data_source['Continent'].nunique()), data_source['Continent'].drop_duplicates())}
        
        # Access specific continent label value {v} with it's key {k} (between 0-n)
        # ''.join(), for loop fuckery just so the format is easier to read. 
        # Simply prints the dict keys & values and adds newline after each item in the dict
        continent_dataframe = data_source[data_source.Continent == continents[input(''.join(f'{k}: {v} \n' for k,v in continents.items()))]]
        
        # Not needed as theres no point in visualising it if only one continent is available
        continent_dataframe = continent_dataframe.drop('Continent', axis=1)

        return continent_dataframe


    def plot_linechart(self, data_source, use_y: bool = False):

        if not use_y:
            data_source.plot(x=self.x_axis, figsize=(10, 7))
        else:
            data_source.plot(x=self.x_axis, y=self.y_axis, figsize=(10, 7))


    def plot_scatter(self, data_source):

        data_source.plot.scatter(x=self.x_axis, y=self.y_axis, figsize=(10, 7))


def main():

    csv_data = pd.read_csv('scrapped_data.csv')
    chart_test = chart_types(csv_data)
    chart_test.choose_chart_params()
    if input('Create another chart y/n: ') == 'y':
        main()
    

main()
plt.show()
