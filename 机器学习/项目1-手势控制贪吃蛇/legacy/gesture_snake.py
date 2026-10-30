import math
import random
import cv2
import mediapipe as mp
import numpy as np
import cvzone

# 设置视频捕获
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# 初始化MediaPipe Hands模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.9, min_tracking_confidence=0.9)
# 蛇游戏类
class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # 蛇的所有点
        self.lengths = []  # 每个点之间的距离
        self.currentLength = 0  # 蛇的总长度
        self.allowedLength = 150  # 允许的总长度
        self.previousHead = 0, 0  # 之前的头部点

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cv2.putText(imgMain, "Game Over", [300, 400], cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 5, cv2.LINE_AA)
            cv2.putText(imgMain, f'Your Score: {self.score}', [300, 550], cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 5,
                        cv2.LINE_AA)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # 长度的缩短
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # 检查蛇是否吃了食物
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # 画蛇
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (255, 255, 0), 20)
                cv2.circle(imgMain, self.points[-1], 20, (255, 0, 0), cv2.FILLED)

            # 画食物
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cv2.putText(imgMain, f'Score: {self.score}', [50, 80], cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5,
                        cv2.LINE_AA)

            # 检查是否发生碰撞
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (255, 0, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                print("Hit")
                self.gameOver = True
                self.points = []  # all points of the snake
                self.lengths = []  # distance between each point
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed Length
                self.previousHead = 0, 0  # previous head point
                self.randomFoodLocation()

        return imgMain


# 初始化游戏
game = SnakeGameClass("D:\\SGAME\\EGG.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 镜像翻转图像
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 使用MediaPipe Hands模型处理图像
    results = hands.process(imgRGB)

    # 如果检测到手
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]  # 获取第一个手的标志点
        # 假设我们使用食指的顶部作为蛇的头部
        pointIndex = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        # 将标准化坐标转换为像素坐标
        pointIndex = int(pointIndex.x * img.shape[1]), int(pointIndex.y * img.shape[0])

        # 更新游戏状态
        img = game.update(img, pointIndex)

    # 显示图像
    cv2.imshow("Image", img)

    # 按下 'r' 键重置游戏
    if cv2.waitKey(1) == ord('r'):
        game.gameOver = False
        game.score = 0

    # 按下 ESC 键退出游戏
    if cv2.waitKey(1) == 27:
        break

# 释放资源
cv2.destroyAllWindows()
cap.release()