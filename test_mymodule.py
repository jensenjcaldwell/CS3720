import pytest
from MyModule import fetcher, csv_fetcher, data_analyzer, DataStore

def test_csv_fetcher():
    # Test with a valid file path
    valid_file_path = "data/Weather Training Data.csv"
    csv_fetcher_instance = csv_fetcher(valid_file_path)
    df = csv_fetcher_instance.fetch()
    assert df is not None, "DataFrame should not be None for a valid file path"
    assert len(df) > 0, "DataFrame should contain rows for a valid file path"

    # Test with an invalid file path
    invalid_file_path = "data/non_existent_file.csv"
    csv_fetcher_instance_invalid = csv_fetcher(invalid_file_path)
    with pytest.raises(Exception):
        csv_fetcher_instance_invalid.fetch()

def test_data_analyzer():
    # Create a sample DataFrame for testing
    import pandas as pd
    data = {
        'MinTemp': [10, 12, 8, None, 15],
        'MaxTemp': [20, 22, 18, 25, None]
    }
    df = pd.DataFrame(data)
    
    analyzer_instance = data_analyzer(df)
    
    # Test missing_values_summary method
    total_missing = analyzer_instance.missing_values_summary()
    assert total_missing == 2, "Total missing values should be 2"
    
    # Test column_values_generator method
    min_temp_values = list(analyzer_instance.column_values_generator('MinTemp'))
    expected_min = [10, 12, 8, None, 15]
    import pandas as _pd
    for actual, exp in zip(min_temp_values, expected_min):
        if exp is None:
            assert _pd.isna(actual), "Expected missing value (NaN)"
        else:
            assert actual == exp, f"Expected {exp}, got {actual}"

    # Test column_pairs_iterator method
    pairs = list(analyzer_instance.column_pairs_iterator('MinTemp', 'MaxTemp'))
    expected_pairs = [(10, 20), (12, 22), (8, 18), (None, 25), (15, None)]
    for (a1,a2), (e1,e2) in zip(pairs, expected_pairs):
        if e1 is None:
            assert _pd.isna(a1), "Expected NaN in first element of pair"
        else:
            assert a1 == e1
        if e2 is None:
            assert _pd.isna(a2), "Expected NaN in second element of pair"
        else:
            assert a2 == e2, f"Expected {e2}, got {a2}"

def test_data_store():

    # Create a sample DataFrame for testing
    import pandas as pd
    data = {
        'MinTemp': [10, 12, 8],
        'MaxTemp': [20, 22, 18]
    }
    df = pd.DataFrame(data)
    
    # Test DataStore class (use the correct class name)
    output_dir = "test_output"
    store_instance = DataStore(output_dir)
    
    output_file = store_instance.save_csv(df, "test_weather_data.csv")
    
    import os
    assert os.path.exists(output_file), "Output file should exist after saving"
    
    # Clean up test output file
    os.remove(output_file)
    os.rmdir(output_dir)

if __name__ == "__main__":
    pytest.main()
