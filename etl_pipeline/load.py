# etl_pipeline/load.py
import pandas as pd

def load_data(data: pd.DataFrame, destination: str) -> None:
    """
    Carrega os dados transformados para um destino especificado.
    
    Args:
        data (pd.DataFrame): Dados transformados.
        destination (str): Caminho ou URL do destino dos dados.
    """
    # Exemplo de carga para um arquivo CSV
    data.to_csv(destination, index=False)