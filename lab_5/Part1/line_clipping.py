import numpy as np

# define the Line and Viewport classes
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

class Viewport:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin, self.ymin = xmin, ymin
        self.xmax, self.ymax = xmax, ymax

# function to implement Cohen-Sutherland algorithm for line clipping
def clip_line(line : Line, viewport : Viewport) -> Line | None:
    x1, y1, x2, y2 = line.x1, line.y1, line.x2, line.y2
    xmin, ymin, xmax, ymax = viewport.xmin, viewport.ymin, viewport.xmax, viewport.ymax

    # compute the binary codes for the two endpoints of the line
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    # keep looping until the line is either completely inside or completely outside the viewport
    while True:
        # if both endpoints have code 0000 (i.e., inside the viewport), accept the line
        if code1 == code2 == 0b0000:
            return Line(x1, y1, x2, y2)

        # if the bitwise AND of the two codes is not 0 (i.e., at least one bit is set to 1),
        # the line is outside the viewport and can be rejected
        elif (code1 & code2) != 0b0000:
            return None

        # otherwise, the line intersects the viewport and we need to clip it
        else:
            # choose the endpoint with a code outside the viewport
            if code1 != 0b0000:
                code = code1
                x, y = x1, y1
            else:
                code = code2
                x, y = x2, y2

            # compute the intersection point between the line and the viewport
            if (code & 0b1000) == 0b1000:
                # intersection with top viewport boundary
                x = x1 + (ymax - y1) * (x2 - x1)  / (y2 - y1)
                y = ymax
            elif (code & 0b0100) == 0b0100:
                # intersection with bottom viewport boundary
                x = x1 + (ymin - y1) * (x2 - x1) / (y2 - y1)
                y = ymin
            elif (code & 0b0010) == 0b0010:
                # intersection with right viewport boundary
                y = y1 + (xmax - x1) * (y2 - y1) / (x2 - x1)
                x = xmax
            elif (code & 0b0001) == 0b0001:
                # intersection with left viewport boundary
                y = y1 + (xmin - x1) * (y2 - y1) / (x2 - x1)
                x = xmin

            # update the endpoint code and coordinates
            if code == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

# function to compute the binary code for a point
def compute_code(x, y, xmin, ymin, xmax, ymax):
    x_code = 0
    y_code = 0
    if x < xmin:
        x_code = 0b0001
    elif x > xmax:
        x_code = 0b0010
    else:
        x_code = 0b0000
    if y < ymin:
        y_code = 0b1000
    elif y > ymax:
        y_code = 0b0100
    else:
        y_code = 0b0000
    return x_code | y_code