import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from pathlib import Path

# --- WAJIB UNTUK SERVER: Agar tidak error "no display name" ---
matplotlib.use('Agg') 

class CorrelationVisualizer:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize dengan menerima DataFrame yang sudah dibaca.
        """
        self.df = df
        self.numeric_df = None
        self.correlation = None
        self.p_values = None
        
        self._prepare_data()
    
    def _prepare_data(self):
        """Bersihkan data dan hitung korelasi"""
        # Hapus baris yang kosong semua
        self.df = self.df.dropna(how='all')
        
        # Ambil hanya kolom angka
        self.numeric_df = self.df.select_dtypes(include=['number'])
        
        if self.numeric_df.empty:
            raise ValueError("Tidak ada kolom numerik dalam file")
        
        # Hitung korelasi
        self.correlation = self.numeric_df.corr(method='pearson')
        self._calculate_p_values()
    
    def _calculate_p_values(self):
        """Hitung p-value untuk setiap pasang kolom"""
        columns = self.numeric_df.columns
        self.p_values = pd.DataFrame(
            np.ones((len(columns), len(columns))),
            columns=columns,
            index=columns
        )
        
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i != j:
                    try:
                        _, p_val = pearsonr(
                            self.numeric_df[col1].dropna(),
                            self.numeric_df[col2].dropna()
                        )
                        self.p_values.iloc[i, j] = p_val
                    except Exception:
                        self.p_values.iloc[i, j] = np.nan
                else:
                    self.p_values.iloc[i, j] = 0

    def get_summary_json(self):
        """
        [BARU] Fungsi ini mengembalikan ringkasan data 
        dalam bentuk JSON agar bisa dikirim ke Frontend Next.js
        """
        strong_corr = []
        for i in range(len(self.correlation.columns)):
            for j in range(i+1, len(self.correlation.columns)):
                col1 = self.correlation.columns[i]
                col2 = self.correlation.columns[j]
                corr_value = self.correlation.iloc[i, j]
                p_value = self.p_values.iloc[i, j]
                
                if abs(corr_value) > 0.5 and not pd.isna(corr_value):
                    strong_corr.append({
                        'var1': col1,
                        'var2': col2,
                        'correlation': round(corr_value, 4),
                        'p_value': round(p_value, 6),
                        'significance': "High" if p_value < 0.05 else "Low"
                    })
        
        return {
            "statistics": self.numeric_df.describe().round(2).to_dict(),
            "strong_correlations": strong_corr,
            "columns": list(self.numeric_df.columns),
            "correlation_matrix": self.correlation.round(3).to_dict() # Untuk Heatmap Frontend
        }

    # --- FITUR GENERATE GAMBAR (Opsional untuk API) ---
    def save_heatmap(self, output_path):
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.correlation, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()