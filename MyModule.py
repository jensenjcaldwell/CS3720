import logging
import os
import pandas as pd
from abc import ABC, abstractmethod


LOG_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


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
        logger.info("Loading data from CSV file: %s", self.file_path)
        try:
            data_frame = pd.read_csv(self.file_path)
            logger.info("Data loaded successfully from CSV file: %s", self.file_path)
            return data_frame
        except Exception as e:
            logger.exception("An error occurred while loading the data")
            raise e

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
        print("DataFrame Description:")
        print(self.df.describe(include='all'))
        print("Missing Values in Each Column:")
        print(self.df.isnull().sum())
        print("Number of rows and columns:")
        print(self.df.shape)

    def print_column_stats(self):
        """
        Print statistics for each column in the DataFrame.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        """
        logger.info("Printing column statistics:")
        for column in self.df.columns:
            logger.info("Statistics for column: %s", column)
            logger.info("%s", self.df[column].describe())
        logger.info("Completed printing column statistics.")
            

    def missing_values_summary(self):
        """
        Print a summary of missing values in the DataFrame.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        """
        missing_values = self.df.isnull().sum()
        total_missing = missing_values.sum()
        return total_missing
    
    def column_values_generator(self, column_name):
        """
        Generator function that yields values from a specific column row by row.
        
        Parameters:
        column_name (str): Name of the column to iterate through.
        
        Yields:
        Any: The value in the specified column for each row.
        
        Raises:
        ValueError: If the column name doesn't exist in the DataFrame.
        """
        if column_name not in self.df.columns:
            logger.error("Column '%s' not found in DataFrame", column_name)
            raise ValueError(f"Column '{column_name}' not found in DataFrame. Available columns: {list(self.df.columns)}")

        logger.info("Starting to yield values from column: %s", column_name)
        for index, row in self.df.iterrows():
            yield row[column_name]
        

    def column_pairs_iterator(self, col1, col2):
        """
        Iterate through two columns simultaneously as tuples.
        
        Parameters:
        col1, col2 (str): Names of columns to iterate.
        
        Yields:
        tuple: (value from col1, value from col2).
        """

        if col1 not in self.df.columns or col2 not in self.df.columns:
            logger.error("One or both columns '%s', '%s' not found in DataFrame", col1, col2)
            raise ValueError(f"One or both columns '{col1}', '{col2}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        logger.info("Starting to yield pairs from columns: %s, %s", col1, col2)
        for val1, val2 in zip(self.df[col1], self.df[col2]):
            yield (val1, val2)

    
    
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
        logger.info("Data saved to %s", output_path)
        return output_path




if __name__ == "__main__":
    # Example usage
    file_path = './data/Weather Training Data.csv'  # Replace with your CSV file path
    fetcher_instance = csv_fetcher(file_path)
    df = fetcher_instance.fetch()
    if df is not None:
        analyzer_instance = data_analyzer(df)
        analyzer_instance.df_details()
        print(df.head())  # Display the first few rows of the DataFrame

        example_tracker = 0 # Limit output for demonstration
        for value in analyzer_instance.column_values_generator('MinTemp'):
            if example_tracker >= 5:
                break
            example_tracker += 1
            print(value)  # Example of using the generator

        example_tracker = 0 # Limit output for demonstration
        for value in analyzer_instance.column_pairs_iterator('MinTemp', 'Rainfall'):
            if example_tracker >= 5:
                break
            example_tracker += 1
            print(value)  # Example of using the generator