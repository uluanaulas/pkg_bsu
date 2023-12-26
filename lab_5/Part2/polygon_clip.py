from __future__ import annotations

class Viewport:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin, self.ymin = xmin, ymin
        self.xmax, self.ymax = xmax, ymax

class Line:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def intersect(self, other: Line) -> list[float]:
        # Calculate the slopes of the two lines
        slope_self = (self.y2 - self.y1) / (self.x2 - self.x1) if self.x2 - self.x1 != 0 else float('inf')
        slope_other = (other.y2 - other.y1) / (other.x2 - other.x1) if other.x2 - other.x1 != 0 else float('inf')

        # Check if the lines are parallel
        if slope_self == slope_other:
            return []

        # Calculate the intersection point (x,y) of the two lines
        if slope_self == float('inf'):  # self line is vertical
            x = self.x1
            y = slope_other * (x - other.x1) + other.y1
        elif slope_other == float('inf'):  # other line is vertical
            x = other.x1
            y = slope_self * (x - self.x1) + self.y1
        else:  # neither line is vertical
            x = (other.y1 - self.y1 + slope_self * self.x1 - slope_other * other.x1) / (slope_self - slope_other)
            y = slope_self * (x - self.x1) + self.y1

        # Check if the intersection point lies within the segments of both lines
        # if not (min(self.x1, self.x2) <= x <= max(self.x1, self.x2) and
        #         min(self.y1, self.y2) <= y <= max(self.y1, self.y2) and
        #         min(other.x1, other.x2) <= x <= max(other.x1, other.x2) and
        #         min(other.y1, other.y2) <= y <= max(other.y1, other.y2)):
        #     return []

        # Return the intersection point as a list of two floats
        return [x, y]
    
def compute_code(x : float, y : float, v : Viewport) -> int:
        code = 0b0000

        if x < v.xmin:
            code |= 0b0001
        elif x > v.xmax:
            code |= 0b0010

        if y < v.ymin:
            code |= 0b0100
        elif y > v.ymax:
            code |= 0b1000

        return code

def sutherland_clip(poly: list[Line], v : Viewport) -> list[Line]:
    xmin, ymin, xmax, ymax = v.xmin, v.ymin, v.xmax, v.ymax

    # Iterate over each edge of the viewport and clip the polygon against it
    borders = [Line(xmin, ymin, xmin, ymax), Line(xmin, ymax, xmax, ymax), Line(xmax, ymax, xmax, ymin), Line(xmax, ymin, xmin, ymin)]
    border_codes = [0b0001, 0b1000, 0b0010, 0b0100]
    for border, border_code in zip(borders, border_codes):
        # Clip the polygon against the edge
        new_vertex = []
        for edge in poly:
            # Check if the start point is visible
            start_code = compute_code(edge.x1, edge.y1, v)
            if start_code & border_code == 0:
                new_vertex.append([edge.x1, edge.y1])

            end_code = compute_code(edge.x2, edge.y2, v)
            # Check if the edge intersects the viewport edge
            if (start_code ^ end_code) & border_code > 0:
                intersection = edge.intersect(border)
                if intersection:
                    new_vertex.append(intersection)

        poly = []
        mod = len(new_vertex)
        for i in range(len(new_vertex)):
            poly.append(Line(new_vertex[i][0], new_vertex[i][1], new_vertex[(i+1) % mod][0], new_vertex[(i+1) % mod][1]))

    return poly
