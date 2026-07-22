## Hepy

Índice de precios de alta frecuencia para Paraguay, construido con scraping diario
de 9 supermercados online, ponderado con la metodología del IPC del Banco Central
del Paraguay (BCP), y validado empíricamente contra la serie oficial.

- Código: Apache-2.0 (`LICENSE-CODE`)
- Dataset: CC BY 4.0 (`LICENSE-DATA`) — citar como "Hepy — Koeti Labs (<año>), <URL del dataset>"
- Dataset descargable: ver la sección "Releases" del repo (`prices.db`, `prices.csv`, `prices.json`)

### Desarrollo

    pip install -r requirements.txt
    pytest
