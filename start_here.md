# 🚀 SMT Line 003 Production Intelligence Dashboard

## Preradena aplikacija: `app.py`

**Verzija:** v2.0 — ANTIGRAVITY ENGINE  
**Theme:** STATIC//VOID Premium Dark Mode  
**Lokacija:** `C:\Users\Igor\Desktop\antigravity\scratch\app.py`

---

## 📋 Kako pokrenuti aplikaciju?

### **Opcija 1: Batch datoteka (najjednostavnije)**
```bash
run_app.bat
```
- Dvostruki klik na `run_app.bat`
- Dashboard će se otvoriti automatski na `http://localhost:8501`

---

### **Opcija 2: PowerShell**
```powershell
.\run_app.ps1
```

Ili direktno iz PowerShell-a:
```powershell
cd "C:\Users\Igor\Desktop\antigravity\scratch"
streamlit run app.py
```

---

### **Opcija 3: Python skriptu**
```python
python run_app.py
```

---

### **Opcija 4: Direktno iz Command Prompt**
```cmd
cd C:\Users\Igor\Desktop\antigravity\scratch
streamlit run app.py
```

---

## 🔧 Instalacija zavisnosti

Ako app ne radi, trebam instalirati Streamlit:

```bash
pip install streamlit pyodbc pandas
```

Za auto-refresh funkcionalnost (opciono):
```bash
pip install streamlit-autorefresh
```

---

## 📊 Što sadrži aplikacija?

✅ **Premium Dark Theme** sa purple gradient-ima  
✅ **Animirani SVG gauges** za OEE metrike (Availability, Performance, Quality, OEE)  
✅ **Downtime & Loss Analysis** sa vizuelnom distribucijom  
✅ **Per-Machine Breakdown** tabela  
✅ **Auto-refresh** toggle sa interval selectorom (10, 20, 30, 60 sekundi)  
✅ **Demo podatci** ako nema logova u bazi  
✅ **Serbo-Croatian UI** sa professional designom  

---

## 🌐 Dashboard URL

```
http://localhost:8501
```

---

## ⚙️ Konfiguracija

### Database Connection
- Server: `.\SQLEXPRESS`
- Database: `SQUAD`
- Table: `Custom_MachineRunFact`

### Line
- **SMT Line 003** — detaljne metrike sa two-lane suportom (CL.1 i CL.2)

---

## 🎯 Posebne izmjene

1. **SVG Filter ID sanitizacija** — svi gauge IDs su sada validni CSS identifikatori
2. **Auto-refresh sa fallback** — ako `streamlit-autorefresh` nije instaliran, koristi JS reload
3. **Per-gauge HTML generacija** — ispravljen rendering SVG gauges-a

---

## 📝 Shortcut kreiraj na Desktop-u

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\SMT Dashboard.lnk")
$Shortcut.TargetPath = "C:\Users\Igor\Desktop\antigravity\scratch\run_app.bat"
$Shortcut.WorkingDirectory = "C:\Users\Igor\Desktop\antigravity\scratch"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll, 71"
$Shortcut.Save()
```

---

## 📞 Podrška

Ako nešto ne radi:
1. Provjeri Python verziju: `python --version` (trebam Python 3.7+)
2. Provjeri Streamlit: `streamlit --version`
3. Provjeri bazu: je li SQLEXPRESS pokrenut?
4. Koristi demo podatke ako nema logova

---

**Made with ⚡ by ANTIGRAVITY | SQUAD Database**
