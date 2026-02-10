import easyocr
import cv2
import os
import subprocess
from collections import defaultdict

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.adaptiveThreshold(gray, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 9)
    processed_path = "preprocessed_temp.png"
    cv2.imwrite(processed_path, enhanced)
    return processed_path

def extract_text_from_image(image_path, output_file="ExtractedText.txt"):
    # Preprocess the image
    processed_path = preprocess_image(image_path)

    # Initialize EasyOCR
    reader = easyocr.Reader(['en'], gpu=False)

    # Perform OCR
    results = reader.readtext(processed_path)

    # Group words by Y position (line-based alignment)
    line_map = defaultdict(list)
    line_threshold = 20  # vertical grouping threshold

    for box, text, _ in results:
        y = int(box[0][1])
        found_line = False
        for key in list(line_map.keys()):
            if abs(y - key) <= line_threshold:
                line_map[key].append((box[0][0], text))  # x position, text
                found_line = True
                break
        if not found_line:
            line_map[y].append((box[0][0], text))

    # Sort lines by Y and words within lines by X
    ordered_lines = []
    for y in sorted(line_map.keys()):
        line = sorted(line_map[y], key=lambda x: x[0])
        ordered_lines.append(" ".join([word for _, word in line]))

    # Join lines preserving visual order
    final_text = "\n".join(ordered_lines)

    # Save the result
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    # Open in Notepad
    subprocess.Popen(["notepad.exe", os.path.abspath(output_file)])
    print("✅ Text extracted and saved in original order.")

# 🔹 Example usage
if __name__ == "__main__":
    image_path = input("📸 Enter image path: ").strip()
    extract_text_from_image(image_path)
