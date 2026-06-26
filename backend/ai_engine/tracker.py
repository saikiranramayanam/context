from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        # DeepSORT configuration
        self.tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
        
    def track(self, detections, frame):
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb() # [left, top, right, bottom]
            
            tracked_objects.append({
                'id': track_id,
                'bbox': ltrb # [x1, y1, x2, y2]
            })
            
        return tracked_objects
