
import pandas as pd
import json
import os
import pandas as pd
import json
import os
import time
# utils에 있는 강력한 병렬 처리 함수 가져오기
import utils

# 설정
# 기존 엑셀 대신 구글 시트 사용
GOOGLE_SHEET_ID = "17JU4KoC-Out5NqGy3qtN7LSunMUsH5xS2qJSk1fBDGQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv"

OUTPUT_FILE = "static/result.json"

def main():
    if not os.path.exists('static'):
        os.makedirs('static')

    print(f"[{time.strftime('%X')}] 구글 시트 데이터 로드 중...")
    # Load Tickers
    print("구글 시트 데이터 로드 중...")
    ticker_info_list = utils.get_tickers_from_google_sheet(GOOGLE_SHEET_URL)
    
    # 2. 실패 시 Fallback
    if not ticker_info_list:
        print("⚠️ 구글 시트 로드 실패 (Fallback 모드)")
        # 주요 나스닥/S&P500 티커 Fallback
        ticker_info_list = [
            {"Ticker": "AAPL", "Sector": "Technology", "Industry": "Consumer Electronics"},
            {"Ticker": "MSFT", "Sector": "Technology", "Industry": "Software - Infrastructure"},
            {"Ticker": "NVDA", "Sector": "Technology", "Industry": "Semiconductors"},
            {"Ticker": "GOOGL", "Sector": "Communication Services", "Industry": "Internet Content & Information"},
            {"Ticker": "AMZN", "Sector": "Consumer Cyclical", "Industry": "Internet Retail"},
            {"Ticker": "TSLA", "Sector": "Consumer Cyclical", "Industry": "Auto Manufacturers"},
            {"Ticker": "META", "Sector": "Communication Services", "Industry": "Internet Content & Information"},
            {"Ticker": "AMD", "Sector": "Technology", "Industry": "Semiconductors"},
            {"Ticker": "NFLX", "Sector": "Communication Services", "Industry": "Entertainment"},
            {"Ticker": "PLTR", "Sector": "Technology", "Industry": "Software - Infrastructure"}
        ]
    else:
        print(f"[{time.strftime('%X')}] 대상 티커: {len(ticker_info_list)}개")
    
    start_time = time.time()
    
    # 병렬 처리 함수 실행 (20개씩 동시 작업)
    try:
        results = utils.get_market_cap_and_rs(ticker_info_list)
    except Exception as e:
        print(f"수집 중 에러 발생: {e}")
        results = []
    
    
    # Save Sector Cache (Persistence)
    utils.save_sector_cache()

    end_time = time.time()
    duration = end_time - start_time
    
    print(f"[{time.strftime('%X')}] 수집 완료! 소요 시간: {duration:.1f}초, 성공: {len(results)}개")

    # ===== 퍼센타일 순위 계산 =====
    print(f"[{time.strftime('%X')}] RS 퍼센타일 순위 계산 중...")
    
    # 개별 RS(6MO) 퍼센타일
    rs_6mo_values = [r['RS_6mo'] for r in results if r.get('RS_6mo') is not None]
    for item in results:
        rs_val = item.get('RS_6mo')
        item['RS_Rank_Pct'] = utils.calculate_percentile_rank(rs_val, rs_6mo_values)
    
    # WRS 계산을 위한 Sector/Industry 그룹핑
    from collections import defaultdict
    import statistics
    
    sector_groups = defaultdict(list)
    for item in results:
        if (item.get('Sector') and item['Sector'] not in ['N/A', 'nan'] and
            item.get('Industry') and item['Industry'] not in ['N/A', 'nan'] and
            item.get('RS_6mo') is not None):
            key = f"{item['Sector']}|{item['Industry']}"
            sector_groups[key].append(item['RS_6mo'])
    
    # WRS 데이터 생성 (중앙값 포함)
    wrs_data = []
    for key, rs_values in sector_groups.items():
        if len(rs_values) >= 1:  # 최소 1개 이상
            sector, industry = key.split('|')
            median_rs = statistics.median(rs_values)
            wrs_data.append({
                'Sector': sector,
                'Industry': industry,
                'Count': len(rs_values),
                'WRS_6mo_MD': round(median_rs, 4)
            })
    
    # WRS 중앙값 퍼센타일 계산
    wrs_md_values = [w['WRS_6mo_MD'] for w in wrs_data]
    for wrs_item in wrs_data:
        wrs_item['WRS_MD_Rank_Pct'] = utils.calculate_percentile_rank(wrs_item['WRS_6mo_MD'], wrs_md_values)
    
    # ===== Market Condition 가져오기 =====
    print(f"[{time.strftime('%X')}] Market Condition 가져오는 중...")
    market_condition = utils.get_market_condition_from_sheet()
    print(f"  → Market Condition: {market_condition}")

    output_data = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_count": len(results),
        "market_condition": market_condition,
        "wrs_data": wrs_data,
        "data": results
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"결과 파일 저장 완료: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
