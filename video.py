import cv2

cap = cv2.VideoCapture(0)  # Replace with the correct index
if not cap.isOpened():
    print("Unable to access the camera")
else:
    print("Camera is accessible")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Failed to grab frame")
cap.release()
cv2.destroyAllWindows()
