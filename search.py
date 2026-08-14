from google import genai

client = genai.Client(api_key="AIzaSyAn2sznHPfb5Exh1aBDNNoZ4-xOm9k3R1M")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, who is Elon Musk?"
)

print(response.text)
