# Oblivion
Oblivion is a Python-based project focused on stock market analysis and prediction. It offers tools for daily stock updates, candlestick pattern analysis, and stock performance forecasting.

## Features
- Daily Stock Updates: Automates the retrieval and storage of daily stock data.
- Candlestick Pattern Analysis: Identifies and analyzes candlestick patterns to assist in technical analysis.
- Stock Performance Prediction: Utilizes historical data to predict future stock performance.

## Project Structure
- BotHelper.py: Contains helper functions for bot operations.
- CandleStickAnalysis.py: Implements candlestick pattern analysis.
- DailyStockPrediction.py: Handles the prediction of daily stock performance.
- DailyStockUpdate.py: Manages the automation of daily stock data updates.
- DailyStockUpdate.sh: Shell script to facilitate daily stock updates.
- Messages.py: Manages message-related functionalities.
- OblivionBot.py: Main bot script integrating various functionalities.
- StockAnalysis.py: Provides additional stock analysis tools.
- Test.py: Contains test cases for validating functionalities.
- config.py: Holds configuration settings.
- .gitignore: Specifies files and directories to be ignored by Git.
- Pipfile and Pipfile.lock: Manage project dependencies.

## Getting Started

### Clone the Repository:
`git clone https://github.com/AnstonM/Oblivion.git`


### Navigate to the Project Directory:
`cd Oblivion`

### Install Dependencies:

Ensure you have Pipenv installed, then run:
`pipenv install`

### Configure the Project:
Update the config.py file with necessary configurations such as API keys and settings.

### Run the Bot:

Execute the main bot script:
`pipenv run python OblivionBot.py`

License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contact
For questions or suggestions, please open an issue in this repository.
