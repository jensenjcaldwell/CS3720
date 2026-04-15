import logging
import os
import multiprocessing as mp
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


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



def _describe_series(series):
    return series.describe()


def _missing_values_for_chunk(df_chunk):
    return df_chunk.isnull().sum()
    

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
        print(f"Total missing values: {total_missing}")
        return total_missing

    def missing_values_summary_parallel(self, processes=None, chunks=4):
        """
        Calculate total missing values in the DataFrame using multiprocessing.
        
        Parameters:
        df (pd.DataFrame): The DataFrame to analyze.
        processes (int): Number of processes to use. If None, uses the number of CPU cores.
        chunks (int): Number of chunks to split the DataFrame into for parallel processing.
        
        Returns:
        int: Total number of missing values in the DataFrame.
        """
        if processes is None:
            processes = mp.cpu_count()
        
        df_chunks  = np.array_split(self.df, chunks)
        with mp.Pool(processes=processes) as pool:
            results = pool.map(_missing_values_for_chunk, df_chunks)
        total_missing = int(sum((chunk.sum() for chunk in results)))
        print(f"Total missing values across all columns (parallel): {total_missing}")
        return total_missing


    def column_describe_parallel(self, columns=None, processes=None):
        if columns is None:
            columns = self.df.columns
        with mp.Pool(processes=processes) as pool:
            results = pool.map(_describe_series, [self.df[col] for col in columns])
        output = dict(zip(columns, results))
        print("Column statistics (parallel):")
        for col, stats in output.items():
            print(f"Statistics for column: {col}")
            print(stats)
        return output
    
    
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

    def column_plotter(self, column_name, location):
        """
        Plot a histogram of the values in a specified column.
        
        Parameters:
        column_name (str): Name of the column to plot.
        location (str): filters the DataFrame to plot only rows where the 'Location' column matches this value.
        
        Raises:
        ValueError: If the column name doesn't exist in the DataFrame.
        """
        if column_name not in self.df.columns:
            logger.error("Column '%s' not found in DataFrame", column_name)
            raise ValueError(f"Column '{column_name}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        logger.info("Plotting histogram for column: %s", column_name)
        if location:
            df_to_plot = self.df[self.df['Location'] == location]
        else:
            df_to_plot = self.df
        plt.hist(df_to_plot[column_name].dropna(), bins=20, edgecolor='black')
        plt.title(f'Histogram of {column_name}{" for " + location if location else ""}')
        plt.xlabel(column_name)
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.75)
        plt.show()

    def column_scatter_plot(self, col1, col2):
        """
        Plot a scatter plot of two specified columns.
        
        Parameters:
        col1, col2 (str): Names of columns to plot.
        
        Raises:
        ValueError: If one or both column names don't exist in the DataFrame.
        """
        if col1 not in self.df.columns or col2 not in self.df.columns:
            logger.error("One or both columns '%s', '%s' not found in DataFrame", col1, col2)
            raise ValueError(f"One or both columns '{col1}', '{col2}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        logger.info("Plotting scatter plot for columns: %s, %s", col1, col2)
        plt.scatter(self.df[col1], self.df[col2], alpha=0.5)
        plt.title(f'Scatter Plot of {col1} vs {col2}')
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.grid()
        plt.show()

    def totals_by_location(self, column_name):
        """
        Calculate and print the total of a specified column grouped by location.
        
        Parameters:
        column_name (str): Name of the column to sum.
        
        Raises:
        ValueError: If the column name doesn't exist in the DataFrame.
        """
        if column_name not in self.df.columns:
            logger.error("Column '%s' not found in DataFrame", column_name)
            raise ValueError(f"Column '{column_name}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        totals = self.df.groupby('Location')[column_name].sum()
        plt.bar(totals.index, totals.values, color='skyblue')
        plt.title(f'Total {column_name} by Location')
        plt.xlabel('Location')
        plt.ylabel(f'Total {column_name}')
        plt.grid(axis='y', alpha=0.75)
        plt.xticks(rotation=90)
        plt.show()


    
    
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
    
class Predictor():
    """
    Class to handle machine learning prediction using scikit-learn models.
    
    Demonstrates:
    - Encapsulation: model stored as instance variable
    - Single Responsibility: only handles making predictions
    """

    def __init__(self, data, model):
        """
        Initialize Predictor with a machine learning model.
        
        Parameters:
        data (pd.DataFrame): DataFrame containing the features for prediction.
        model: A trained machine learning model with a predict method.
        """
        self.data = data
        self.model = model
        self.training_feature_columns_ = None

    def build_previous_two_day_features(self, feature_columns, group_column='Location', sort_columns=None, drop_missing_history=True):
        """
        Create lagged feature columns for the previous two days.

        Parameters:
        feature_columns (list[str]): Columns to convert into 1-day and 2-day lag features.
        group_column (str | None): Column used to separate independent weather histories.
            Defaults to 'Location' so one city's history is not mixed with another.
        sort_columns (list[str] | str | None): Optional columns used to order rows before creating lags.
            If omitted, the current row order is used.
        drop_missing_history (bool): When True, remove rows that do not have a full two-day history.

        Returns:
        pd.DataFrame: Data with additional lag columns.
        """
        if not feature_columns:
            raise ValueError("feature_columns must contain at least one column name.")

        missing_columns = [column for column in feature_columns if column not in self.data.columns]
        if missing_columns:
            raise ValueError(
                f"Columns not found in DataFrame: {missing_columns}. Available columns: {list(self.data.columns)}"
            )

        if group_column is not None and group_column not in self.data.columns:
            raise ValueError(
                f"Group column '{group_column}' not found in DataFrame. Available columns: {list(self.data.columns)}"
            )

        if sort_columns is None:
            normalized_sort_columns = []
        elif isinstance(sort_columns, str):
            normalized_sort_columns = [sort_columns]
        else:
            normalized_sort_columns = list(sort_columns)

        missing_sort_columns = [column for column in normalized_sort_columns if column not in self.data.columns]
        if missing_sort_columns:
            raise ValueError(
                f"Sort columns not found in DataFrame: {missing_sort_columns}. Available columns: {list(self.data.columns)}"
            )

        feature_data = self.data.copy()

        if group_column is not None:
            sort_by = [group_column, *normalized_sort_columns] if normalized_sort_columns else [group_column]
        else:
            sort_by = normalized_sort_columns

        if sort_by:
            feature_data = feature_data.sort_values(by=sort_by, kind='mergesort').reset_index(drop=True)
        else:
            feature_data = feature_data.reset_index(drop=True)

        lag_columns = []
        for column in feature_columns:
            first_lag_name = f"{column}_prev_day_1"
            second_lag_name = f"{column}_prev_day_2"

            if group_column is not None:
                grouped_column = feature_data.groupby(group_column, sort=False)[column]
                feature_data[first_lag_name] = grouped_column.shift(1)
                feature_data[second_lag_name] = grouped_column.shift(2)
            else:
                feature_data[first_lag_name] = feature_data[column].shift(1)
                feature_data[second_lag_name] = feature_data[column].shift(2)

            lag_columns.extend([first_lag_name, second_lag_name])

        if drop_missing_history:
            feature_data = feature_data.dropna(subset=lag_columns).reset_index(drop=True)

        logger.info("Built previous two day features for columns: %s", feature_columns)
        return feature_data

    def build_tomorrow_prediction_input(self, feature_columns, location, group_column='Location', sort_columns=None):
        """
        Build a single-row feature frame for predicting tomorrow from the latest two rows.

        Parameters:
        feature_columns (list[str]): Base columns whose lagged values should be included.
        location (str): Location to predict for.
        group_column (str): Column used to filter the requested location.
        sort_columns (list[str] | str | None): Optional columns used to order rows before selecting the last two.

        Returns:
        pd.DataFrame: Single-row DataFrame ready for predict_max_temp_tomorrow.
        """
        if not feature_columns:
            raise ValueError("feature_columns must contain at least one column name.")

        if group_column not in self.data.columns:
            raise ValueError(
                f"Group column '{group_column}' not found in DataFrame. Available columns: {list(self.data.columns)}"
            )

        missing_columns = [column for column in feature_columns if column not in self.data.columns]
        if missing_columns:
            raise ValueError(
                f"Columns not found in DataFrame: {missing_columns}. Available columns: {list(self.data.columns)}"
            )

        if sort_columns is None:
            normalized_sort_columns = []
        elif isinstance(sort_columns, str):
            normalized_sort_columns = [sort_columns]
        else:
            normalized_sort_columns = list(sort_columns)

        missing_sort_columns = [column for column in normalized_sort_columns if column not in self.data.columns]
        if missing_sort_columns:
            raise ValueError(
                f"Sort columns not found in DataFrame: {missing_sort_columns}. Available columns: {list(self.data.columns)}"
            )

        location_data = self.data[self.data[group_column] == location].copy()
        if len(location_data) < 2:
            raise ValueError(f"Location '{location}' needs at least two rows to build a tomorrow prediction.")

        if normalized_sort_columns:
            location_data = location_data.sort_values(by=normalized_sort_columns, kind='mergesort').reset_index(drop=True)
        else:
            location_data = location_data.reset_index(drop=True)

        latest_row = location_data.iloc[-1]
        previous_row = location_data.iloc[-2]

        prediction_row = {}
        for column in feature_columns:
            prediction_row[f"{column}_prev_day_1"] = latest_row[column]
            prediction_row[f"{column}_prev_day_2"] = previous_row[column]

        prediction_row[group_column] = location
        prediction_frame = pd.DataFrame([prediction_row])
        logger.info("Built tomorrow prediction input for location: %s", location)
        return prediction_frame

    def train_sklearn_max_temp_model(
        self,
        feature_columns,
        target_column='MaxTemp',
        group_column='Location',
        sort_columns=None,
        include_group_column=True,
        model=None,
    ):
        """
        Train a scikit-learn regression pipeline to predict max temperature from the previous two days.

        Parameters:
        feature_columns (list[str]): Base weather columns whose previous two days should be used as predictors.
        target_column (str): Numeric column to predict. Defaults to 'MaxTemp'.
        group_column (str | None): Column used to keep independent weather histories separate.
        sort_columns (list[str] | str | None): Optional columns used to order rows before building lags.
        include_group_column (bool): When True, include the group column as a categorical model feature.
        model: Optional scikit-learn regressor. If omitted, uses HistGradientBoostingRegressor.

        Returns:
        tuple: (trained scikit-learn pipeline, training DataFrame with lag features)
        """
        from sklearn.compose import ColumnTransformer
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder

        if target_column not in self.data.columns:
            raise ValueError(
                f"Target column '{target_column}' not found in DataFrame. Available columns: {list(self.data.columns)}"
            )

        model_feature_columns = list(feature_columns)
        if target_column not in model_feature_columns:
            model_feature_columns.append(target_column)

        training_data = self.build_previous_two_day_features(
            feature_columns=model_feature_columns,
            group_column=group_column,
            sort_columns=sort_columns,
            drop_missing_history=True,
        )
        training_data = training_data.dropna(subset=[target_column]).reset_index(drop=True)
        if training_data.empty:
            raise ValueError("No rows remain for training after building lag features and dropping missing targets.")

        lag_feature_columns = []
        for column in model_feature_columns:
            lag_feature_columns.append(f"{column}_prev_day_1")
            lag_feature_columns.append(f"{column}_prev_day_2")

        categorical_feature_columns = []
        if include_group_column and group_column is not None:
            categorical_feature_columns.append(group_column)

        self.training_feature_columns_ = lag_feature_columns + categorical_feature_columns
        X = training_data[self.training_feature_columns_]
        y = training_data[target_column]

        transformers = [
            (
                'numeric',
                Pipeline([('imputer', SimpleImputer(strategy='median'))]),
                lag_feature_columns,
            )
        ]

        if categorical_feature_columns:
            transformers.append(
                (
                    'categorical',
                    Pipeline(
                        [
                            ('imputer', SimpleImputer(strategy='most_frequent')),
                            ('encoder', OneHotEncoder(handle_unknown='ignore')),
                        ]
                    ),
                    categorical_feature_columns,
                )
            )

        estimator = model if model is not None else HistGradientBoostingRegressor(random_state=42)
        self.model = Pipeline(
            [
                ('preprocessor', ColumnTransformer(transformers=transformers)),
                ('model', estimator),
            ]
        )
        self.model.fit(X, y)
        logger.info("Trained scikit-learn max temperature model using features: %s", self.training_feature_columns_)
        return self.model, training_data


    def predict_max_temp_tomorrow(self, X):
        """
        Predict the maximum temperature for tomorrow using the trained model.
        
        Parameters:
        X (pd.DataFrame): Feature data for making predictions.
        
        Returns:
        np.ndarray: Predicted maximum temperatures.
        """
        predictions = self.model.predict(X)
        logger.info("Predictions made successfully.")
        return predictions

    

    





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
        '''
        # Example of plotting a column
        analyzer_instance.column_plotter('MinTemp', "Sydney")

        # Example of plotting a scatter plot
        analyzer_instance.column_scatter_plot('MinTemp', 'MaxTemp')

        # Example of totals by location
        analyzer_instance.totals_by_location('Rainfall')

        '''
        analyzer_instance.column_describe_parallel()
        analyzer_instance.missing_values_summary_parallel()
        analyzer_instance.missing_values_summary()