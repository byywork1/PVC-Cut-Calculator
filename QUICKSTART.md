# Quick Start Guide

## 🚀 Getting Started (2 minutes)

### 1. Install dependencies (first time only)
```bash
pip install -r requirements.txt
```

### 2. Start the web app
```bash
python -m streamlit run streamlit_app.py
```

The app opens automatically in your browser at: **http://localhost:8501**

---

## 📋 Using the Web App

### Step 1: Select Calculation Type
Choose from 3 tabs at the top:
- **Standard Cut** - Single cut between two connectors
- **Lay-in Cut** - Two separate cuts
- **Bushing Cut** - Accounting for bushing thickness

### Step 2: Pick Connector Types
Use dropdown menus to select:
- Connection Type A (from 5 options)
- Connection Type B (from 5 options)

### Step 3: Enter Measurements
- **Size**: The connector size (e.g., `2`, `1.5x1.5x0.5`)
- **C2C**: Center-to-center distance in inches
- **Additional options** depend on calculation type

### Step 4: Hit Calculate
Click the **Calculate** button to get results in:
- **Decimal format** (e.g., `9.15625"`)
- **Fraction format** (e.g., `9 5/16"`)

### Optional: Apply Shave
Check the **Include Shave** box to subtract 1/16" from the result

---

## 🔧 Connector Types Available

1. **Tee (Socket x Socket x Socket)** - Standard 3-way tee
2. **Tee (Reducing)** - Reducing tee with different sizes
3. **Bushing (Spigot x Socket)** - Bushing connector
4. **Elbow 90 (Socket x Socket)** - 90-degree elbow
5. **Union (Socket x Socket)** - Union connector

---

## 💾 Database

All connector sizes and offsets are stored in:
```
data/PVC Cut Database.xlsx
```

Supported size formats:
- **Numeric**: `1.5`, `2`, `3`, `4`, etc.
- **Text**: `1.5x1.5x0.5`, `2x2x1`, etc. (for reducing connectors)

---

## 📊 Example Calculation

**Standard Cut between two size-2 tees:**

- Connection A: Tee (Socket x Socket x Socket), Size: 2
- Connection B: Elbow 90 (Socket x Socket), Size: 2
- Center-to-Center: 12 inches
- Shave: No

**Result**: `9 5/16 inches` (9.15625")

---

## 🐛 Troubleshooting

### "Streamlit not found"
```bash
pip install streamlit
```

### "Database file not found"
Ensure the file exists at: `data/PVC Cut Database.xlsx`

### App crashes on calculation
- Check that sizes exist in the database for selected connectors
- Look at error message for specific size not found

### Port 8501 already in use
```bash
python -m streamlit run streamlit_app.py --server.port=8502
```

---

## 📤 Sharing the App

### Option 1: Share Computer IP (Local Network)
```bash
python -m streamlit run streamlit_app.py --server.address=0.0.0.0
```
Then share: `http://YOUR_COMPUTER_IP:8501`

### Option 2: Deploy to Cloud (Recommended)
See **DEPLOYMENT.md** for free cloud hosting options

---

## 🛑 Stop the App

Press `Ctrl + C` in the terminal, or close the browser tab

---

## 📖 More Information

- **Full documentation**: See `README.md`
- **Deployment guide**: See `DEPLOYMENT.md`
- **Code structure**: See `README.md` > Project Structure

---

## 💡 Next Steps

1. ✅ Try a calculation in the web app
2. 📊 Verify results match your manual calculations
3. 📤 Deploy to cloud (see DEPLOYMENT.md) to share with team
4. 🔧 Add new connector types if needed (edit config.py and database)

Enjoy! 🎉
