# 💧 AquaTrack

A minimalist water intake tracker, with zero dependencies: a single HTML page, a Python server (standard library only), and JSON storage.

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Overview

AquaTrack lets you log every glass of water you drink in one click, track your progress toward a daily goal, and review your stats from previous days.

- **Main page** — today's total in liters, a progress bar toward your goal, and 4 quick-add buttons
- **Statistics** — daily average, number of days the goal was hit, a 7-day bar chart, and full history

## Features

- ✅ Quick add: glass (20 cl), small bottle (50 cl), liter (1 L), or a custom amount
- ✅ Configurable daily goal
- ✅ Today's log with the ability to delete an entry
- ✅ Daily statistics with a bar chart
- ✅ Local JSON storage, no database to set up
- ✅ Zero external dependencies — Python standard library only
- ✅ Accessible from your local network (usable from your phone)

## Tech stack

| Component | Tech |
|---|---|
| Frontend | Vanilla HTML / CSS / JavaScript |
| Backend | Python 3 (`http.server`, standard library only) |
| Storage | `data.json` file |

## Installation

No dependencies to install — Python 3 is the only requirement.

```bash
git clone https://github.com/<your-username>/aquatrack.git
cd aquatrack
python3 server.py
```

The server starts on port **8421** and listens on all network interfaces.

## Usage

Once the server is running, open:

- **On this computer**: [http://localhost:8421](http://localhost:8421)
- **From another device on the same network** (phone, tablet…): `http://<this-machine's-IP>:8421`

> To find your machine's local IP: `ipconfig` (Windows) or `ifconfig` / `ip a` (macOS / Linux).

## Project structure

```
aquatrack/
├── server.py      # HTTP server + JSON API
├── index.html      # UI (HTML/CSS/JS bundled together)
├── data.json        # Stored entries and goal
└── README.md
```

## API

The server exposes a small JSON API used by the frontend:

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/data` | Returns all entries and the current goal |
| `GET` | `/api/stats` | Returns daily totals |
| `POST` | `/api/add` | Adds an entry — body: `{ "amount_ml": 250 }` |
| `POST` | `/api/delete` | Deletes an entry — body: `{ "id": 1234567890 }` |
| `POST` | `/api/goal` | Updates the daily goal — body: `{ "goal_ml": 2000 }` |

## Data storage

All data is saved to `data.json`, at the project root:

```json
{
  "entries": [
    { "id": 1234567890, "date": "2026-09-20", "time": "14:32", "amount_ml": 250 }
  ],
  "goal_ml": 2000
}
```

To start fresh, just empty the `entries` array — or delete the file, it will be recreated automatically on the next launch.

## Possible roadmap

- [ ] CSV export of history
- [ ] Reminders / notifications
- [ ] Dark theme
- [ ] Multi-user support

## License

MIT — free to use, modify, and share.
