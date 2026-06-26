import cv2
import mediapipe.python.solutions.pose as mp_pose_module
import mediapipe.python.solutions.drawing_utils as mp_draw_module

mp_pose = mp_pose_module
pose = mp_pose.Pose()

mp_draw = mp_draw_module


def detect_pose(frame_rgb):
    results = pose.process(frame_rgb)

    return results


def draw_pose(frame, pose_results):
    if pose_results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    return frame