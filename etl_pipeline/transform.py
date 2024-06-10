# etl_pipeline/transform.py
import pandas as pd
from haversine import haversine

def dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma e limpa os dados extraídos.
    
    Args:
        df (pd.DataFrame): Dados extraídos.
    
    Returns:
        pd.DataFrame: Dados transformados.
    """
    
    # Exemplo de transformação: remover valores nulos
    # 1. convertando a coluna Age de texto para numero
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas,:].copy()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # 2. convertando a coluna Ratings de texto para decimal(float)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # 3. convertando a coluna order_date de texto para data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

    # 4. convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df['multiple_deliveries'] != 'NaN ')
    df = df.loc[linhas_selecionadas,:].copy()
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    # 4. Removendo NaNs
    df = df[df['Road_traffic_density'] != 'NaN ']
    df = df[df['Road_traffic_density'].isna() == False]
    df = df[df['City'] != 'NaN ']
    df = df[df['City'].notna()]
    df = df[df['City'].isna() == False]
    df = df[df['Festival'] != 'NaN ']

    # # 5. Removendo os espacos dentro de strings/texto/object\
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:,'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:,'Festival'].str.strip()

    df['Time_taken(min)'] = df['Time_taken(min)'].str.extract(r'(\d+)').astype(int)

    # NOvas features
    df['Distance'] = df.apply(
        lambda x: haversine(
            (
                x['Restaurant_latitude'],
                x['Restaurant_longitude']
            ),
            (
                x['Delivery_location_latitude'],
                x['Delivery_location_longitude']
            )
        ),
        axis=1)
    return df

    
