# RS Scanner 2 🚀

A comprehensive relative strength (RS) scanner for US stocks with RESTful API support.

## Features

- 📊 **Individual RS Analysis**: Track individual stock performance vs QQQ benchmark
- 🎯 **Weighted RS (WRS)**: Sector/industry level analysis with market cap weighting
- 📈 **Today's List**: Auto-filtered list of top-performing stocks in strong sectors
- 🌐 **RESTful API**: Full programmatic access to all data
- 📱 **Responsive UI**: Dark-themed, mobile-friendly interface
- 🔄 **Auto-Update**: Daily data collection via automation

## Live Demo

🔗 **Website**: [Your Vercel URL here]  
📚 **API Docs**: [Your Vercel URL]/api/docs

## API Quick Start

```javascript
// Get all data
fetch('https://your-url.vercel.app/api/v1/all')
  .then(res => res.json())
  .then(data => console.log(data));

// Get Today's List
fetch('https://your-url.vercel.app/api/v1/todays-list')
  .then(res => res.json())
  .then(data => console.log(data.data));

// Get specific ticker
fetch('https://your-url.vercel.app/api/v1/ticker/NVDA')
  .then(res => res.json())
  .then(data => console.log(data.data));
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/all` | All data (Individual + WRS + Market Condition) |
| `/api/v1/individual` | Individual stock data with filters |
| `/api/v1/wrs` | Weighted Relative Strength by sector |
| `/api/v1/todays-list` | Filtered top stocks |
| `/api/v1/market-condition` | Current market condition |
| `/api/v1/ticker/<symbol>` | Specific ticker details |

Full API documentation available at `/api/docs`

## Local Development

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rs-scanner-2.git
cd rs-scanner-2

# Install dependencies
pip install -r requirements.txt

# Run data collection
python fetch_and_save.py

# Start the server
python app.py
```

Visit `http://localhost:8888`

## Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/rs-scanner-2)

Or manually:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## Data Updates

Data is updated daily after US market close (21:00 UTC / 6:00 AM KST).

For automated updates, set up GitHub Actions:
1. Fork this repository
2. Enable GitHub Actions
3. Data will auto-update daily

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript
- **Data Source**: Yahoo Finance (yfinance)
- **Deployment**: Vercel
- **Automation**: GitHub Actions (optional)

## Project Structure

```
rs-scanner-2/
├── app.py                 # Flask application
├── fetch_and_save.py      # Data collection script
├── utils.py               # Helper functions
├── templates/             # HTML templates
│   ├── index.html         # Main UI
│   └── api_docs.html      # API documentation
├── static/                # Static files
│   └── result.json        # Generated data
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is for **personal educational purposes only** and is **not for commercial use**.  
Data provided by Yahoo Finance.

## Disclaimer

All data is strictly for informational purposes and should not be considered financial advice. This tool is provided as-is with no warranties.

## Credits

- **Idea**: In-gyu Lee
- **Development**: Dae-sik Min
- **Data**: Yahoo Finance API

---

Made with ❤️ using Flask and Vercel
