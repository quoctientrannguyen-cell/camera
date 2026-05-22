import cv2
import numpy as np
import time

# =====================================
# CAMERA
# =====================================

cap = cv2.VideoCapture(0)

# =====================================
# KERNEL
# =====================================

kernel = np.ones((5,5), np.uint8)

# =====================================
# COUNTER
# =====================================

good_count = 0
error_count = 0

# =====================================
# LINE POSITION
# =====================================

line_y = 240

# =====================================
# AVOID DUPLICATE COUNT
# =====================================

detected_objects = []

# =====================================
# FPS
# =====================================

prev_time = 0

# =====================================
# MAIN LOOP
# =====================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # =====================================
    # RESIZE
    # =====================================

    frame = cv2.resize(frame, (640,480))

    # =====================================
    # BLUR
    # =====================================

    blur = cv2.GaussianBlur(frame, (5,5), 0)

    # =====================================
    # HSV
    # =====================================

    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # =====================================
    # RED COLOR MASK
    # =====================================

    lower_red1 = np.array([0,120,70])
    upper_red1 = np.array([10,255,255])

    lower_red2 = np.array([170,120,70])
    upper_red2 = np.array([180,255,255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    # =====================================
    # MORPHOLOGY
    # =====================================

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # =====================================
    # CONTOURS
    # =====================================

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # =====================================
    # DRAW INSPECTION LINE
    # =====================================

    cv2.line(
        frame,
        (0, line_y),
        (640, line_y),
        (255,0,255),
        3
    )

    cv2.putText(
        frame,
        "INSPECTION LINE",
        (220, line_y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,0,255),
        2
    )

    # =====================================
    # LOOP OBJECTS
    # =====================================

    for cnt in contours:

        area = cv2.contourArea(cnt)

        # FILTER SMALL NOISE
        if area > 3000:

            peri = cv2.arcLength(cnt, True)

            approx = cv2.approxPolyDP(
                cnt,
                0.04 * peri,
                True
            )

            x, y, w, h = cv2.boundingRect(approx)

            # =====================================
            # CENTER POINT
            # =====================================

            cx = int(x + w/2)
            cy = int(y + h/2)

            # =====================================
            # CIRCULARITY
            # =====================================

            if peri != 0:
                circularity = (
                    4 * np.pi * area
                ) / (peri * peri)
            else:
                circularity = 0

            # =====================================
            # SHAPE DETECTION
            # =====================================

            shape = "Unknown"

            if len(approx) > 6:
                shape = "Circle"

            elif len(approx) == 4:
                shape = "Square"

            elif len(approx) == 3:
                shape = "Triangle"

            # =====================================
            # INSPECTION LOGIC
            # =====================================

            status = "ERROR"

            if (
                shape == "Circle"
                and 5000 < area < 30000
                and circularity > 0.80
            ):
                status = "GOOD"

            # =====================================
            # COLOR
            # =====================================

            if status == "GOOD":
                color = (0,255,0)

            else:
                color = (0,0,255)

            # =====================================
            # DRAW OBJECT
            # =====================================

            cv2.rectangle(
                frame,
                (x,y),
                (x+w,y+h),
                color,
                3
            )

            # CENTER
            cv2.circle(
                frame,
                (cx,cy),
                5,
                (255,255,255),
                -1
            )

            # =====================================
            # DISPLAY INFO
            # =====================================

            cv2.putText(
                frame,
                f"{shape} | {status}",
                (x,y-15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            cv2.putText(
                frame,
                f"Area: {int(area)}",
                (x,y+h+20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            cv2.putText(
                frame,
                f"Circularity: {circularity:.2f}",
                (x,y+h+45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            # =====================================
            # WARNING DISPLAY
            # =====================================

            if status == "ERROR":

                cv2.putText(
                    frame,
                    "DEFECT PRODUCT!",
                    (200,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,0,255),
                    3
                )

            # =====================================
            # COUNT WHEN CROSS LINE
            # =====================================

            if abs(cy - line_y) < 10:

                object_id = (x,y,w,h)

                if object_id not in detected_objects:

                    detected_objects.append(object_id)

                    if status == "GOOD":

                        good_count += 1

                        print("GOOD PRODUCT")

                    else:

                        error_count += 1

                        print("ERROR PRODUCT")

                        # =====================================
                        # REJECT SIMULATION
                        # =====================================

                        print("SERVO REJECT ACTIVATED")

            # =====================================
            # OBJECT LABEL
            # =====================================

            cv2.putText(
                frame,
                f"ID:{len(detected_objects)}",
                (x,y-40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,0),
                2
            )

    # =====================================
    # FPS CALCULATION
    # =====================================

    current_time = time.time()

    fps = 1 / (current_time - prev_time)

    prev_time = current_time

    # =====================================
    # DISPLAY FPS
    # =====================================

    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (500,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255,255,255),
        2
    )

    # =====================================
    # DISPLAY COUNTER
    # =====================================

    cv2.putText(
        frame,
        f"GOOD: {good_count}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        3
    )

    cv2.putText(
        frame,
        f"ERROR: {error_count}",
        (20,90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,0,255),
        3
    )

    # =====================================
    # TITLE
    # =====================================

    cv2.putText(
        frame,
        "REALTIME INSPECTION SYSTEM",
        (130,470),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255,255,0),
        2
    )

    # =====================================
    # SHOW
    # =====================================

    cv2.imshow("Inspection System", frame)

    cv2.imshow("Mask", mask)

    # =====================================
    # EXIT
    # =====================================

    key = cv2.waitKey(1)

    if key == 27:
        break

# =====================================
# RELEASE
# =====================================

cap.release()

cv2.destroyAllWindows()