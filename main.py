
import MyModule as my_package

if __name__ == "__main__":

    
    # Step 1: Fetch data using csv_fetcher class
    file_path = "data/Weather Training Data.csv" 
    fetcher_instance = my_package.csv_fetcher(file_path)
    df = fetcher_instance.fetch()
    
    if df is not None:
        print(f" Data loaded successfully from {file_path}")
        print(f"  Loaded {len(df)} rows and {len(df.columns)} columns")
        
        # Step 2: Process data using data_analyzer class
        analyzer_instance = my_package.data_analyzer(df)
        
        print("\n--- DataFrame Details ---")
        analyzer_instance.df_details()
        
        print("\n--- Missing Values Summary ---")
        total_missing = analyzer_instance.missing_values_summary()
        print(f"Total missing values across all columns: {total_missing}")
        
        print("\n--- First 5 Rows of DataFrame ---")
        print(df.head())

        example_tracker = 0 # Limit output for demonstration
        for val in analyzer_instance.column_values_generator('MinTemp'):
            if example_tracker >= 5:
                break
            example_tracker += 1
            print(f" MinTemp value: {val}")

        example_tracker = 0 # Limit output for demonstration
        for mintemp, maxtemp in analyzer_instance.column_pairs_iterator('MinTemp', 'MaxTemp'):
            if example_tracker >= 5:
                break
            example_tracker += 1
            print(f" MinTemp: {mintemp}, MaxTemp: {maxtemp}")
            print(f" Difference: {int(maxtemp - mintemp)}")


        

        print("\n--- Data Storage ---")
        try:

            store_instance = my_package.DataStore("output")
            output_file = store_instance.save_csv(df, "processed_weather_data.csv")
            print(f"Data storage completed: {output_file}")
        except AttributeError:  
            print(" DataStore class not found. Skipping data storage step.")

        
    else:
        print(" Data failed to load. Please check the file path.")

