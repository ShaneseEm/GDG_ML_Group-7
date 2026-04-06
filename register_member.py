import os
from datetime import datetime

import cv2
from insightface.app import FaceAnalysis


def validate_name(raw_name: str) -> str:
    name = raw_name.strip()
    if not name:
        return ""
    if os.sep in name or (os.altsep and os.altsep in name):
        return ""
    if name in {".", ".."}:
        return ""
    return name


def main() -> None:
    print("=== Member Registration ===")
    name_input = input("Enter member name: ")
    member_name = validate_name(name_input)

    if not member_name:
        print("❌ Invalid name. Use a non-empty name without path characters.")
        return

    db_root = "faces_db"
    person_dir = os.path.join(db_root, member_name)
    os.makedirs(person_dir, exist_ok=True)

    print(f"Folder ready: {person_dir}")

    print("Loading ArcFace model...")
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=-1, det_size=(640, 640))

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access camera.")
        return

    print("Camera started ✅")
    saved_count = 0

    gui_mode = True
    try:
        cv2.namedWindow("Register Member", cv2.WINDOW_NORMAL)
    except cv2.error:
        gui_mode = False

    if gui_mode:
        print("Press 'C' to capture and save a frame, press 'Q' to finish.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read camera frame.")
                break

            cv2.putText(
                frame,
                "C: Capture  Q: Quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            try:
                cv2.imshow("Register Member", frame)
            except cv2.error:
                gui_mode = False
                print("⚠️ GUI preview not available. Switching to terminal capture mode.")
                break

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("c"), ord("C")):
                faces = app.get(frame)
                if len(faces) == 0:
                    print("⚠️ No face detected. Capture not saved.")
                    continue

                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                destination = os.path.join(person_dir, filename)
                cv2.imwrite(destination, frame)
                saved_count += 1
                print(f"✅ Saved: {destination}")

            if key in (ord("q"), ord("Q")):
                break

    if not gui_mode:
        print("Terminal mode:")
        print("Type 'c' then Enter to capture, or 'q' then Enter to quit.")
        while True:
            command = input("Command [c/q]: ").strip().lower()
            if command == "q":
                break
            if command != "c":
                print("⚠️ Invalid command. Use 'c' or 'q'.")
                continue

            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read camera frame.")
                continue

            faces = app.get(frame)
            if len(faces) == 0:
                print("⚠️ No face detected. Capture not saved.")
                continue

            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            destination = os.path.join(person_dir, filename)
            cv2.imwrite(destination, frame)
            saved_count += 1
            print(f"✅ Saved: {destination}")

    cap.release()
    cv2.destroyAllWindows()

    print(f"Session ended. Total images saved for {member_name}: {saved_count}")
    print("Now run face_recogntion.py again to load the updated database.")


if __name__ == "__main__":
    main()
