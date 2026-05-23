import sys
import os
import decimal
import argparse
import pyodbc
from datetime import datetime

# Osiguravamo UTF-8 encoding za Windows konzolu kako bismo crtali cyberpunk grafike bez greške
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ----------------------------
# CONFIG & ESTETIKA (STATIC//VOID Dark Cyber theme)
# ----------------------------
CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=SQUAD;"
    r"Trusted_Connection=yes;"
)

# ANSI boje za futuristički izgled (Dark Navy / Purple / Silver)
C_PURPLE = "\033[95m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_SILVER = "\033[37m"
C_BOLD = "\033[1m"
C_END = "\033[0m"

def draw_header():
    header = f"""
{C_PURPLE}┌────────────────────────────────────────────────────────┐
│               S T A T I C  //  V O I D                 │
│         SMT LINE 003 - PRODUCTION INTELLIGENCE         │
└────────────────────────────────────────────────────────┘{C_END}
"""
    print(header)

def draw_gauge(label: str, value: float):
    # Kreiranje vizuelnog gauge bar-a (širina 20 karaktera)
    bar_width = 25
    filled_width = int(round(value * bar_width))
    # Ako je preko 1.0, limitiramo na 100% za grafiku
    filled_width = min(filled_width, bar_width)
    
    # Izbor boje u zavisnosti od performansi (OEE standardi)
    if value >= 0.85:
        color = C_GREEN
    elif value >= 0.70:
        color = C_YELLOW
    else:
        color = C_RED
        
    bar = "█" * filled_width + "░" * (bar_width - filled_width)
    pct = f"{value*100:6.2f}%"
    print(f"  {C_SILVER}{label:<15}{C_END} | {color}{bar}{C_END} | {C_BOLD}{color}{pct}{C_END}")

def get_connection():
    return pyodbc.connect(CONN_STR, timeout=10)

def analyze_line_003(date_str: str):
    print(f"{C_BLUE}[*] Pokrećem analizu za datum: {date_str} (Line 003)...{C_END}")
    
    query = """
        SELECT 
            f.MachineNm, 
            f.BaseProgramNm, 
            c.IdealCycleSec,
            f.TotalBoard, 
            f.WorkedPcb, 
            f.RunSec, 
            f.StopSec, 
            f.PlaceSec,
            f.TransferSec,
            f.EntryWaitSec,
            f.ExitWaitSec,
            f.HeadPartNg, 
            f.HeadError,
            f.HeadPlace,
            f.PeakBuildSecPerBoard
        FROM Custom_MachineRunFact f WITH (NOLOCK)
        LEFT JOIN Custom_ProgramCycleTime c WITH (NOLOCK)
            ON f.LineCd = c.LineCd AND f.BaseProgramNm = c.BaseProgramNm
        WHERE f.LineCd = '003LINE' AND CAST(f.StartTime AS DATE) = ?
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print(f"{C_YELLOW}[!] Nema podataka u bazi za datum {date_str}.{C_END}")
            return
            
        # Grupisanje i klasifikacija po CL.1 vs CL.2 na osnovu naziva programa
        # (Zasebno računamo ActualProductCnt / TotalBoard)
        data_cl1 = []
        data_cl2 = []
        data_other = []
        
        for r in rows:
            prog_name = str(r[1]).upper()
            
            machine = r[0]
            program = r[1]
            ideal_cycle = r[2]
            total_board = r[3] or 0
            worked_pcb = r[4] or 0
            run_sec = r[5] or 0
            stop_sec = r[6] or 0
            place_sec = r[7] or 0
            transfer_sec = r[8] or 0
            entry_wait_sec = r[9] or 0
            exit_wait_sec = r[10] or 0
            head_part_ng = r[11] or 0
            head_error = r[12] or 0
            head_place = r[13] or 0
            peak_build = r[14] or 0.0
            
            # Izračunavanje metrika po mašini
            avail = float(run_sec) / (run_sec + stop_sec) if (run_sec + stop_sec) > 0 else 0.0
            qual = float(head_place - head_part_ng) / head_place if head_place > 0 else 1.0
            
            ideal = float(ideal_cycle) if ideal_cycle is not None else float(peak_build)
            perf = (total_board * ideal) / run_sec if run_sec > 0 and ideal > 0 else 0.0
            if perf > 1.0:
                perf = 1.0
                
            row_dict = {
                "machine": machine,
                "program": program,
                "total_board": total_board,
                "worked_pcb": worked_pcb,
                "run_sec": run_sec,
                "stop_sec": stop_sec,
                "place_sec": place_sec,
                "transfer_sec": transfer_sec,
                "entry_wait_sec": entry_wait_sec,
                "exit_wait_sec": exit_wait_sec,
                "part_ng": head_part_ng,
                "head_error": head_error,
                "availability": avail,
                "performance": perf,
                "quality": qual
            }
            
            # Pravilo detekcije CL.1 i CL.2
            if "CL.1" in prog_name or "_CL1" in prog_name or "CL1" in prog_name:
                data_cl1.append(row_dict)
            elif "CL.2" in prog_name or "_CL2" in prog_name or "CL2" in prog_name:
                data_cl2.append(row_dict)
            else:
                data_other.append(row_dict)
                
        def print_group_summary(name: str, dataset: list):
            if not dataset:
                return
            
            print(f"\n{C_PURPLE}═══ {name} SMT STATISTIKA ═══{C_END}")
            
            # Agregacija metrika
            total_panels = sum(d["total_board"] for d in dataset)
            total_pcbs = sum(d["worked_pcb"] for d in dataset)
            total_run = sum(d["run_sec"] for d in dataset)
            total_stop = sum(d["stop_sec"] for d in dataset)
            total_ng = sum(d["part_ng"] for d in dataset)
            total_err = sum(d["head_error"] for d in dataset)
            
            total_place = sum(d["place_sec"] for d in dataset)
            total_transfer = sum(d["transfer_sec"] for d in dataset)
            total_entry = sum(d["entry_wait_sec"] for d in dataset)
            total_exit = sum(d["exit_wait_sec"] for d in dataset)
            
            avg_avail = sum(d["availability"] for d in dataset) / len(dataset)
            avg_perf = sum(d["performance"] for d in dataset) / len(dataset)
            avg_qual = sum(d["quality"] for d in dataset) / len(dataset)
            
            oee_calc = avg_avail * avg_perf * avg_qual
            
            # Ispis brojnih podataka
            print(f"  {C_CYAN}Programi:{C_END}   " + ", ".join(set(d["program"] for d in dataset)))
            print(f"  {C_CYAN}Broj panela:{C_END} {total_panels:<10} | {C_CYAN}Broj PCB-ova:{C_END} {total_pcbs}")
            print(f"  {C_CYAN}Aktivno vreme:{C_END} {total_run/60:.1f} min | {C_CYAN}Zastoj (Stop):{C_END} {total_stop/60:.1f} min")
            print(f"  {C_CYAN}Škart (NG):{C_END}  {total_ng:<10} | {C_CYAN}Greške glave:{C_END} {total_err}")
            print()
            
            # Crtanje OEE grafika
            draw_gauge("Availability", avg_avail)
            draw_gauge("Performance", avg_perf)
            draw_gauge("Quality", avg_qual)
            print("  " + "-" * 45)
            draw_gauge("OVERALL OEE", oee_calc)
            
            # Vizuelna analiza stanja i zastoja
            total_all_time = total_run + total_stop
            if total_all_time > 0:
                print(f"\n  {C_BOLD}{C_SILVER}ANALIZA STANJA VREMENA (DOWNTIME & LOSS ANALYSIS):{C_END}")
                
                pct_stop = total_stop / total_all_time
                pct_starve = total_entry / total_all_time
                pct_block = total_exit / total_all_time
                pct_transit = total_transfer / total_all_time
                pct_work = total_place / total_all_time
                
                # Izračunavanje širine karaktera za grafik (širina 50 karaktera)
                stop_ch = int(round(pct_stop * 50))
                starve_ch = int(round(pct_starve * 50))
                block_ch = int(round(pct_block * 50))
                transit_ch = int(round(pct_transit * 50))
                work_ch = 50 - (stop_ch + starve_ch + block_ch + transit_ch)
                if work_ch < 0:
                    work_ch = 0
                    
                # Stacked bar
                bar = (
                    (C_RED + "█" * stop_ch) +
                    (C_YELLOW + "█" * starve_ch) +
                    (C_BLUE + "█" * block_ch) +
                    (C_CYAN + "█" * transit_ch) +
                    (C_GREEN + "█" * work_ch) +
                    C_END
                )
                print(f"  ┌──────────────────────────────────────────────────┐")
                print(f"  │{bar}│")
                print(f"  └──────────────────────────────────────────────────┘")
                print(f"  Legend: {C_RED}■ Stop ({pct_stop*100:.1f}%){C_END} | "
                      f"{C_YELLOW}■ Starvation ({pct_starve*100:.1f}%){C_END} | "
                      f"{C_BLUE}■ Blockage ({pct_block*100:.1f}%){C_END}")
                print(f"          {C_CYAN}■ Transit ({pct_transit*100:.1f}%){C_END} | "
                      f"{C_GREEN}■ Placement ({pct_work*100:.1f}%){C_END}")
                print()
            
        print_group_summary("BOARD SIDE CL.1 (LANE 1 / SIDE A)", data_cl1)
        print_group_summary("BOARD SIDE CL.2 (LANE 2 / SIDE B)", data_cl2)
        print_group_summary("GENERAL / SINGLE SIDE RUNS", data_other)

        
    except Exception as e:
        log_error(f"Greška tokom analize Line 003: {e}")

def get_top_errors(date_str: str):
    print(f"\n{C_BLUE}[*] Učitavam analizu škarta i zastoja sa Line 003...{C_END}")
    
    # Query za top 5 feeder grešaka
    query = """
        SELECT TOP 5 
            CMEqpCd, 
            DeviceNm, 
            FeederNm, 
            SUM(PickUpCnt) as TotalPick, 
            SUM(PickMissCnt) as TotalMiss,
            SUM(PartNgCnt) as TotalNg,
            SUM(ErrorCnt) as TotalErrors
        FROM FMS_ErrorData WITH (NOLOCK)
        WHERE LastLoadDt >= ? AND LastLoadDt < DATEADD(day, 1, ?)
        GROUP BY CMEqpCd, DeviceNm, FeederNm
        HAVING SUM(ErrorCnt) > 0
        ORDER BY TotalErrors DESC
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Pretvaramo datum u datetime za query
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        cursor.execute(query, (dt, dt))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print(f"{C_YELLOW}[!] Nema zabeleženih grešaka na mašinama za dan {date_str}.{C_END}")
            return
            
        print(f"\n{C_PURPLE}═══ TOP 5 ALARMANTNIH FEEDER-A NA LINIJI ═══{C_END}")
        print(f"{'Mašina':<8} | {'Komponenta':<20} | {'Feeder':<12} | {'Pickups':<8} | {'Misses':<8} | {'NG':<6} | {'Err PPM'}")
        print("-" * 80)
        
        for r in rows:
            eqp = r[0]
            device = r[1] if r[1] else "UNKNOWN"
            feeder = r[2] if r[2] else "N/A"
            picks = r[3] or 0
            miss = r[4] or 0
            ng = r[5] or 0
            errs = r[6] or 0
            
            # Računanje PPM
            ppm = (errs / picks) * 1000000 if picks > 0 else 0
            
            print(f"{eqp:<8} | {device:<20} | {feeder:<12} | {picks:<8} | {miss:<8} | {ng:<6} | {ppm:.0f}")
        print("========================================================================\n")
        
    except Exception as e:
        log_error(f"Greška tokom analize feeder grešaka: {e}")

def main():
    parser = argparse.ArgumentParser(description="STATIC//VOID Line 003 Intelligence CLI")
    parser.add_argument("--date", type=str, default="2026-05-18", help="Datum za analizu (Format: YYYY-MM-DD)")
    parser.add_argument("--errors", action="store_true", help="Prikaži top greške na feeder-ima")
    
    args = parser.parse_args()
    
    # Validacija formata datuma
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        log_error("Format datuma mora biti YYYY-MM-DD")
        sys.exit(1)
        
    draw_header()
    
    # Test konekcije pre pokretanja
    try:
        conn = get_connection()
        conn.close()
    except Exception as e:
        log_error(f"Nemoguće uspostaviti vezu sa SQLEXPRESS: {e}")
        sys.exit(1)
        
    analyze_line_003(args.date)
    if args.errors:
        get_top_errors(args.date)

if __name__ == "__main__":
    main()
