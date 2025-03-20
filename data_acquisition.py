import requests
from bs4 import BeautifulSoup
import logging
import json
from timetable_mock import get_mock_timetable_data  # 追加
import os  # 追加

def get_timetable_data(url):
    """
    NAVITIMEの時刻表ページからHTMLを取得し、必要なデータを抽出する。

    Args:
        url (str): NAVITIMEの時刻表ページのURL

    Returns:
        dict: 時刻表データを格納した辞書
              例: {
                  "時刻": "05:00",
                  "種別": "各駅停車",
                  "行き先": "元町・中華街"
              }
              取得失敗時はNoneを返す
    """
    timetable_data = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # エラーレスポンスをチェック
        response.encoding = "UTF-8"

        # HTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        # 時刻表データを抽出
        # 例: 時刻、種別、行き先の情報を抽出する処理
        # ここでは、NAVITIMEのHTML構造に合わせて抽出処理を記述する必要があります
        # 具体的な抽出方法は、NAVITIMEのHTML構造に依存するため、
        # 実際のHTMLを確認しながら実装する必要があります
        # 以下はあくまで例です

        # 例: tableタグから時刻、種別、行き先の情報を抽出する
        # この部分は、NAVITIMEのHTML構造に合わせて修正する必要があります
        time_table = soup.find("div", id="diagram-table-weekday")
        if time_table:
            rows = time_table.find_all("dt")
            for row in rows:
                時刻 = row.find("div", {"aria-hidden": "true"}).text.strip()
                時刻 = f"{時刻}時台"
                時刻表 = row.find_next_sibling("dd")
                trains = 時刻表.find_all("a")
                for train in trains:
                    種別 = train.find("div", class_="topLegends").get("data-text")
                    行き先 = train.find("div", class_="destination").text.strip()
                    if not 行き先:  # 行き先が空の場合
                        行き先 = "元町・中華街"
                    時刻分 = train.find("div", class_="minute").text.strip()

                    timetable_data.append({"時刻": f"{時刻}{時刻分}分", "種別": 種別, "行き先": 行き先})
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    finally:
        # JSON形式に変換
        json_data = json.dumps(timetable_data, ensure_ascii=False, indent=2)
        
        # URLからstCdの値を取得してファイル名に使用
        stCd = url.split("stCd=")[1].split("&")[0]
        output_dir = "diagram/time_tables"
        os.makedirs(output_dir, exist_ok=True)  # ディレクトリが存在しない場合は作成
        file_path = os.path.join(output_dir, f"{stCd}_timetable.json")
        
        # JSONデータをファイルに保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_data)
        
    return json_data


if __name__ == "__main__":
    # テスト用のURL
    test_url = "https://transfer.navitime.biz/tokyu/pc/diagram/TrainDiagram?stCd=00006133&rrCd=00000790&updown=1"

    # 時刻表データを取得
    timetable = get_timetable_data(test_url)

    if timetable:
        # 取得したデータを表示
        print(f"取得した時刻表データ: {timetable}")  # 取得成功時のデータ出力
    else:
        print("時刻表データの取得に失敗しました。")  # 取得失敗時のメッセージ
