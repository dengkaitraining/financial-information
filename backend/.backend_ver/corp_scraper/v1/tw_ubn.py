import requests

def get_business_info(tax_id):
    # 經濟部商業登記基本資料 API
    url = f"https://data.gcis.nat.gov.tw/od/data/api/A082215A-612A-4B07-A587-578B228B0D23?$format=json&$filter=President_No eq {tax_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            info = data[0]
            print("=== 商業登記基本資料 ===")
            print(f"商業名稱: {info.get('Business_Name')}")
            print(f"統一編號: {info.get('President_No')}")
            print(f"負責人: {info.get('Responsible_Name')}")
            print(f"現況: {info.get('Business_Current_Status_Desc')}")
            print(f"資本額: {info.get('Capital_Amount')} 元")
            print(f"商業地址: {info.get('Business_Address')}")
            print(f"組織類型: {info.get('Organization_Type_Desc')}")
            print(f"設立日期: {info.get('Register_Date')}")
            return info
        else:
            print("查無此統一編號的商業登記資料。")
            return None

    except Exception as e:
        print(f"請求發生錯誤: {e}")
        return None


# 測試：輸入商業登記的統一編號
get_business_info("41012345")  # 請替換為欲查詢的行號統編