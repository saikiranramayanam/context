import cv2
import threading
import time
import os

class VideoCapture:
    def __init__(self, src=0):
        try:
            self.src = int(src)
        except ValueError:
            self.src = src
            
        self.lock = threading.Lock()
        self.cap = None
        self.ret = False
        self.frame = None
        
        # Try standard VideoCapture first with retries if device was recently busy
        max_retries = 3
        for attempt in range(max_retries):
            self.cap = cv2.VideoCapture(self.src)
            if isinstance(self.src, int) and os.name == 'nt' and not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)

            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.ret = ret
                    self.frame = frame
                    break
                else:
                    self.cap.release()
                    self.cap = None
            
            if attempt < max_retries - 1:
                time.sleep(0.3) # Wait for hardware driver to release on Windows

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.ret = ret
                        self.frame = frame
                else:
                    if isinstance(self.src, str):
                        # Re-open video file to loop seamlessly without freezing
                        if self.cap:
                            self.cap.release()
                        self.cap = cv2.VideoCapture(self.src)
                        if self.cap and self.cap.isOpened():
                            ret_retry, frame_retry = self.cap.read()
                            if ret_retry and frame_retry is not None:
                                with self.lock:
                                    self.ret = ret_retry
                                    self.frame = frame_retry
                    time.sleep(0.01)
            else:
                # If capture device was unavailable, periodically try reopening it
                time.sleep(1.0)
                if self.running:
                    try:
                        self.cap = cv2.VideoCapture(self.src)
                        if isinstance(self.src, int) and os.name == 'nt' and not self.cap.isOpened():
                            self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
                    except Exception:
                        pass

    def read(self):
        with self.lock:
            if self.frame is not None:
                return self.ret, self.frame.copy()
            return False, None

    def release(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None

