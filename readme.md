# Asignment
This project uses weather data to observe and predict weather trends

## Data souces

All data was sourced from the Kaggle Australia Weather Data set and can be found [here](https://www.kaggle.com/datasets/arunavakrchakraborty/australia-weather-data)

## Classes

    fetcher (ABC)
        Abstract base class for data fetchers.

        Methods:
            __init__(file_path): Initialize with file path.
            fetch(): Abstract method to fetch data. Must be implemented by subclasses.

    csv_fetcher(fetcher)
        Class to fetch CSV data using pandas. Inherits from fetcher.

        Methods:
            __init__(file_path): Initialize with file path.
            fetch(): Load data from a CSV file into a pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.

    data_analyzer
        Class to analyze and process DataFrame data.

        Methods:
            __init__(df): Initialize with a DataFrame to analyze.
            df_details(): Print details about the DataFrame including info, description, missing values, and shape.
            print_column_stats(): Print statistics for each column in the DataFrame.
            missing_values_summary(): Calculate total missing values in the DataFrame.
            missing_values_summary_parallel(processes=None, chunks=4): Calculate total missing values using multiprocessing for large datasets.
            column_describe_parallel(processes=None, chunks=4): Compute descriptive statistics for each column in parallel using multiprocessing.
            column_scatter_plot(col1, col2): Create a scatter plot to visualize the relationship between two columns.
            totals_by_location(column_name): Create a bar chart showing total values by location for a specified column.
            column_values_generator(column_name): Generator to yield values from a specified column.
            column_pairs_iterator(col1, col2): Generator to yield pairs of values from two specified columns. Useful for comparisons


    DataStore
        Class to handle data storage operations.

        Methods:
            __init__(output_dir): Initialize with output directory path.
            save_csv(df, filename): Save DataFrame to CSV file in the output directory.

        Returns:
            str: Path to the saved file.
    
    Predictor
        Class to handle weather prediction tasks using scikit-learn.

        Methods:
            __init__(data, model): Initialize Predictor with a DataFrame and optional trained model.
            build_previous_two_day_features(feature_columns, group_column='Location', sort_columns=None, drop_missing_history=True): Build lagged feature columns from the previous two days for each selected weather variable.
            build_tomorrow_prediction_input(feature_columns, location, group_column='Location', sort_columns=None): Build a single-row feature set for predicting tomorrow's weather for a specific location using its latest two rows of data.
            train_sklearn_max_temp_model(feature_columns, target_column='MaxTemp', group_column='Location', sort_columns=None, include_group_column=True, model=None): Train a scikit-learn regression pipeline to predict tomorrow's maximum temperature from two-day lag features.
            predict_max_temp_tomorrow(X): Use the trained scikit-learn model to predict tomorrow's maximum temperature.

        Returns:
            pd.DataFrame: For lag-building helper methods that generate model-ready features.
            tuple: For model training, returns the trained pipeline and the training DataFrame with lag features.
            np.ndarray: For prediction, returns the predicted maximum temperatures.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries.

## Design Choices and Architecture

The application follows a modular architecture with three main components:

    1. Data Fetching Layer (fetcher, csv_fetcher):
       - Chose an abstract base class to define a common interface for all fetchers
       - This allows easy extension to other data sources (API, JSON, databases) without changing other parts of the code
       - Used inheritance to create specific implementations while maintaining a consistent interface

    2. Data Processing Layer (data_analyzer):
       - Encapsulates the DataFrame and all analysis methods in one class
       - Chose to store the DataFrame as an instance variable (self.df) so methods can operate on the same data
       - This keeps related functionality together and prevents passing the DataFrame around constantly

    3. Data Storage Layer (DataStore):
       - Separate class for saving/persisting data
       - Chose to make output directory configurable via constructor to support different output locations
       - Keeps storage logic separate from analysis logic (Single Responsibility Principle)



## Implementing OOP principles

Several OOP principles were implemented in this project, including:

    inheritance: The csv_fetcher class inherits from the abstract base class fetcher, allowing it to implement the fetch method defined in the base class, this also makes it easy to add more fetcher types in the future by simply creating new subclasses of fetcher.
    
    abstraction: The fetcher class serves as an abstract base class, defining a common interface for all data fetchers. This abstraction allows users to interact with different fetcher implementations without needing to know the details of how each one works.
    
    encapsulation: The data_analyzer class encapsulates the DataFrame as an instance variable (self.df), keeping the data and the methods that operate on it together. This protects the data and provides a clean interface for analysis operations.
    
    polymorphism: Different fetcher subclasses (once implemented) can be used interchangeably since they all implement the same fetch() interface defined in the abstract base class. This allows the code to work with any type of fetcher without modification.
    
    decoration: The @abstractmethod decorator is used to indicate that the fetch method in the fetcher class must be implemented by any subclass. This enforces a contract for subclasses, ensuring they provide their own implementation of the fetch method.

    super(): The super() function is used in the csv_fetcher class to call the constructor of the base class fetcher. This ensures that the base class is properly

    constructor initialized when creating an instance of the subclass.

    Method Overriding: The fetch method in the csv_fetcher class overrides the abstract fetch method defined in the fetcher base class. This allows the subclass to provide a specific implementation for fetching CSV data.

    Single Responsibility Principle: Each class has a single responsibility. The fetcher class is responsible for defining the interface for data fetching, the csv_fetcher class is responsible for fetching CSV data, and the data_analyzer class is responsible for analyzing DataFrame data. This separation of concerns makes the code easier to maintain and understand.


## Implementation of Generators
    Generators were implemented in the data_analyzer class to efficiently handle large datasets. By using generators, we can iterate over large DataFrames without loading the entire dataset into memory at once. This is particularly useful for operations like calculating column statistics or processing rows of data, where we can yield one item at a time instead of returning a complete list. This approach reduces memory consumption and improves performance when working with big data.

## Logging
    Logging was implemented throughout the code, logs are saved to the output/app.log file. This is helpful for troubleshooting and understanding the flow of the application. Key events such as data fetching, analysis steps, and errors are logged.

## Testing
    Unit tests were written using pytest to test the csv_fetcher, data_analyzer, and DataStore classes. The tests cover various scenarios, including valid and invalid file paths for csv_fetcher, analysis of DataFrame details and missing values in data_analyzer, and saving DataFrames to CSV files in DataStore. The tests ensure that the classes behave as expected and handle edge cases appropriately.

## Data Visualization
    Data visualization was implemented in the data_analyzer class using matplotlib. The column_scatter_plot method creates scatter plots to visualize relationships between two columns, while the totals_by_location method generates bar charts to show total values by location. These visualizations help users understand trends and patterns in the weather data more effectively. Some test cases were added to the module to demonstrate the functionality of these visualization methods. These include showing total rainfall by location, plotting the relationship between minimum and maximum temperatures, and a histogram of rainfall distribution for a specific location.

## Multiprocessing
    Multiprocessing was implemented in the data_analyzer class to speed up the analysis of large datasets. The missing_values_summary_parallel method uses the multiprocessing module to divide the DataFrame into chunks and process them in parallel, significantly reducing the time taken to calculate missing values across large datasets. This is particularly beneficial when working with extensive weather data, allowing for faster insights and analysis. Additionally the column_describe_parallel method was implemented to compute descriptive statistics for each column in parallel, further enhancing the performance of data analysis tasks.

## Adapting Data Analysis for PySpark
    PySpark was added to make the same analysis workflow work better for larger datasets. Instead of reading files with pandas, data is loaded with Spark's DataFrameReader using schema inference. Analysis logic was updated to use pyspark.sql.functions so Spark can handle optimization and parallel execution automatically, replacing the need for manual multiprocessing. For sampling and iteration-style tasks, Spark actions such as .limit() and .collect() are used when needed. This keeps the project structure similar while improving scalability beyond what a single machine's memory can support.

## Web Application
    A web application was developed using Flask to provide a user-friendly interface for uploading weather data files and performing analysis. The application allows users to select different types of analysis (descriptive statistics, missing values summary, histograms, scatter plots, and bar charts) through a dropdown menu. The results of the analysis are displayed on the webpage, and users can also download the results as CSV files. This web interface makes it easier for users who may not be comfortable with command-line tools to interact with the data and gain insights from it.

    The required packages for the web application can be found in the requirements.txt file, which includes Flask for the web framework, SQLAlchemy for database interactions (if needed), and other libraries for data analysis and visualization. 

    To launch the web application, users can run the WebApp.py script, which will start the Flask development server. The application can then be accessed through a web browser at the specified local address (e.g., http://localhost:5000).

## Predictive Modeling
    A predictive modeling component was implemented using scikit-learn to predict tomorrow's maximum temperature from the previous two days of weather data. The Predictor class now includes helper methods for building two-day lag features, preparing a single prediction row for a selected location, training a regression pipeline, and generating predictions. The current implementation uses lagged weather measurements such as temperature, humidity, pressure, rainfall, cloud cover, and wind speed, along with location information, so the project can move beyond analysis into forecast-style modeling.
