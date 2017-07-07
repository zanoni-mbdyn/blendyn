from math import *
from mathutils import *
# import matplotlib.pyplot as plt

def calc_nurbs(angle, radius, axis):
	nurbsPoints = {}

	weight = 1

	for point in range(1, 10):
		nurbsPoints[point] = {'location': Vector((0, 0, 0))}
		nurbsPoints[point]['location'][(axis + 1)%3] = radius 

	for point in range(1, 10):
		nurbsPoints[point]['max'] = 45 * (point - 1)
		nurbsPoints[point]['min'] = -45 * (point - 1)

	for point in range(1, 10, 2):
		if angle > 0:
			nurbsPoints[point]['rotation'] = min(nurbsPoints[point]['max'], angle)

		elif angle < 0:
			nurbsPoints[point]['rotation'] = max(nurbsPoints[point]['min'], angle)

		else:
			nurbsPoints[point]['rotation'] = 0

	for point in range(2, 9, 2):

		nurbsPoints[point]['rotation'] = (nurbsPoints[point-1]['rotation'] + nurbsPoints[point+1]['rotation']) / 2 

	for point in range(1, 10, 1):
		dummy = nurbsPoints[point]['rotation']
		rotationAngle = Euler((0, 0, 0))
		rotationAngle[axis] = radians(dummy)
		nurbsPoints[point]['location'].rotate(rotationAngle)
		nurbsPoints[point]['weight'] = 1.0

		if angle:
			swept = (nurbsPoints[point]['max'] * angle/abs(angle), (point - 2) * 45 * angle/abs(angle))
			if point%2 == 0 and  min(swept) <= nurbsPoints[point]['rotation']  <= max(swept):
				magAngle = nurbsPoints[point]['rotation']
				magAngle = radians(magAngle - 90*int(magAngle/90) )
				nurbsPoints[point]['weight'] = cos(abs(magAngle)/2)
				nurbsPoints[point]['location'].magnitude = abs(radius / cos(magAngle))

	# plt.xlim(-3, 3)
	# plt.ylim(-3, 3)
	# plt.gca().set_aspect('equal', adjustable='box')
	# plt.scatter(0, 0)

	# for point in range(1, 10, 1):
	# 	axes = [0, 1, 2]
	# 	axes.remove(axis)
	# 	x, y = nurbsPoints[point]['location'][axes[0]], nurbsPoints[point]['location'][axes[1]]
	# 	plt.scatter(x, y)
	# 	print(tuple(nurbsPoints[point]['location']))
	# 	plt.annotate(str(point), (x,y))

	# plt.show()

	return [(nurbsPoints[element]['location'], nurbsPoints[element]['weight']) for element in nurbsPoints]

# calc_nurbs(-285, 1, 1)