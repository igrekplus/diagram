import requests

def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Content fetched successfully!")
        print(response.text[:200])  # 最初の200文字を表示
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")

if __name__ == "__main__":
    test_url = "https://www.example.com"
    fetch_url_content(test_url)
