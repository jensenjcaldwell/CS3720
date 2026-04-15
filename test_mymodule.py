import pytest
from MyModule import csv_fetcher, data_analyzer, DataStore, Predictor

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

    # Test parallel missing values summary
    total_missing_parallel = analyzer_instance.missing_values_summary_parallel(processes=2, chunks=2)
    assert total_missing_parallel == 2, "Total missing values from parallel method should be 2"
    
    # Test parallel column describe
    output = None
    output = analyzer_instance.column_describe_parallel()
    assert output is not None, "Output from column_describe_parallel should not be None"

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

def test_predictor_build_previous_two_day_features():
    import pandas as pd

    df = pd.DataFrame(
        {
            'Location': ['A', 'A', 'A', 'B', 'B', 'B'],
            'DayNumber': [1, 2, 3, 1, 2, 3],
            'MaxTemp': [20, 22, 25, 15, 16, 18],
            'MinTemp': [10, 11, 13, 7, 8, 9],
        }
    )

    predictor = Predictor(df, model=None)
    lagged_df = predictor.build_previous_two_day_features(
        feature_columns=['MaxTemp', 'MinTemp'],
        group_column='Location',
        sort_columns='DayNumber',
    )

    assert len(lagged_df) == 2, "Only rows with two full previous days should remain"

    first_row = lagged_df.iloc[0]
    assert first_row['Location'] == 'A'
    assert first_row['DayNumber'] == 3
    assert first_row['MaxTemp_prev_day_1'] == 22
    assert first_row['MaxTemp_prev_day_2'] == 20
    assert first_row['MinTemp_prev_day_1'] == 11
    assert first_row['MinTemp_prev_day_2'] == 10

    second_row = lagged_df.iloc[1]
    assert second_row['Location'] == 'B'
    assert second_row['DayNumber'] == 3
    assert second_row['MaxTemp_prev_day_1'] == 16
    assert second_row['MaxTemp_prev_day_2'] == 15

def test_predictor_build_previous_two_day_features_missing_column():
    import pandas as pd

    df = pd.DataFrame({'Location': ['A', 'A'], 'MaxTemp': [20, 22]})
    predictor = Predictor(df, model=None)

    with pytest.raises(ValueError):
        predictor.build_previous_two_day_features(feature_columns=['MissingColumn'])

def test_predictor_train_sklearn_max_temp_model():
    pytest.importorskip('sklearn')
    import pandas as pd

    df = pd.DataFrame(
        {
            'Location': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'],
            'DayNumber': [1, 2, 3, 4, 1, 2, 3, 4],
            'MinTemp': [10, 11, 12, 13, 7, 8, 9, 10],
            'MaxTemp': [20, 22, 24, 26, 15, 17, 18, 20],
        }
    )

    predictor = Predictor(df, model=None)
    model, training_data = predictor.train_sklearn_max_temp_model(
        feature_columns=['MinTemp'],
        target_column='MaxTemp',
        group_column='Location',
        sort_columns='DayNumber',
    )

    assert model is predictor.model
    assert predictor.training_feature_columns_ is not None
    assert 'MaxTemp_prev_day_1' in predictor.training_feature_columns_
    assert 'Location' in predictor.training_feature_columns_

    predictions = predictor.predict_max_temp_tomorrow(training_data[predictor.training_feature_columns_])
    assert len(predictions) == len(training_data)

def test_predictor_build_tomorrow_prediction_input():
    import pandas as pd

    df = pd.DataFrame(
        {
            'Location': ['A', 'A', 'A', 'B', 'B'],
            'DayNumber': [1, 2, 3, 1, 2],
            'MaxTemp': [20, 22, 25, 15, 16],
            'MinTemp': [10, 11, 13, 7, 8],
        }
    )

    predictor = Predictor(df, model=None)
    prediction_input = predictor.build_tomorrow_prediction_input(
        feature_columns=['MaxTemp', 'MinTemp'],
        location='A',
        sort_columns='DayNumber',
    )

    assert len(prediction_input) == 1
    assert prediction_input.iloc[0]['MaxTemp_prev_day_1'] == 25
    assert prediction_input.iloc[0]['MaxTemp_prev_day_2'] == 22
    assert prediction_input.iloc[0]['MinTemp_prev_day_1'] == 13
    assert prediction_input.iloc[0]['MinTemp_prev_day_2'] == 11
    assert prediction_input.iloc[0]['Location'] == 'A'

if __name__ == "__main__":
    pytest.main()
