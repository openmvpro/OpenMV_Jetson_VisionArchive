import turtle

# 迷宫类 
class Maze(object):
	# 读取迷宫数据，初始化迷宫内部，并找到海龟初始位置。
	def __init__(self, mazeFileName):
		rowsInMaze = 0							#初始化迷宫行数
		columnsInMaze = 0 						#初始化迷宫列数
		self.mazelist = []						#初始化迷宫列表
		mazeFile = open(mazeFileName, 'r')		#读取迷宫文件
		for line in mazeFile:					#按行读取
			rowList = [] 						#初始化行列表
			col = 0 							#初始化列
			# for ch in line[:-1]:				#这样会丢失最后一列
			for ch in line:						#按列读取
				rowList.append(ch)				#添加到行列表
				if ch == 'S':					#S为乌龟初始位置，即迷宫起点
					self.startRow = rowsInMaze	#乌龟初始行
					self.startCol = col 		#乌龟初始列
				col = col + 1 					#下一列
			rowsInMaze = rowsInMaze + 1 		#下一行
			self.mazelist.append(rowList)		#行列表添加到迷宫列表
			columnsInMaze = len(rowList) 		#获取迷宫总列数
		self.rowsInMaze = rowsInMaze 			#设置迷宫总行数
		self.columnsInMaze = columnsInMaze		#设置迷宫总列数
		self.xTranslate = -columnsInMaze/2 		#设置迷宫左上角的初始x坐标
		self.yTranslate = rowsInMaze/2 			#设置迷宫左上角的初始y坐标
		self.t = turtle.Turtle()				#创建一个海龟对象
		self.t.shape('turtle')					#给当前指示点设置样式(类似鼠标箭头)，海龟形状为参数指定的形状名，指定的形状名应存在于TurtleScreen的shape字典中。多边形的形状初始时有以下几种："arrow", "turtle", "circle", "square", "triangle", "classic"。
		self.wn = turtle.Screen()				#创建一个能在里面作图的窗口
		self.wn.setworldcoordinates(-columnsInMaze/2, -rowsInMaze/2, columnsInMaze/2, rowsInMaze/2)			#设置世界坐标系，原点在迷宫正中心。参数依次为画布左下角x轴坐标、左下角y轴坐标、右上角x轴坐标、右上角y轴坐标

	# 在屏幕上绘制迷宫
	def drawMaze(self):
		self.t.speed(100)						#绘图速度
		for y in range(self.rowsInMaze):		#按单元格依次循环迷宫
			for x in range(self.columnsInMaze):
				if self.mazelist[y][x] == OBSTACLE:	#如果迷宫列表的该位置为障碍物，则画方块
					self.drawCenteredBox(x + self.xTranslate, -y + self.yTranslate, 'orange')

	# 画方块
	def drawCenteredBox(self, x, y, color):
		self.t.up()								#画笔抬起
		self.t.goto(x - 0.5, y - 0.5)			#前往参数位置，此处0.5偏移量的作用是使乌龟的探索路线在单元格的正中心位置
		self.t.color(color)						#方块边框为橙色
		self.t.fillcolor('green')				#方块内填充绿色
		self.t.setheading(90)					#设置海龟的朝向，标准模式：0 - 东，90 - 北，180 - 西，270 - 南。logo模式：0 - 北，90 - 东，180 - 南，270 - 西。
		self.t.down()							#画笔落下
		self.t.begin_fill()						#开始填充
		for i in range(4):						#画方块边框
			self.t.forward(1)					#前进1个单位
			self.t.right(90)					#右转90度
		self.t.end_fill()						#结束填充

	# 移动海龟
	def moveTurtle(self, x, y):
		self.t.up()								#画笔抬起
		self.t.setheading(self.t.towards(x + self.xTranslate, -y + self.yTranslate))	#setheading()设置海龟朝向，towards()从海龟位置到由(x, y)，矢量或另一海龟位置连线的夹角。此数值依赖于海龟初始朝向，由"standard"、"world"或"logo" 模式设置所决定。
		self.t.goto(x + self.xTranslate, -y + self.yTranslate)	#前往目标位置

	# 画路径圆点
	def dropBreadcrumb(self, color):
		self.t.dot(color)						#dot(size=None, color)画路径圆点

	# 用以更新迷宫内的状态及在窗口中改变海龟位置，行列参数为乌龟的初始坐标。
	def updatePosition(self, row, col, val):
		self.mazelist[row][col] = val 			#设置该标记状态为当前单元格的值
		self.moveTurtle(col, row)				#移动海龟
		if val == PART_OF_PATH: 				#其中一条成功路径的圆点的颜色
			color = 'green'
		elif val == TRIED:						#尝试用的圆点的颜色
			color = 'black'
		elif val == DEAD_END:					#死胡同用的圆点的颜色
			color = 'red'
		self.dropBreadcrumb(color)				#画路径圆点并上色

	# 用以判断当前位置是否为出口。
	def isExit(self, row, col):
		return (row == 0 or row == self.rowsInMaze - 1 or col == 0 or col == self.columnsInMaze - 1)								#根据海龟位置是否在迷宫的4个边线位置判断

	# 返回键对应的值，影响searchFrom()中maze[startRow][startColumn]值的获取
	def __getitem__(self, key):
		return self.mazelist[key]

# 探索迷宫，注意此函数包括三个参数：一个迷宫对象、起始行、起始列。
def searchFrom(maze, startRow, startColumn):
	# 从初始位置开始尝试四个方向，直到找到出路。
	# 1. 遇到障碍
	if maze[startRow][startColumn] == OBSTACLE:
		return False
	# 2. 发现已经探索过的路径或死胡同
	if maze[startRow][startColumn] == TRIED or maze[startRow][startColumn]== DEAD_END:
		return False
	# 3. 发现出口
	if maze.isExit(startRow, startColumn):
		maze.updatePosition(startRow, startColumn, PART_OF_PATH)#显示出口位置，注释则不显示此点
		return True
	maze.updatePosition(startRow, startColumn, TRIED)#更新迷宫状态、设置海龟初始位置并开始尝试
	# 4. 依次尝试每个方向
	found = searchFrom(maze, startRow - 1, startColumn) or \
            searchFrom(maze, startRow + 1, startColumn) or \
            searchFrom(maze, startRow, startColumn - 1) or \
            searchFrom(maze, startRow, startColumn + 1)
	if found:													#找到出口
		maze.updatePosition(startRow, startColumn, PART_OF_PATH)#返回其中一条正确路径
	else:														#4个方向均是死胡同
		maze.updatePosition(startRow, startColumn, DEAD_END)
	return found

if __name__ == '__main__':
	PART_OF_PATH = 'O'			#部分路径
	TRIED = '.'					#尝试
	OBSTACLE = '+'				#障碍
	DEAD_END = '-'				#死胡同
	myMaze = Maze('maze.txt')	#实例化迷宫类，maze文件是使用“+”字符作为墙壁围出空心正方形空间，并用字母“S”来表示起始位置的迷宫文本文件。
	myMaze.drawMaze()			#在屏幕上绘制迷宫。
	searchFrom(myMaze, myMaze.startRow, myMaze.startCol)	#探索迷宫
