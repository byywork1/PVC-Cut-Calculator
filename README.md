# PVC Cut Calculator - MVP Web App

A web-based calculator for determining precise PVC pipe cut lengths for different connector configurations.

## Features

- **Standard Cut**: Calculate single cuts between two connectors using center-to-center measurements
- **Lay-in Cut**: Calculate two separate cuts for lay-in connector configurations
- **Bushing Cut**: Account for bushing thickness in calculations
- **Dropdown Menus**: Select from 5 predefined connector types:
  - Tee (Socket x Socket x Socket)
  - Tee (Reducing)
  - Bushing (Spigot x Socket)
  - Elbow 90 (Socket x Socket)
  - Union (Socket x Socket)
- **Decimal & Fraction Display**: Results shown in both decimal and 1/16th inch fractions
- **Shave Option**: Optional -1/16" adjustment for all calculation types

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone or navigate to the project directory:
```bash
cd PVC-Cut-Calculator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Web App

Start the Streamlit application:
```bash
python -m streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Project Structure

```
PVC-Cut-Calculator/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and connector types
│   ├── loader.py              # Excel database loader
│   ├── calculator.py          # Core calculation logic
│   ├── api.py                 # API wrapper functions
│   ├── models.py              # Data models
│   └── main.py                # CLI interface
├── data/
│   └── PVC Cut Database.xlsx  # Connector offset database
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── streamlit_app.py           # Web app entry point
├── requirements.txt           # Python dependencies
└── README.md
```

## How It Works

1. **Database**: Stores connector types, sizes, and their corresponding offsets
2. **Loader**: Reads Excel database and provides exact lookup of connector offsets
3. **Calculator**: Performs cut length calculations based on selected connectors and measurements
4. **Web Interface**: Streamlit-based UI with dropdown menus and real-time results

## Connector Database

The `PVC Cut Database.xlsx` file contains:
- **Part**: Connector type (e.g., "Tee (Socket x Socket x Socket)")
- **Size**: Connector size (numeric or text format like "1.5x1.5x0.5")
- **Offset**: Offset measurement from fitting center
- **Offset (G1)**: Alternative offset column for extended configurations

## Calculation Types

### Standard Cut
Formula: `C2C - Offset_A - Offset_B`

### Lay-in Cut
Calculates two separate cuts with configurable lay-in center-to-center and offset

### Bushing Cut
Formula: `C2C - Offset_A - Offset_B - Bushing_Thickness`

## Deployment

### Local Development
```bash
python -m streamlit run streamlit_app.py --logger.level=debug
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Deploy by connecting your GitHub repo
4. Share the public URL

### Other Deployment Options
- **Heroku**: See Streamlit deployment guides
- **PythonAnywhere**: Free tier available
- **Docker**: Containerize with Dockerfile

## Development

### CLI Version
For command-line interface:
```bash
python -m src.main
```

### Adding New Connector Types
1. Update `SUPPORTED_CONNECTOR_TYPES` in `src/config.py`
2. Add corresponding rows to `PVC Cut Database.xlsx`
3. Ensure exact match between config and database Part column names

## Testing Calculations

Example test case:
- Type A: Tee (Socket x Socket x Socket), Size: 2
- Type B: Elbow 90 (Socket x Socket), Size: 2
- C2C: 12 inches
- Expected Result: ~9.15625 inches

## Technologies

- **Python 3.13**
- **Streamlit** - Web framework
- **pandas** - Data handling
- **openpyxl** - Excel support

## License

Internal use only

## Support

For issues or questions, check the database configuration and ensure connector types match exactly between `config.py` and the Excel database.