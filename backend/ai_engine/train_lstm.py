import os
import torch
import torch.nn as nn
import torch.optim as optim
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

def generate_synthetic_data(num_samples=150, seq_len=30, num_features=36):
    X = []
    y = []
    
    # 3 classes: 0: Normal, 1: Fall, 2: Aggression
    samples_per_class = num_samples // 3
    
    # Class 0: Normal (realistic standing/sitting upright or half-body poses)
    for i in range(samples_per_class):
        seq = []
        base_pose = np.zeros(num_features)
        
        # x coordinates: left joints are around 0.4, right joints around 0.6
        base_pose[0::3] = np.random.uniform(0.35, 0.45, size=(12,))
        base_pose[3::6] = np.random.uniform(0.55, 0.65, size=(6,))
        
        # y coordinates mapping
        base_pose[1] = 0.25  # left shoulder
        base_pose[4] = 0.25  # right shoulder
        base_pose[7] = 0.45  # left elbow
        base_pose[10] = 0.45 # right elbow
        base_pose[13] = 0.55 # left wrist
        base_pose[16] = 0.55 # right wrist
        base_pose[19] = 0.65 # left hip
        base_pose[22] = 0.65 # right hip
        base_pose[25] = 0.8  # left knee
        base_pose[28] = 0.8  # right knee
        base_pose[31] = 0.95 # left ankle
        base_pose[34] = 0.95 # right ankle
        
        # Visibilities
        base_pose[2::3] = 0.9
        
        # 50% of normal samples represent half-body crops (lower body is occluded/zeroed)
        is_half_body = (i % 2 == 0)
        if is_half_body:
            base_pose[18:] = 0.0
            
        for t in range(seq_len):
            # Minor natural sway/noise
            noise = np.random.normal(0, 0.015, size=(num_features,))
            pose = base_pose + noise
            pose = np.clip(pose, 0.0, 1.0)
            if is_half_body:
                pose[18:] = 0.0
            seq.append(pose)
        X.append(seq)
        y.append(0)
        
    # Class 1: Fall (shoulders & hips coordinates dropping vertically over time)
    for i in range(samples_per_class):
        seq = []
        base_pose = np.zeros(num_features)
        base_pose[0::3] = np.random.uniform(0.35, 0.45, size=(12,))
        base_pose[3::6] = np.random.uniform(0.55, 0.65, size=(6,))
        base_pose[1] = 0.2
        base_pose[4] = 0.2
        base_pose[7] = 0.35
        base_pose[10] = 0.35
        base_pose[13] = 0.45
        base_pose[16] = 0.45
        base_pose[19] = 0.55
        base_pose[22] = 0.55
        base_pose[25] = 0.7
        base_pose[28] = 0.7
        base_pose[31] = 0.85
        base_pose[34] = 0.85
        base_pose[2::3] = 0.9
        
        is_half_body = (i % 2 == 0)
        if is_half_body:
            base_pose[18:] = 0.0
            
        for t in range(seq_len):
            ratio = t / (seq_len - 1)
            pose = base_pose.copy()
            # drop the vertical coordinates (all y-coords increase towards the bottom)
            pose[1] += ratio * 0.5  # left shoulder
            pose[4] += ratio * 0.5  # right shoulder
            pose[7] += ratio * 0.5  # left elbow
            pose[10] += ratio * 0.5 # right elbow
            pose[13] += ratio * 0.5 # left wrist
            pose[16] += ratio * 0.5 # right wrist
            
            if not is_half_body:
                pose[19] += ratio * 0.35
                pose[22] += ratio * 0.35
                pose[25] += ratio * 0.2
                pose[28] += ratio * 0.2
                pose[31] += ratio * 0.1
                pose[34] += ratio * 0.1
                
            pose += np.random.normal(0, 0.02, size=(num_features,))
            pose = np.clip(pose, 0.0, 1.0)
            if is_half_body:
                pose[18:] = 0.0
            seq.append(pose)
        X.append(seq)
        y.append(1)
        
    # Class 2: Aggression (high-frequency, high-amplitude movements of wrists/elbows)
    for i in range(samples_per_class):
        seq = []
        base_pose = np.zeros(num_features)
        base_pose[0::3] = np.random.uniform(0.35, 0.45, size=(12,))
        base_pose[3::6] = np.random.uniform(0.55, 0.65, size=(6,))
        base_pose[1] = 0.25
        base_pose[4] = 0.25
        base_pose[7] = 0.45
        base_pose[10] = 0.45
        base_pose[13] = 0.55
        base_pose[16] = 0.55
        base_pose[19] = 0.65
        base_pose[22] = 0.65
        base_pose[25] = 0.8
        base_pose[28] = 0.8
        base_pose[31] = 0.95
        base_pose[34] = 0.95
        base_pose[2::3] = 0.9
        
        is_half_body = (i % 2 == 0)
        if is_half_body:
            base_pose[18:] = 0.0
            
        for t in range(seq_len):
            pose = base_pose.copy()
            # high amplitude noise on wrists and elbows (indices 6 to 17)
            pose[6:18] += np.sin(t * 0.8) * 0.25 + np.random.normal(0, 0.05, size=(12,))
            pose += np.random.normal(0, 0.02, size=(num_features,))
            pose = np.clip(pose, 0.0, 1.0)
            if is_half_body:
                pose[18:] = 0.0
            seq.append(pose)
        X.append(seq)
        y.append(2)
        
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)

def train_model(save_path):
    print("Generating synthetic data for PyTorch LSTM Action model...")
    X, y = generate_synthetic_data()
    
    # Shuffle
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]
    
    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y)
    
    model = ActionLSTM()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    print("Training Action LSTM model on synthetic dataset...")
    model.train()
    epochs = 20
    batch_size = 16
    
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        for i in range(0, len(X), batch_size):
            inputs = X_tensor[i:i+batch_size]
            targets = y_tensor[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * len(inputs)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == targets).sum().item()
            
        acc = correct / len(X)
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/len(X):.4f} - Accuracy: {acc*100:.1f}%")
            
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Action LSTM weights successfully saved to {save_path}!")

if __name__ == "__main__":
    weights_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/weights/lstm_behavior.pth"))
    train_model(weights_path)
