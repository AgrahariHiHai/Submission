import pandas as pd


def generate_car_matrix(df)->pd.DataFrame:
    car_matrix = pd.pivot_table(df, values='car', index='id_1', columns='id_2', fill_value=0)
    car_matrix.values[[range(len(car_matrix))]*2] = 0
    return car_matrix

def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Write your logic here
    df['car_type'] = pd.cut(df['car'], bins=[-float('inf'), 15, 25, float('inf')], labels=['low', 'medium', 'high'])
    car_type_count = dict(sorted(df['car_type'].value_counts().items()))
    return car_type_count


def get_bus_indexes(df)->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Write your logic here
    mean_bus = df['bus'].mean()
    bus_indexes = df[df['bus'] > 2 * mean_bus].index.sort_values().tolist()
    return bus_indexes


def filter_routes(df)->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Write your logic here
    truck_avg_by_route = df.groupby('route')['truck'].mean()
    filtered_routes = truck_avg_by_route[truck_avg_by_route > 7].index.sort_values().tolist()
    return filtered_routes


def multiply_matrix(matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Write your logic here
    modified_matrix = matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25).round(1)
    return modified_matrix


def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    # Write your logic here
    df['start_timestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])
    df['end_timestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

    df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()

    # Grouping by 'id' and 'id_2'
    grouped_df = df.groupby(['id', 'id_2'])

    # Checking if timestamps cover a full 24-hour period and span all 7 days
    time_check_result = grouped_df.apply(lambda x: (
        (x['start_timestamp'].min().time() == pd.to_datetime('00:00:00').time()) and
        (x['end_timestamp'].max().time() == pd.to_datetime('23:59:59').time()) and
        (x['duration_seconds'].sum() == 7 * 24 * 3600)
    ))

    # Returning the resulting boolean Series with multi-index (id, id_2)
    return time_check_result.droplevel(2)