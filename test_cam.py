import cv2

print("Testing camera 0...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera 0.")
else:
    ret, frame = cap.read()
    if ret:
        print(f"Success! Read a frame of size {frame.shape}")
    else:
        print("Error: Camera 0 opened, but could not read a frame.")

cap.release()

print("\nTesting camera with cv2.CAP_DSHOW (Windows specific)...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Error: Could not open camera with CAP_DSHOW.")
else:
    ret, frame = cap.read()
    if ret:
        print(f"Success! Read a frame of size {frame.shape}")
    else:
        print("Error: Camera opened with CAP_DSHOW, but could not read a frame.")
cap.release()
