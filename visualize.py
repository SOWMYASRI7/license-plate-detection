import ast
import cv2
import numpy as np
import pandas as pd

def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, min(y1 + line_length_y, y2)), color, thickness)  # top-left
    cv2.line(img, (x1, y1), (min(x1 + line_length_x, x2), y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, max(y2 - line_length_y, y1)), color, thickness)  # bottom-left
    cv2.line(img, (x1, y2), (min(x1 + line_length_x, x2), y2), color, thickness)

    cv2.line(img, (x2, y1), (max(x2 - line_length_x, x1), y1), color, thickness)  # top-right
    cv2.line(img, (x2, y1), (x2, min(y1 + line_length_y, y2)), color, thickness)

    cv2.line(img, (x2, y2), (x2, max(y2 - line_length_y, y1)), color, thickness)  # bottom-right
    cv2.line(img, (x2, y2), (max(x2 - line_length_x, x1), y2), color, thickness)

    return img

# Load results from CSV
results = pd.read_csv('./test_interpolated.csv')

# Load video
video_path = 's3.mp4'
cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('./out3.mp4', fourcc, fps, (width, height))

license_plate = {}

# Process best frame per car
for car_id in np.unique(results['car_id']):
    car_rows = results[results['car_id'] == car_id]
    max_score = np.amax(car_rows['license_number_score'])
    best_row = car_rows[car_rows['license_number_score'] == max_score]

    if best_row.empty:
        continue

    license_plate[car_id] = {
        'license_crop': None,
        'license_plate_number': best_row['license_number'].iloc[0]
    }

    cap.set(cv2.CAP_PROP_POS_FRAMES, best_row['frame_nmr'].iloc[0])
    ret, frame = cap.read()
    if not ret:
        continue

    try:
        bbox_str = best_row['license_plate_bbox'].iloc[0]
        x1, y1, x2, y2 = map(int, ast.literal_eval(bbox_str.replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ',')))

        license_crop = frame[y1:y2, x1:x2]
        if license_crop.size > 0 and (y2 - y1) > 0:
            new_width = int((x2 - x1) * 400 / (y2 - y1))
            license_crop = cv2.resize(license_crop, (new_width, 400))
        else:
            license_crop = np.zeros((400, 600, 3), dtype=np.uint8)

        license_plate[car_id]['license_crop'] = license_crop
    except:
        license_plate[car_id]['license_crop'] = np.zeros((400, 600, 3), dtype=np.uint8)

# Reset video to beginning
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
frame_nmr = -1

# Frame processing loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_nmr += 1

    df_ = results[results['frame_nmr'] == frame_nmr]

    for idx, row in df_.iterrows():
        car_id = row['car_id']

        # --- Car bounding box ---
        try:
            car_x1, car_y1, car_x2, car_y2 = map(int, ast.literal_eval(row['car_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ',')))
            draw_border(frame, (car_x1, car_y1), (car_x2, car_y2), (0, 255, 0), 25)
        except:
            continue

        # --- License Plate bounding box ---
        try:
            lp_x1, lp_y1, lp_x2, lp_y2 = map(int, ast.literal_eval(row['license_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ',')))
            cv2.rectangle(frame, (lp_x1, lp_y1), (lp_x2, lp_y2), (0, 0, 255), 12)
        except:
            continue

        # --- Insert License Plate Image and Text ---
        try:
            license_crop = license_plate[car_id]['license_crop']
            plate_text = license_plate[car_id]['license_plate_number']
            H, W, _ = license_crop.shape

            insert_y1 = max(0, car_y1 - H - 100)
            insert_y2 = insert_y1 + H
            insert_x1 = max(0, int((car_x1 + car_x2 - W) / 2))
            insert_x2 = insert_x1 + W

            if insert_y2 < height and insert_x2 < width:
                frame[insert_y1:insert_y2, insert_x1:insert_x2] = license_crop

                # White background for text
                bg_y1 = max(0, insert_y1 - 300)
                bg_y2 = insert_y1
                frame[bg_y1:bg_y2, insert_x1:insert_x2] = (255, 255, 255)

                # Text
                (text_width, text_height), _ = cv2.getTextSize(plate_text, cv2.FONT_HERSHEY_SIMPLEX, 3.2, 10)
                text_x = insert_x1 + (W - text_width) // 2
                text_y = bg_y1 + (300 + text_height) // 2 - 10

                cv2.putText(frame, plate_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 3.2, (0, 0, 0), 10)
        except:
            continue

    out.write(frame)

    # Optional live preview (uncomment if needed)
    # resized = cv2.resize(frame, (1280, 720))
    # cv2.imshow('Frame', resized)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cap.release()
out.release()
