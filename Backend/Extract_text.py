import easyocr
import os
import subprocess

def extract_text_from_image(image_path, output_file="output.txt"):
    # Initialize EasyOCR
    reader = easyocr.Reader(['en'], gpu=False)

    # Perform OCR
    results = reader.readtext(image_path)

    # Sort results by line (Y position) then by word (X position)
    lines = []
    current_y = -1
    current_line = []

    for box, text, _ in sorted(results, key=lambda x: (x[0][0][1], x[0][0][0])):
        y = int(box[0][1])

        if current_y == -1:
            current_y = y

        # New line if Y distance is significant
        if abs(y - current_y) > 15:
            lines.append(" ".join(current_line))
            current_line = [text]
            current_y = y
        else:
            current_line.append(text)

    if current_line:
        lines.append(" ".join(current_line))

    # Join all lines into final output
    final_text = "\n".join(lines)

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    # Open in Notepad
    subprocess.Popen(["notepad.exe", os.path.abspath(output_file)])

    print("✅ Extracted text saved and opened in Notepad.")

if __name__ == "__main__":
    image_path = input("📸 Enter path of the image: ").strip()
    extract_text_from_image(image_path)
