update:
    git clone https://github.com/codefordc/dc-campaign-finance-data.git $(DATA_DIR)
    python download.py $(DATA_DIR)
    python wrangle.py $(DATA_DIR)
    cd $(DATA_DIR)
    git commit -am 'automated wrangle update'
    git push origin
