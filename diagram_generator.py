import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, blue, green  # 例として色を追加
import json
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import matplotlib.font_manager as fm  # フォント検索用

def load_timetable_data(folder_path="time_tables", use_mock_data=False):
    """
    指定したフォルダ内のJSONファイルから時刻表データを読み込む関数。

    Args:
        folder_path (str, optional): 時刻表データが格納されたフォルダのパス。
                                     デフォルトは "time_tables"。
        use_mock_data (bool, optional): モックデータを使用するかどうか。
                                       モックデータを使用する場合はTrueに設定。
                                       デフォルトはFalse。

    Returns:
        dict: 駅名をキーとし、時刻表データのリストを値とする辞書。
              例: {
                  "渋谷": [
                      {"時刻": "05:00", "種別": "各駅停車", "行き先": "元町・中華街"},
                      {"時刻": "05:16", "種別": "各駅停車", "行き先": "元町・中華街"},
                      ...
                  ],
                  "中目黒": [
                      {"時刻": "05:04", "種別": "各停", "行き先": "元町・中華街"},
                      {"時刻": "05:20", "種別": "各停", "行き先": "元町・中華街"},
                      ...
                  ],
                  ...
              }
              ファイルが存在しない場合や読み込みに失敗した場合は、
              空の辞書を返す。
    """

    timetable_data = {}

    if use_mock_data:
        # モックデータを生成する処理
        # ここでは、モックデータを返す関数などを呼び出す
        # 例: timetable_data = get_mock_timetable_data()
        # モックデータは、実際のデータと同じ形式の辞書に格納する
        #timetable_data = get_mock_timetable_data()
        pass  # 後で実装
    else:
        # フォルダ内のJSONファイルを読み込む処理
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # ファイル名から駅名を取得 (例: "shibuya_timetable.json" -> "渋谷")
                        station_name = filename.split("_")[0].capitalize()
                        timetable_data[station_name] = data
        except FileNotFoundError:
            print(f"Error: Folder '{folder_path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in files in '{folder_path}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    return timetable_data


def create_diagram(timetable_data, stations, file_path="diagram.pdf"):
    """
    時刻表データからダイヤグラムを生成し、PDFファイルとして出力する関数。

    Args:
        timetable_data (dict): 駅名と時刻表データの辞書
        stations (list): 駅名のリスト（上から順）
        file_path (str, optional): 出力するPDFファイルのパス。デフォルトは "diagram.pdf"。
    """

    # PDFキャンバスの初期化
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # フォントの登録
    try:
        # UnicodeCIDFontを使用して簡単に日本語フォントを設定
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        c.setFont("HeiseiKakuGo-W5", 10)  # フォント設定
    except Exception as e:
        print(f"フォントの登録に失敗しました: {e}")
        return

    # ダイヤグラムの描画範囲を定義
    diagram_top = 50 * mm
    diagram_bottom = (height - 50) * mm
    diagram_left = 20 * mm
    diagram_right = (width - 20) * mm

    # 縦軸（駅）の描画
    num_stations = len(stations)
    station_interval = (diagram_bottom - diagram_top) / (num_stations - 1)  # 駅間隔を計算

    for i, station in enumerate(stations):
        y = diagram_bottom - i * station_interval
        c.drawString(diagram_left - 10 * mm, y, station)  # 駅名を描画
        c.line(diagram_left, y, diagram_right, y)  # 水平線を描画

    # 横軸（時刻）の描画
    start_time = "05:00"  # ダイヤグラムの開始時刻
    end_time = "24:00"    # ダイヤグラムの終了時刻
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))
    total_minutes = (end_hour - start_hour) * 60 + (end_minute - start_minute)
    time_interval = (diagram_right - diagram_left) / total_minutes  # 時間間隔を計算

    for hour in range(start_hour, end_hour + 1):
        if hour % 2 == 0:  # 2時間ごとに時刻を描画
            time_str = f"{hour:02d}:00"
            hour_minutes = (hour - start_hour) * 60
            x = diagram_left + hour_minutes * time_interval
            c.drawString(x, diagram_bottom + 5 * mm, time_str)  # 時刻を描画
            c.line(x, diagram_top, x, diagram_bottom)  # 垂直線を描画

    # 列車データの描画
    train_colors = {
        "特急": red,
        "急行": blue,
        "各停": black,
        "通勤特急": green,
        "Fライナ": red  # 仮の色
    }

    for station_idx, station in enumerate(stations):
        for train in timetable_data.get(station,):
            時刻 = train["時刻"]
            種別 = train["種別"]
            行き先 = train["行き先"]

            hour, minute = map(int, 時刻.replace('時台','').replace('分','').split('時'))
            train_minutes = (hour - start_hour) * 60 + minute
            x = diagram_left + train_minutes * time_interval
            y = diagram_bottom - station_idx * station_interval

            # 列車種別に応じた色を取得、存在しない場合は黒
            color = train_colors.get(種別, black)
            c.setFillColor(color)
            c.circle(x, y, 1 * mm, fill=1)  # 列車の点を描画

    c.save()
    print(f"ダイヤグラムを生成しました: {file_path}")

if __name__ == "__main__":
    # 時刻表データを読み込む
    # use_mock_dataをTrueにするとモックデータを使用
    timetable_data = load_timetable_data(use_mock_data=False)

    # 駅名リスト（上から順）
    # 実際の駅名に合わせて修正してください
    stations = list(timetable_data.keys())  # timetable_dataのキーを駅名として使用

    if timetable_data:
        # ダイヤグラムを生成
        create_diagram(timetable_data, stations)
    else:
        print("時刻表データの読み込みに失敗しました。")