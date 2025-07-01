DELTA_T_TABLE = {
    -500: 17190,   # 500 BCE
    0: 10583,      # 0 CE
    500: 5700,     # 500 CE
    1000: 1570,    # 1000 CE
    1500: 200,     # 1500 CE
    2000: 64,      # 2000 CE
}

def utc_to_tt(jd_utc: float) -> float:
    delta_t = _estimate_delta_t(jd_utc)
    return jd_utc + delta_t / 86400.0

def _estimate_delta_t(jd: float) -> float:
    year = _jd_to_year(jd)
    years = sorted(DELTA_T_TABLE.keys())
    
    if year < years[0]:
        return DELTA_T_TABLE[years[0]]
    if year > years[-1]:
        return DELTA_T_TABLE[years[-1]]
    
    for i in range(len(years)-1):
        y1, y2 = years[i], years[i+1]
        if y1 <= year <= y2:
            dt1 = DELTA_T_TABLE[y1]
            dt2 = DELTA_T_TABLE[y2]
            return dt1 + (dt2 - dt1) * (year - y1) / (y2 - y1)
    
    return DELTA_T_TABLE[years[0]]

def _jd_to_year(jd: float) -> float:
    return (jd - 1721424.5) / 365.25
