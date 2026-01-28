import pandas as pd
from abc import ABC, abstractmethod


class fetcher(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
    '''
    Abstract base class for data fetchers.
    '''
    @abstractmethod
    def fetch(self):
        '''
        Abstract method to fetch data.
        
        Parameters:
        file_path (str): The path to the data file.

        Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
        '''
        pass

class csv_fetcher(fetcher):
    def __init__(self, file_path):
        super().__init__(file_path)
    '''
    class to fetch CSV data using pandas.
    
    '''
    def fetch(self):
        """
        Load data from a CSV file into a pandas DataFrame.
        
        Parameters:
        file_path (str): The path to the CSV file.
        
        Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
        """
        try:
            data_frame = pd.read_csv(self.file_path)
            return data_frame
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            return None

class data_analyzer:
    def __init__(self, df):
        self.df = df
    
    def df_details(self):
        """
        Print details about the DataFrame including info, description, missing values, and shape.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        """
        print("DataFrame Info:")
        self.df.info()
        print("\nDataFrame Description:")
        self.df.describe(include='all')
        print("\nMissing Values in Each Column:")
        self.df.isnull().sum()
        print("\nNumber of rows and columns:")
        self.df.shape

    def print_column_stats(self):
        """
        Print statistics for each column in the DataFrame.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        """
        for column in self.df.columns:
            print(f"\nStatistics for column: {column}")
            print(self.df[column].describe())
            

    def missing_values_summary(self):
        """
        Print a summary of missing values in the DataFrame.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        """
        missing_values = self.df.isnull().sum()
        total_missing = missing_values.sum()
        return total_missing
    
class DataStore:
    """
    Class to handle data storage operations.
    
    Demonstrates:
    - Encapsulation: output directory stored as instance variable
    - Single Responsibility: only handles saving/storing data
    """
    def __init__(self, output_dir):
        """
        Initialize DataStore with output directory.
        
        Parameters:
        output_dir (str): Directory path where files will be saved.
        """
        self.output_dir = output_dir
    
    def save_csv(self, df, filename):
        """
        Save DataFrame to CSV file in the output directory.
        
        Parameters:
        df (pd.DataFrame): DataFrame to save.
        filename (str): Name of the output file.
        
        Returns:
        str: Path to the saved file.
        """
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
        return output_path




if __name__ == "__main__":
    # Example usage
    file_path = './data/Weather Training Data.csv'  # Replace with your CSV file path
    fetcher_instance = csv_fetcher(file_path)
    df = fetcher_instance.fetch()
    if df is not None:
        print("Data loaded successfully:")
        analyzer_instance = data_analyzer(df)
        analyzer_instance.df_details()
        print(df.head())  # Display the first few rows of the DataFrame