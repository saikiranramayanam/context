import os
import torch
import torch.nn as nn
import numpy as np

class ActionLSTM(nn.Module):
    def __init__(self, input_dim=36, hidden_dim=64, num_classes=3, num_layers=2):
        super(ActionLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class BehaviorAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ActionLSTM().to(self.device)
        self.seq_len = 30
        self.num_landmarks = 12 # 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28
        self.landmark_indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        self.history = {} # track ID -> list of joint keypoints
        
        weights_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/weights/lstm_behavior.pth"))
        
        # If weights do not exist, trigger training script automatically
        if not os.path.exists(weights_path):
            print("Action LSTM weights not found. Running training script...")
            try:
                from .train_lstm import train_model
                train_model(weights_path)
            except Exception as e:
                print(f"Auto-training failed: {e}. Using uninitialized weights.")
                
        if os.path.exists(weights_path):
            try:
                self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
                self.model.eval()
                print("Action LSTM model loaded successfully!")
            except Exception as e:
                print(f"Error loading model weights: {e}")
        else:
            self.model.eval()

    def _extract_keypoints(self, landmarks, bbox):
        # Normalize landmarks relative to bbox width/height
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        
        kps = []
        for idx in self.landmark_indices:
            if landmarks and idx < len(landmarks):
                abs_x, abs_y, vis = landmarks[idx]
                norm_x = (abs_x - x1) / w if w > 0 else 0
                norm_y = (abs_y - y1) / h if h > 0 else 0
                kps.extend([norm_x, norm_y, vis])
            else:
                kps.extend([0.0, 0.0, 0.0])
        return kps

    def analyze(self, tracked_objects, proximities):
        alerts = []
        max_risk = 0.0
        
        active_ids = set()
        
        for obj in tracked_objects:
            tid = obj['id']
            active_ids.add(tid)
            bbox = obj['bbox']
            landmarks = obj.get('landmarks')
            
            kps = self._extract_keypoints(landmarks, bbox)
            
            if tid not in self.history:
                self.history[tid] = []
            self.history[tid].append(kps)
            
            if len(self.history[tid]) > self.seq_len:
                self.history[tid].pop(0)
                
            x1, y1, x2, y2 = bbox
            aspect_ratio = (y2 - y1) / (x2 - x1) if (x2 - x1) > 0 else 0

            if len(self.history[tid]) < self.seq_len:
                # Basic heuristic check as fallback if sequence isn't full yet
                if aspect_ratio < 0.7:
                    max_risk = max(max_risk, 50.0)
                    alerts.append(f"Person {tid} exhibits fallen posture (Heuristic).")
                continue
                
            # Run deep LSTM model
            seq_tensor = torch.tensor([self.history[tid]], dtype=torch.float32).to(self.device)
            with torch.no_grad():
                outputs = self.model(seq_tensor)
                probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
                
            # Probabilities for Normal (0), Fall (1), Aggression (2)
            normal_p, fall_p, aggression_p = probs
            
            person_risk = 0.0
            if fall_p > 0.5:
                # Gate fall prediction: horizontal posture (aspect ratio < 0.95)
                if aspect_ratio < 0.95:
                    person_risk = max(person_risk, fall_p * 80.0)
                    alerts.append(f"Fall detected for Person {tid} (Conf: {fall_p:.2f}).")
                else:
                    # Log suppression
                    print(f"[INFO] Person {tid} fall prediction suppressed (Conf: {fall_p:.2f}, Aspect Ratio: {aspect_ratio:.2f})")
            
            if aggression_p > 0.5:
                person_risk = max(person_risk, aggression_p * 100.0)
                alerts.append(f"Violence/aggression detected for Person {tid} (Conf: {aggression_p:.2f}).")
                
            max_risk = max(max_risk, person_risk)

        # Proximity check
        for t1, t2, dist in proximities:
            if dist < 120:
                max_risk = max(max_risk, 40.0)
                alerts.append(f"Person {t1} and Person {t2} are dangerously close ({dist:.1f}px).")
                
        # Prune dead tracks
        self.history = {tid: self.history[tid] for tid in self.history if tid in active_ids}
        
        return min(max_risk, 100.0), alerts
