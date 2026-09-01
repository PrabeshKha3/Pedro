import numpy as np
import cv2 
import sys
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QImage, QPixmap 
from PyQt6.QtCore import QTimer, QUrl 
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput 
from pathlib import Path

class Pedro:
    def __init__(self, left_hand, right_hand):
        self.left_hand = left_hand 
        self.right_hand = right_hand

        self.base_dir = Path(__file__).resolve().parent
        audio_path = self.base_dir / "Pedro Pedro.mp3"

        self.beat_times = [3.78485261, 4.17959184, 4.57433107, 4.96907029, 5.36380952, 5.75854875, 6.15328798, 6.54802721, 6.96598639, 7.36072562, 7.75546485, 8.15020408, 8.54494331]

        # the modules for handling and playing audio in PyQt
        self.audio = QAudioOutput()
        self.player = QMediaPlayer()  
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.7)  
        self.player.setSource(QUrl.fromLocalFile(str(audio_path)))

        self.current_beat = 0

        self.zoom_in_rate = 0.025
        self.zoom_limit = 0.5
        self.zoom_in_mode = True

        self.rotation_rate = 1

        # a utility function that resets the hand
    def alignment_reset(self):
        self.thumb_aligned = False
        self.index_aligned = False
        self.middle_aligned = False
        self.ring_aligned = False
        self.pinky_aligned = False

    def hand_position_correct(self):
        self.alignment_reset()

        if self.right_hand is not None and self.left_hand is not None:
            if self.left_hand.landmark[3].y > self.left_hand.landmark[4].y and self.right_hand.landmark[3].y > self.right_hand.landmark[4].y:
                self.thumb_aligned = True  
                
            if self.left_hand.landmark[7].y > self.left_hand.landmark[8].y and self.right_hand.landmark[7].y > self.right_hand.landmark[8].y:
                self.index_aligned = True  

            if self.left_hand.landmark[11].y > self.left_hand.landmark[12].y and self.right_hand.landmark[11].y > self.right_hand.landmark[12].y:
                self.middle_aligned = True   

            if self.left_hand.landmark[15].y > self.left_hand.landmark[16].y and self.right_hand.landmark[15].y > self.right_hand.landmark[16].y:
                self.ring_aligned = True  

            if self.left_hand.landmark[19].y > self.left_hand.landmark[20].y and self.right_hand.landmark[19].y > self.right_hand.landmark[20].y:
                self.pinky_aligned = True  

            if self.thumb_aligned and self.index_aligned and self.middle_aligned and self.ring_aligned and self.pinky_aligned:
                return True
            else:
                return False

    def dhukchuk(self):
        original = self.frame.copy()
        height, width = self.frame.shape[:2]
        x1 = int(width*self.zoom_in_rate)
        y1 = int(height*self.zoom_in_rate)

        x2 = int(width - width*self.zoom_in_rate)
        y2 = int(height - height*self.zoom_in_rate) 

        self.frame = original[y1:y2, x1:x2]
        self.frame = cv2.resize(self.frame, (width, height))

    def mask(self):
        h, w = self.frame.shape[:2]

        center_x, center_y = w // 2, h // 2

        mask = np.zeros((h, w), dtype="uint8")
        radius = 250  

        cv2.circle(mask, (center_x, center_y), radius, 255, -1)

        self.frame = cv2.bitwise_and(self.frame, self.frame, mask=mask)

    def rotate(self):
        (h, w) = self.frame.shape[:2]

        # 1. Define the center, angle, and scale
        center = (w // 2, h // 2)
        angle = self.rotation_rate
        scale = 1.0  

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)

        self.frame = cv2.warpAffine(self.frame, rotation_matrix, (w, h))

        self.rotation_rate = (self.rotation_rate + 1) % 360

    def play(self, rgb_frame):
        self.frame = rgb_frame
        if self.right_hand is not None and self.left_hand is not None and self.hand_position_correct():
            # cv2.putText(self.frame, "Pedro Pedro", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (225, 0, 0), 1, cv2.LINE_AA)

            if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                self.player.play()

            self.mask()

            self.rotate()

            current_time = self.player.position() / 1000
            if self.current_beat < len(self.beat_times):
                if current_time >= self.beat_times[self.current_beat]:
                    print("Beat!")
                    self.dhukchuk()
                    self.current_beat += 1

        else:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                print("stopping")
                self.player.stop()
                self.current_beat = 0
                self.rotation_rate = 1
                self.zoom_in_mode = True
                self.zoom_in_rate = 0.025
        return self.frame