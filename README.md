# CarMoney
Bachelor project on estimating car market value using machine learning. This prediction model is based on data collected using web scraping, processing the data using machine learning techniques and applying algorithms such as XGBoost, Random Forests and Deep Neural Networks.

**Prerequisites**
- Python 3.x installed.
- Knowledge of Python programming.
- Basic understanding of web scraping and data analysis.
- Understanding of Machine Learning Algorithms

**Technology Stack**
Technologies, libraries and frameworks used in this project:
    Python: Programming language.
    Pandas: Data manipulation and analysis.
    Selenium: Web scraping tool.
    SQLite: Database used for storing scraped data.
    Scikit-learn: Machine learning library for building models.
    PolyFuzz: For string matching in data preprocessing.

1. Clone the repository
    git clone https://your-project-link
    cd CarMoney
2. install dependencies
    pip install -r requirements.txt
**Web Scraping**
1. Creating the database for holding data
    python create_database.py
2. Initializing Scraper
   python finn_car_scraper.py
**Data Processing**
1. Process specifications
   python process_specifications.py
2. Processing Equipment's, includes PolyFuzz String Matching
   python process_equipments.py
3. Clean Cars Data and Synchronize Datasets:
   python sync_and_clean_data.py
**Employ Machine Learning**
python model.py

