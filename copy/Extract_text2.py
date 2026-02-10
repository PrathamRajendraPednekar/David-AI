import easyocr
import os
import subprocess

def extract_text_from_image(image_path, output_file="ExtractedText.txt"):
    # Initialize EasyOCR Reader
    reader = easyocr.Reader(['en'], gpu=False)

    # Perform OCR
    results = reader.readtext(image_path)

    # Group text lines by vertical Y position
    lines = []
    current_y = -1
    current_line = []

    for box, text, _ in sorted(results, key=lambda x: (x[0][0][1], x[0][0][0])):
        y = int(box[0][1])

        if current_y == -1:
            current_y = y

        # Check if this text is on a new line
        if abs(y - current_y) > 15:
            lines.append(" ".join(current_line))
            current_line = [text]
            current_y = y
        else:
            current_line.append(text)

    if current_line:
        lines.append(" ".join(current_line))

    # ✅ Preserve line-by-line layout (just like in the image)
    final_text = "\n".join(lines)

    # Save the extracted text to a file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    # Open in Notepad
    subprocess.Popen(["notepad.exe", os.path.abspath(output_file)])

    print("✅ Text extracted and opened in Notepad with original alignment.")

# 🔹 Example usage
if __name__ == "__main__":
    image_path = input("📷 Enter path of the image: ").strip()
    extract_text_from_image(image_path)
