import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    # Creating an empty dataframe with unique IDs
    unique_ids = sorted(set(df['id_start']).union(df['id_end']))
    distance_matrix = pd.DataFrame(index=unique_ids, columns=unique_ids)
    
    # Filling in the distances in the matrix
    for index, row in df.iterrows():
        id_start, id_end, distance = row['id_start'], row['id_end'], row['distance']
        # Setting distances for both directions
        distance_matrix.at[id_start, id_end] = distance
        distance_matrix.at[id_end, id_start] = distance
    
    #dia = 0
    for id in unique_ids:
        distance_matrix.at[id, id] = 0
    
    # Filling in missing values with cumulative distances
    for col in distance_matrix.columns:
        for row in distance_matrix.index:
            if pd.isna(distance_matrix.at[row, col]):
                distance_matrix.at[row, col] = distance_matrix[row].sum()
    
    # Ensuring matrix is symmetric
    distance_matrix = distance_matrix.fillna(0) + distance_matrix.fillna(0).T
    
    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    # Create an empty list to store the data
    data = []

    # Iterate over the rows of the distance matrix
    for i in range(len(df)):
        for j in range(len(df.columns)):
            # Skip the diagonal and NaN values
            if i != j and not pd.isna(df.iloc[i, j]):
                # Append the data to the list
                data.append({'id_start': df.index[i], 'id_end': df.columns[j], 'distance': df.iloc[i, j]})

    # Create a DataFrame from the list of data
    unrolled_df = pd.DataFrame(data)

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    # Filtering the DataFrame based on the reference_id
    reference_df = df[df['id_start'] == reference_id]

    # Calculating the average distance for the reference_id
    reference_avg_distance = reference_df['distance'].mean()

    # Calculating the lower and upper bounds of the threshold
    lower_bound = reference_avg_distance - 0.1 * reference_avg_distance
    upper_bound = reference_avg_distance + 0.1 * reference_avg_distance

    # Filtering the DataFrame based on the threshold
    filtered_df = df[(df['distance'] >= lower_bound) & (df['distance'] <= upper_bound)]

    #sorted list of values from the id_start column
    result = sorted(filtered_df['id_start'].unique())

    return result


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        # Create a new column for the toll rate of the current vehicle type
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    df_time_based = pd.DataFrame()

    # Iterate over each unique (id_start, id_end) pair
    for _, row in df.iterrows():
        # Define time ranges and discount factors
        time_ranges = {
            'weekday_morning': ('00:00:00', '10:00:00', 0.8),
            'weekday_afternoon': ('10:00:00', '18:00:00', 1.2),
            'weekday_evening': ('18:00:00', '23:59:59', 0.8),
            'weekend_all_day': ('00:00:00', '23:59:59', 0.7)
        }

        # Create a new DataFrame to store time-based toll rates for the current pair
        pair_time_based_df = pd.DataFrame()

        # Iterate over each time range
        for range_name, (start_time, end_time, discount_factor) in time_ranges.items():
            # Calculate updated toll rates based on the current time range
            current_range_df = pd.DataFrame(row[['moto', 'car', 'rv', 'bus', 'truck']] * discount_factor).T
            current_range_df.columns = [f'{vehicle}_rate_{range_name}' for vehicle in ['moto', 'car', 'rv', 'bus', 'truck']]

            # Add columns for start_day, start_time, end_day, and end_time
            current_range_df['start_day'] = pd.to_datetime(row['id_start']).day_name()
            current_range_df['start_time'] = start_time
            current_range_df['end_day'] = pd.to_datetime(row['id_end']).day_name()
            current_range_df['end_time'] = end_time

            # Append the current range DataFrame to the result DataFrame
            pair_time_based_df = pd.concat([pair_time_based_df, current_range_df], axis=1)

        # Append the pair-specific time-based toll rates to the overall result DataFrame
        df_time_based = pd.concat([df_time_based, pair_time_based_df], ignore_index=True)

    return df_time_based
