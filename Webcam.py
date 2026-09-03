import cv2 
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QImage, QPixmap 
from PyQt6.QtCore import QTimer, QUrl 
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput 
from pathlib import Path
from pedro import Pedro

class Webcam(QGraphicsView):
    def __init__(self):
        super().__init__()

        # setting up the scene and view
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.resize(800, 600)
        self.setWindowTitle("Hands up 🔫")

        # creating a Pixmaop item on the scene to hold our image frames
        self.video_frame_item = QGraphicsPixmapItem()
        self.scene.addItem(self.video_frame_item)

        # reading the images from the camera:
        self.capture = cv2.VideoCapture(0)  

        if not self.capture.isOpened():
            raise RuntimeError("Could not open webcam")

        # setting the qtimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start()

        # the modules used to detect and draw landmarks of the hand
        self.mp_hands = mp.solutions.hands 
        self.mp_draw = mp.solutions.drawing_utils 
        self.hands_obj = self.mp_hands.Hands()     

        self.base_dir = Path(__file__).resolve().parent

        self.pedro_obj = Pedro(None, None)

    # method that inputs from the webcam and displays it in the Qt window
    def update_frame(self):
        # reading the video frame by frame
        ret, frame = self.capture.read()
        if not ret:
            return  

        # preprocessing the frames
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detecting the hands by inferencing the frame for the hand object
        results = self.hands_obj.process(rgb_frame)

        # initalizing no hands detected
        self.left_hand = None
        self.right_hand = None

        # drawing the landmarks on the frame read and also classifying the right and left hand 
        if results.multi_hand_landmarks:
            for hand, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                self.mp_draw.draw_landmarks(rgb_frame, hand, self.mp_hands.HAND_CONNECTIONS)

                if hand_info.classification[0].label == "Right":
                    self.right_hand = hand
                else:
                    self.left_hand = hand


        self.pedro_obj.left_hand = self.left_hand
        self.pedro_obj.right_hand = self.right_hand

        rgb_frame = self.pedro_obj.play(rgb_frame) 

        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width 

        q_image = QImage(
            rgb_frame.data,
            width, 
            height, 
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)
        self.video_frame_item.setPixmap(pixmap)

    def closeEvent(self, event):
        self.capture.release()
        event.accept()