import pandas as pd
import statistics 


"""""

Read observation from thermal manikin
"""""


class thermalManikin():
    """
    Data from excel log of thermal manikin

    Parameters
    ----------
    excelPath: str,
    """

    def __init__(self, excelPath):  
        self.file = excelPath


    def get_latest_MST(self):
        df = pd.read_csv(self.file, header=3, encoding = "ISO-8859-1")
        df.index = pd.to_datetime(df['Unnamed: 0'])
        cols = [c for c in df.columns if 'Unname' not in c]
        df = df[cols]
        df = df.drop(df.index[0])
 
        MST_last10Minutes = pd.to_numeric(df.last("10M")["All"]).mean()
        return MST_last10Minutes



