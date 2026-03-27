import streamlit as st
import datetime
# 設定頁面配置
st.set_page_config(page_title="期權商品規格建檔系統", layout="wide", initial_sidebar_state="collapsed")
# 隱藏 Streamlit 預設選單與 Footer，維持介面潔淨
hide_st_style = """
<style>
           #MainMenu {visibility: hidden;}
           footer {visibility: hidden;}
           header {visibility: hidden;}
</style>
           """
st.markdown(hide_st_style, unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# 字典定義與資料源 (保留原始內容)
# -----------------------------------------------------------------------------
PRODUCTS = {
   'OMWP': {
       'id': 'OMWP', 'exchange': 'EUREX', 'type': 'index', 'underlying': 'MSCI Taiwan Index',
       'multiplier': '100', 'style': 'european', 'currency': 'USD',
       'settlement': 'cash', 'timing': 'standard', 'cycle': 'monthly', 'expiryRule': '3rd_wed',
       'explanations': [
           "**[2. a 歐式履約]**：僅能在到期日當天提出履約要求，盤中不接受提前履約。",
           "**[4. a 現金結算]**：指數無法實體持有。到期時，系統自動比對結算價，直接將「差價盈虧」以美金 (USD) 撥入或扣除客戶帳戶。不涉及任何現貨部位轉換。",
           "**[8. a 到期日規則]**：系統將自動依照「每月第三個星期三」生成未來各月份的合約序列。"
       ]
   },
   'OESX': {
       'id': 'OESX', 'exchange': 'EUREX', 'type': 'index', 'underlying': 'EURO STOXX 50 Index',
       'multiplier': '10', 'style': 'european', 'currency': 'EUR',
       'settlement': 'cash', 'timing': 'standard', 'cycle': 'monthly', 'expiryRule': '3rd_fri',
       'explanations': [
           "**[2. a 歐式履約]**：僅能在到期日當天提出履約要求，盤中不接受提前履約。",
           "**[4. a 現金結算]**：指數無法實體持有。到期時，系統自動比對結算價，直接將「差價盈虧」以歐元 (EUR) 撥入或扣除客戶帳戶。",
           "**[8. b 到期日規則]**：系統將自動依照「每月第三個星期五」生成未來各月份的合約序列。"
       ]
   },
   'SPX': {
       'id': 'SPX', 'exchange': 'CBOE', 'type': 'index', 'underlying': '$SPX',
       'multiplier': '100', 'style': 'european', 'currency': 'USD',
       'settlement': 'cash', 'timing': 'pm', 'cycle': 'daily', 'expiryRule': 'daily',
       'explanations': [
           "**[2. a 歐式履約]**：僅能在到期日提出履約要求。",
           "**[4. a 現金結算]**：直接以美金差額結算盈虧。",
           "**[5. b 客製化 PM 結算注意]**：此商品設定為收盤結算。系統將於到期日美東時間 16:00 抓取最後一筆指數收盤價作為結算依據，而非隔日開盤價。",
           "**[8. d 到期日規則]**：支援 0DTE，系統每日自動生成當日到期的新合約。"
       ]
   },
   'SPY': {
       'id': 'SPY', 'exchange': 'CBOE', 'type': 'etf', 'underlying': 'SPY ETF',
       'multiplier': '100', 'style': 'american', 'currency': 'USD',
       'settlement': 'physical', 'timing': 'standard', 'cycle': 'weekly', 'expiryRule': 'weekly_fri',
       'explanations': [
           "**[2. b 美式履約]**：買方可在到期日前的任何交易日，隨時提出「提前履約 (Early Exercise)」。後台需支援逐日履約指派作業。",
           "**[4. b 實物結算注意]**：若到期時為價內 (ITM)，系統將進行「部位轉換」。買方需有足夠資金買入 SPY 現貨；賣方可能被指派賣出 SPY 現貨。系統風控需連動檢核 T+1 / T+2 的交割保證金是否充足。"
       ]
   },
   'TXO': {
       'id': 'TXO', 'exchange': 'TAIFEX', 'type': 'index', 'underlying': 'TAIEX',
       'multiplier': '50', 'style': 'european', 'currency': 'TWD',
       'settlement': 'cash', 'timing': 'standard', 'cycle': 'monthly', 'expiryRule': '3rd_wed',
       'explanations': [
           "**[2. a 歐式履約]**：僅能在到期日當天提出履約要求，盤中不接受提前履約。",
           "**[4. a 現金結算]**：台灣期交所台指選擇權。到期時直接以新台幣 (TWD) 進行差價盈虧撥補，不涉及現貨部位轉換。",
           "**[8. a 到期日規則]**：系統將自動依照「每月第三個星期三」生成未來各月份的合約序列。"
       ]
   },
   'QQQ': {
       'id': 'QQQ', 'exchange': 'CBOE', 'type': 'etf', 'underlying': 'QQQ ETF',
       'multiplier': '100', 'style': 'american', 'currency': 'USD',
       'settlement': 'physical', 'timing': 'standard', 'cycle': 'weekly', 'expiryRule': 'weekly_fri',
       'explanations': [
           "**[2. b 美式履約]**：買方可在到期日前的任何交易日，隨時提出「提前履約 (Early Exercise)」。",
           "**[4. b 實物結算注意]**：若到期時為價內 (ITM)，系統將轉換為 QQQ 現貨部位。請特別留意客戶帳戶是否具備足夠的交割款餘額或現貨庫存。"
       ]
   }
}
# 下拉選單對應字典
MAPPINGS = {
   'products': {
       'SPX': 'SPX - S&P 500 Index Options (SP 500選擇權客製化 PM 結算)',
       'SPY': 'SPY - SPDR S&P 500 ETF Options (SPY ETF 選擇權)',
       'OMWP': 'OMWP - MSCI Taiwan Index Options (MSCI世界指數選擇權)',
       'OESX': 'OESX - EURO STOXX 50 Index Options (歐洲藍籌50指數選擇權)',
       'TXO': 'TXO - Taiwan Index Options (台指選擇權)',
       'QQQ': 'QQQ - Invesco QQQ ETF Options (QQQ ETF 選擇權)'
   },
   'exchange': {
       'CBOE': '6. a CBOE - 芝加哥選擇權',
       'TAIFEX': '6. b TAIFEX - 台灣期交所',
       'EUREX': '6. c EUREX - 歐洲期交所'
   },
   'type': {
       'index': '1. a 指數選擇權 (Index Option)',
       'etf': '1. b ETF 選擇權 (ETF Option)'
   },
   'style': {
       'european': '2. a 歐式 (European)',
       'american': '2. b 美式 (American)'
   },
   'currency': {
       'USD': '3. a USD - 美元',
       'EUR': '3. b EUR - 歐元',
       'TWD': '3. c TWD - 新台幣'
   },
   'settlement': {
       'cash': '4. a 現金結算 (Cash Settlement)',
       'physical': '4. b 實物結算 (Physical Settlement)'
   },
   'timing': {
       'standard': '5. a 標準 (Standard) - 依交易所預設',
       'pm': '5. b 客製化 PM (PM-Settled) - 收盤結算'
   },
   'cycle': {
       'monthly': '7. a 標準月選 (Monthly)',
       'weekly': '7. b 週選擇權 (Weekly)',
       'daily': '7. c 每日到期 (0DTE)'
   },
   'expiryRule': {
       '3rd_wed': '8. a 每月第三個星期三',
       '3rd_fri': '8. b 每月第三個星期五',
       'weekly_fri': '8. c 每週五 (週權)',
       'daily': '8. d 每日產生 (0DTE)'
   }
}
# -----------------------------------------------------------------------------
# 頂部狀態列
# -----------------------------------------------------------------------------
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
   st.title("商品規格建檔系統")
with col_header2:
   st.write("") # 排版用空白
   st.markdown("**狀態：建檔中**")
   if st.button("儲存設定", type="primary", use_container_width=True):
       st.success("設定已儲存 (系統展示用)")
st.divider()
# -----------------------------------------------------------------------------
# 0. 商品選擇
# -----------------------------------------------------------------------------
st.markdown("### 請選擇建檔商品 (Select Product)")
selected_pid = st.selectbox(
   "商品",
   options=list(MAPPINGS['products'].keys()),
   format_func=lambda x: MAPPINGS['products'][x],
   label_visibility="collapsed"
)
# 取得目前選擇的商品資料
p_data = PRODUCTS[selected_pid]
# -----------------------------------------------------------------------------
# A. 基本資料
# -----------------------------------------------------------------------------
st.markdown("#### A. 基本資料 (Basic Info)")
col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
   st.text_input("交易所 (Exchange)", value=MAPPINGS['exchange'][p_data['exchange']], disabled=True)
with col_a2:
   st.text_input("商品類別 (Product Type)", value=MAPPINGS['type'][p_data['type']], disabled=True)
with col_a3:
   st.text_input("標的物 (Underlying)", value=p_data['underlying'], disabled=True)
st.write("") # 排版間距
# -----------------------------------------------------------------------------
# B. 合約規格
# -----------------------------------------------------------------------------
st.markdown("#### B. 合約規格 (Contract Specs)")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
   st.text_input("契約乘數 (Multiplier)", value=p_data['multiplier'])
with col_b2:
   style_keys = list(MAPPINGS['style'].keys())
   st.selectbox(
       "履約方式 (Exercise Style)",
       options=style_keys,
       index=style_keys.index(p_data['style']),
       format_func=lambda x: MAPPINGS['style'][x]
   )
with col_b3:
   currency_keys = list(MAPPINGS['currency'].keys())
   st.selectbox(
       "交易幣別 (Currency)",
       options=currency_keys,
       index=currency_keys.index(p_data['currency']),
       format_func=lambda x: MAPPINGS['currency'][x]
   )
st.write("")
# -----------------------------------------------------------------------------
# C. 結算與到期設定
# -----------------------------------------------------------------------------
st.markdown("#### C. 結算與到期設定 (Settlement)")
col_c1, col_c2 = st.columns(2)
with col_c1:
   settlement_keys = list(MAPPINGS['settlement'].keys())
   st.selectbox(
       "結算方式 (Settlement Type)",
       options=settlement_keys,
       index=settlement_keys.index(p_data['settlement']),
       format_func=lambda x: MAPPINGS['settlement'][x]
   )
   cycle_keys = list(MAPPINGS['cycle'].keys())
   st.selectbox(
       "結算週期 (Expiry Cycle)",
       options=cycle_keys,
       index=cycle_keys.index(p_data['cycle']),
       format_func=lambda x: MAPPINGS['cycle'][x]
   )
with col_c2:
   timing_keys = list(MAPPINGS['timing'].keys())
   st.selectbox(
       "結算時間判定 (Timing)",
       options=timing_keys,
       index=timing_keys.index(p_data['timing']),
       format_func=lambda x: MAPPINGS['timing'][x]
   )
   rule_keys = list(MAPPINGS['expiryRule'].keys())
   st.selectbox(
       "自動到期日規則 (Expiry Rule)",
       options=rule_keys,
       index=rule_keys.index(p_data['expiryRule']),
       format_func=lambda x: MAPPINGS['expiryRule'][x]
   )
st.write("")
# 特定客製到期日 & 警示設定
st.markdown("**特定客製到期日 (Custom Expiry Date) & 特定覆寫設定**")
col_date, col_alert = st.columns(2)
with col_date:
   custom_date = st.date_input("選擇到期日", value=None, label_visibility="collapsed")
   if custom_date:
       weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
       st.caption(f"換算結果：{weekdays[custom_date.weekday()]}")
with col_alert:
   # 依據防呆邏輯，有選日期才解鎖警示設定
   is_disabled = custom_date is None
   alert_toggle = st.checkbox("10. 提早 3 日警示", disabled=is_disabled)
st.caption("※ 防呆提示：若有自訂到期日需求，請選擇西元日期。系統會自動換算星期供核對。選定日期後，即可解鎖右側「提早 3 日警示」功能，確保營運同仁能提早收到風控通知。")
st.divider()
# -----------------------------------------------------------------------------
# 商品規格說明與系統防呆提示
# -----------------------------------------------------------------------------
st.markdown("#### 商品規格說明與系統防呆提示")
for exp in p_data['explanations']:
   st.info(exp, icon=None) # 確保無預設 icon
st.write("")
# -----------------------------------------------------------------------------
# 商品參數標準字典 (跨部門共通規格)
# -----------------------------------------------------------------------------
with st.expander("商品參數標準字典 (跨部門共通規格)", expanded=False):
   col_dict1, col_dict2, col_dict3 = st.columns(3)
   with col_dict1:
       st.markdown("**0. 建檔商品 (Product Symbol)**")
       st.markdown("- MSCI 台灣指數選擇權：`OMWP`\n- 歐洲藍籌50指數選擇權：`OESX`\n- S&P 500 指數選擇權：`SPX`\n- SPY ETF 選擇權：`SPY`\n- 台指選擇權：`TXO`\n- QQQ ETF 選擇權：`QQQ`")
       st.markdown("**1. 商品類別 (Product Type)**")
       st.markdown("- 1. a 指數選擇權：`index`\n- 1. b ETF 選擇權：`etf`")
       st.markdown("**2. 履約方式 (Exercise Style)**")
       st.markdown("- 2. a 歐式：`european`\n- 2. b 美式：`american`")
   with col_dict2:
       st.markdown("**3. 交易幣別 (Currency)**")
       st.markdown("- 3. a 美元：`USD`\n- 3. b 歐元：`EUR`\n- 3. c 新台幣：`TWD`")
       st.markdown("**4. 結算方式 (Settlement)**")
       st.markdown("- 4. a 現金結算：`cash`\n- 4. b 實物結算：`physical`")
       st.markdown("**5. 結算時間 (Timing)**")
       st.markdown("- 5. a 標準：`standard`\n- 5. b 客製化 PM：`pm`")
       st.markdown("**6. 交易所 (Exchange)**")
       st.markdown("- 6. a CBOE：`CBOE`\n- 6. b TAIFEX：`TAIFEX`\n- 6. c EUREX：`EUREX`")
   with col_dict3:
       st.markdown("**7. 結算週期 (Expiry Cycle)**")
       st.markdown("- 7. a 標準月選：`monthly`\n- 7. b 週選擇權：`weekly`\n- 7. c 每日到期：`daily`")
       st.markdown("**8. 到期日規則 (Expiry Rule)**")
       st.markdown("- 8. a 第三個週三：`3rd_wed`\n- 8. b 第三個週五：`3rd_fri`\n- 8. c 每週五：`weekly_fri`\n- 8. d 每日產生：`daily`")
       st.markdown("**9. 特定客製到期日 & 10. 到期前警示**")
       st.markdown("- 日期格式：`YYYY-MM-DD`\n- 啟用警示：`true` / 停用：`false`")
