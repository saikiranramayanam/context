import cv2
import threading
import time

class VideoCapture:
    def __init__(self, src=0):
        # Convert src to int if it's a numeric string (e.g. "0")
        try:
            self.src = int(src)
        except ValueError:
            self.src = src
            
        self.cap = cv2.VideoCapture(self.src)
        self.ret, self.frame = self.cap.read()
        self.running = True
        
        # Start a background thread to read frames continuously to avoid buffer build-up
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.ret = ret
                    self.frame = frame
                else:
                    if isinstance(self.src, str):
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.running = False
        self.thread.join(timeout=1.0)
        self.cap.release()
