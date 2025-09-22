import pandas as pd
import numpy as np

def dv_index2xy(i):
    """
    Converts a given index to x and y coordinates 
    based on a specific transformation formula.

    Args:
        i (int or array-like): 
        Index or array of indices to be converted.

    Returns:
        np.ndarray: 
        A 2D numpy array where each row contains the x 
        and y coordinates corresponding to the input index.

    Example:
        index = 150
        coordinates = dv_index2xy(index)
        print(coordinates)
        # Output: array([[0.5225 , 0.34438]])

        indices = [1, 50, 150]
        coordinates = dv_index2xy(indices)
        print(coordinates)
        # Output: array([[ 0.14375 , -0.2037  ],
        #                [ 1.86562 , -0.2037  ],
        #                [ 0.5225  ,  0.34438 ]])
    """
    x = ((i - 1 - np.floor((i - 1) / 100) * 100) / 99) * 3.7125 + 0.14375
    y = (np.floor((i - 1) / 100) / 100) * 7.4074 - 0.2037
    # Return a simple (x, y) tuple for scalar input; otherwise, a 2D array for array-like input
    try:
        # numpy's isscalar handles python scalars and 0-d numpy arrays
        if np.isscalar(i) or (np.asarray(i).ndim == 0):
            return (float(x), float(y))
    except Exception:
        pass
    return np.column_stack((x, y))


def add_xy(a, b=None):
    """
    Add XY values.

    Two modes are supported:
    1) Tuple/sequence mode: add two 2D points element-wise.
       Example:
           add_xy((1, 2), (3, 4)) -> (4, 6)

    2) DataFrame mode: add x and y coordinate columns to the DataFrame
       based on start, mid, and end coordinate indices using dv_index2xy.

    Args:
        a: Either a tuple/list like (x, y) OR a pandas DataFrame with
           'start_coordinate', 'mid_coordinate', and 'end_coordinate' columns.
        b: Optional second tuple/list like (x, y) when using tuple mode.

    Returns:
        - Tuple[int|float, int|float] when in tuple/sequence mode.
        - pandas.DataFrame when in DataFrame mode.
    """
    # Tuple/sequence mode
    if b is not None:
        try:
            ax, ay = a
            bx, by = b
        except Exception:
            raise TypeError("When providing two arguments, each must be a 2-item sequence (x, y).")
        return (ax + bx, ay + by)

    # DataFrame mode
    if not isinstance(a, pd.DataFrame):
        raise TypeError("Single-argument mode expects a pandas DataFrame or provide two (x, y) sequences.")

    data = a.copy()
    data['start_coordinate'] = pd.to_numeric(data['start_coordinate'], errors='coerce')
    data['start_coordinate'] = data['start_coordinate'].astype('Int64')
    data['start_coord_xy'] = data['start_coordinate'].apply(dv_index2xy)
    data[['start_coordinate_x', 'start_coordinate_y']] = \
        pd.DataFrame(data['start_coord_xy'].tolist(), index=data.index)

    data['mid_coordinate'] = pd.to_numeric(data['mid_coordinate'], errors='coerce')
    data['mid_coordinate'] = data['mid_coordinate'].astype('Int64')
    data['mid_coord_xy'] = data['mid_coordinate'].apply(dv_index2xy)
    data[['mid_coordinate_x', 'mid_coordinate_y']] = \
        pd.DataFrame(data['mid_coord_xy'].tolist(), index=data.index)

    data['end_coordinate'] = pd.to_numeric(data['end_coordinate'], errors='coerce')
    data['end_coordinate'] = data['end_coordinate'].astype('Int64')
    data['end_coord_xy'] = data['end_coordinate'].apply(dv_index2xy)
    data[['end_coordinate_x', 'end_coordinate_y']] = \
        pd.DataFrame(data['end_coord_xy'].tolist(), index=data.index)

    data = data.drop(columns=['start_coord_xy', 'end_coord_xy', 'mid_coord_xy'])
    return data
