# etl_pipeline/extract.py
import pandas as pd

def csv(source: str) -> pd.DataFrame:
    """
    Extrai dados de uma fonte especificada.
    
    Args:
        source (str): Caminho ou URL da fonte de dados.
    
    Returns:
        pd.DataFrame: Dados extraídos em um DataFrame.
    """
    # Extração de um arquivo CSV
    return pd.read_csv(source)