from datavolley import dv_index2xy, add_xy

# Example test
x, y = dv_index2xy(5)
print(x, y)

res = add_xy((1, 2), (3, 4))
print(res)  # Should output (4, 6)
