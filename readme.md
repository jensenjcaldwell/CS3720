# Asignment 1
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
            column_values_generator(column_name): Generator to yield values from a specified column.
            column_pairs_iterator(col1, col2): Generator to yield pairs of values from two specified columns. Useful for comparisons


    DataStore
        Class to handle data storage operations.

        Methods:
            __init__(output_dir): Initialize with output directory path.
            save_csv(df, filename): Save DataFrame to CSV file in the output directory.

        Returns:
            str: Path to the saved file.

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

