import math

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] DeepSORT failed to import ({e}). Falling back to Simple Centroid Tracker.")
    DEEPSORT_AVAILABLE = False

class SimpleFallbackTracker:
    def __init__(self, max_disappeared=30):
        self.next_object_id = 1
        self.objects = {} # id -> bbox [x1, y1, x2, y2]
        self.disappeared = {} # id -> frames count
        self.max_disappeared = max_disappeared

    def track(self, detections):
        input_bboxes = []
        for det in detections:
            bbox, conf, _ = det
            x1, y1, w, h = bbox
            input_bboxes.append([x1, y1, x1 + w, y1 + h])

        if len(input_bboxes) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    del self.objects[obj_id]
                    del self.disappeared[obj_id]
            return [{'id': obj_id, 'bbox': bbox} for obj_id, bbox in self.objects.items()]

        if len(self.objects) == 0:
            for bbox in input_bboxes:
                self.objects[self.next_object_id] = bbox
                self.disappeared[self.next_object_id] = 0
                self.next_object_id += 1
        else:
            object_ids = list(self.objects.keys())
            object_bboxes = list(self.objects.values())

            used_inputs = set()
            used_objects = set()

            for i, obj_id in enumerate(object_ids):
                ox1, oy1, ox2, oy2 = object_bboxes[i]
                ocx, ocy = (ox1 + ox2) / 2, (oy1 + oy2) / 2
                best_dist = float('inf')
                best_idx = -1

                for j, ibbox in enumerate(input_bboxes):
                    if j in used_inputs:
                        continue
                    ix1, iy1, ix2, iy2 = ibbox
                    icx, icy = (ix1 + ix2) / 2, (iy1 + iy2) / 2
                    dist = math.hypot(ocx - icx, ocy - icy)
                    if dist < best_dist and dist < 250:
                        best_dist = dist
                        best_idx = j

                if best_idx != -1:
                    self.objects[obj_id] = input_bboxes[best_idx]
                    self.disappeared[obj_id] = 0
                    used_inputs.add(best_idx)
                    used_objects.add(obj_id)

            for i, obj_id in enumerate(object_ids):
                if obj_id not in used_objects:
                    self.disappeared[obj_id] += 1
                    if self.disappeared[obj_id] > self.max_disappeared:
                        del self.objects[obj_id]
                        del self.disappeared[obj_id]

            for j, ibbox in enumerate(input_bboxes):
                if j not in used_inputs:
                    self.objects[self.next_object_id] = ibbox
                    self.disappeared[self.next_object_id] = 0
                    self.next_object_id += 1

        return [{'id': obj_id, 'bbox': bbox} for obj_id, bbox in self.objects.items()]

class PersonTracker:
    def __init__(self):
        self.use_deepsort = DEEPSORT_AVAILABLE
        if self.use_deepsort:
            try:
                self.tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
            except Exception as e:
                print(f"[WARNING] DeepSort initialization failed: {e}. Using fallback tracker.")
                self.use_deepsort = False
                self.tracker = SimpleFallbackTracker()
        else:
            self.tracker = SimpleFallbackTracker()

    def track(self, detections, frame):
        if not detections:
            if self.use_deepsort:
                try:
                    tracks = self.tracker.update_tracks([], frame=frame)
                    tracked_objects = []
                    for track in tracks:
                        if not track.is_confirmed():
                            continue
                        track_id = track.track_id
                        ltrb = track.to_ltrb() # [left, top, right, bottom]
                        tracked_objects.append({
                            'id': track_id,
                            'bbox': ltrb
                        })
                    return tracked_objects
                except Exception as e:
                    print(f"[ERROR] DeepSort update_tracks failed ({e}). Switching to fallback tracker.")
                    self.use_deepsort = False
                    self.tracker = SimpleFallbackTracker()
                    return self.tracker.track([])
            else:
                return self.tracker.track([])
        
        if self.use_deepsort:
            try:
                tracks = self.tracker.update_tracks(detections, frame=frame)
                tracked_objects = []
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    track_id = track.track_id
                    ltrb = track.to_ltrb() # [left, top, right, bottom]
                    tracked_objects.append({
                        'id': track_id,
                        'bbox': ltrb
                    })
                return tracked_objects
            except Exception as e:
                print(f"[ERROR] DeepSort update_tracks failed ({e}). Switching to fallback tracker.")
                self.use_deepsort = False
                self.tracker = SimpleFallbackTracker()
                return self.tracker.track(detections)
        else:
            return self.tracker.track(detections)

