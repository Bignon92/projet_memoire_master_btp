import pandas as pd

def extract_data():

    dataset = pd.read_csv(
        "../data/processed/dataset_analytique.csv"
    )

    trc = pd.read_csv(
        "../data/processed/sinistre_trc_enrichi.csv"
    )

    print("Extraction OK")

    return dataset, trc