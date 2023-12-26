from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR, ROUND_CEILING
import numpy as np
import math
# Enum for rasterizing algorithms
class RasterizingAlgorithm:
    Naive = 0
    DDA = 1
    Bresenham = 2
    Circle = 3

def my_round(x, rounding = ROUND_HALF_UP):
    return int(Decimal(x).to_integral_value(rounding=rounding))

def rasterize_line(start_x, start_y, end_x, end_y, color, algorithm):
    start_x, start_y = my_round(start_x), my_round(start_y)
    end_x, end_y = my_round(end_x), my_round(end_y)

    dx = end_x - start_x
    dy = end_y - start_y
    
    filled_pixels = []
    if algorithm == RasterizingAlgorithm.Naive:
        start = [start_x, start_y]
        end = [end_x, end_y]
        if start[0] > end[0]:
            start[0], end[0] = end[0], start[0]
        if start[1] > end[1]:
            start[1], end[1] = end[1], start[1]

        if (start[1] == end[1]):
            return [(x, start[1], color) for x in range(start[0], end[0] + 1, 1)]
        elif (start[0] == end[0]):
            return [(start[0], y, color) for y in range(start[1], end[1] + 1, 1)]

        for x in np.arange(start[0], end[0] + 1, 0.33):
            y = start_y + (dy / dx) * (x - start_x)
            filled_pixels.append((my_round(x, ROUND_FLOOR), my_round(y), color))

    elif algorithm == RasterizingAlgorithm.DDA:
        steps = max(abs(dx), abs(dy))
        x_increment = dx / steps
        y_increment = dy / steps

        x = start_x
        y = start_y

        for _ in range(steps):
            filled_pixels.append((my_round(x), my_round(y), color))
            x += x_increment
            y += y_increment

    elif algorithm == RasterizingAlgorithm.Bresenham:
        # Setup initial conditions
        x1, y1 = start_x, start_y
        x2, y2 = end_x, end_y
        dx = x2 - x1
        dy = y2 - y1

        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)
        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        # Swap start and end points if necessary and store swap state
        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1

        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        # Iterate over bounding box generating points between start and end
        y = y1
        for x in range(x1, x2 + 1):
            coord = (y, x) if is_steep else (x, y)
            filled_pixels.append([*coord, color])
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

        # Reverse the list if the coordinates were swapped
        if swapped:
            filled_pixels.reverse()

    elif algorithm == RasterizingAlgorithm.Circle:
        x0 = start_x
        y0 = start_y
        radius = math.sqrt(abs(end_x - start_x)**2 + abs(end_y - start_y)**2)

        x = radius
        y = 0
        err = 0

        while x >= y:
            filled_pixels.append((x0 + x, y0 + y, color))
            filled_pixels.append((x0 + y, y0 + x, color))
            filled_pixels.append((x0 - y, y0 + x, color))
            filled_pixels.append((x0 - x, y0 + y, color))
            filled_pixels.append((x0 - x, y0 - y, color))
            filled_pixels.append((x0 - y, y0 - x, color))
            filled_pixels.append((x0 + y, y0 - x, color))
            filled_pixels.append((x0 + x, y0 - y, color))

            y += 1
            err += 1 + 2*y
            if 2*(err-x) + 1 > 0:
                x -= 1
                err += 1 - 2*x

    return filled_pixels


for i in range(1, 15, 2):
    n = i / 2
    print(n, "=>", my_round(n))