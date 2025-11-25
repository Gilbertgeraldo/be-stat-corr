# app/routers/ml.py - Optimized untuk Vercel
from fastapi import APIRouter, HTTPException, File, UploadFile
import pandas as pd
import numpy as np
import io
from scipy.stats import pearsonr
import traceback

router = APIRouter(tags=["Machine Learning"])

# Max file size: 5MB untuk Vercel
MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/analyze/correlation-upload")
async def analyze_correlation_upload(file: UploadFile = File(...)):
    """
    Analisis korelasi dari file yang di-upload langsung
    Optimized untuk Vercel serverless
    """
    try:
        # Validasi tipe file
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_ext = None
        for ext in allowed_extensions:
            if file.filename.lower().endswith(ext):
                file_ext = ext
                break
        
        if not file_ext:
            raise HTTPException(
                status_code=400, 
                detail=f"Format file tidak didukung. Gunakan: {', '.join(allowed_extensions)}"
            )
        
        # Baca file yang diupload
        contents = await file.read()
        
        # Validasi ukuran file
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File terlalu besar. Max: 5MB"
            )
        
        if not contents:
            raise HTTPException(status_code=400, detail="File kosong atau tidak terbaca")
        
        # Deteksi format dan baca file
        try:
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(io.BytesIO(contents))
            else:  # CSV
                df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Gagal membaca file: {str(e)}"
            )
        
        # Validasi data
        if df.empty:
            raise HTTPException(status_code=400, detail="File tidak memiliki data")
        
        # Bersihkan data - hapus baris yang seluruhnya kosong
        df = df.dropna(how='all')
        
        # Limit rows untuk performa Vercel (max 1000 rows)
        if len(df) > 1000:
            df = df.head(1000)
        
        # Ambil hanya kolom numerik
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            raise HTTPException(
                status_code=400, 
                detail=f"Tidak ada kolom numerik dalam file. Kolom yang ada: {list(df.columns)}"
            )
        
        # Limit kolom untuk performa (max 20 kolom)
        if len(numeric_df.columns) > 20:
            numeric_df = numeric_df.iloc[:, :20]

        # Hitung korelasi Pearson (skip Spearman untuk hemat waktu)
        pearson_corr = numeric_df.corr(method='pearson')
        p_values = calculate_p_values_fast(numeric_df)
        
        # Identifikasi korelasi kuat
        strong_correlations = extract_strong_correlations(
            pearson_corr, 
            p_values,
            threshold=0.7
        )

        return {
            "status": "success",
            "file_name": file.filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": list(numeric_df.columns),
            "non_numeric_columns": [col for col in df.columns if col not in numeric_df.columns],
            "pearson_correlation": correlation_to_dict(pearson_corr),
            "p_values": p_values_to_dict(p_values),
            "strong_correlations": strong_correlations,
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "summary_stats": summary_stats_to_dict(numeric_df.describe())
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


def correlation_to_dict(corr_matrix):
    """Konversi correlation matrix ke dictionary dengan handling NaN"""
    result = {}
    for col in corr_matrix.columns:
        result[col] = {}
        for idx in corr_matrix.index:
            value = corr_matrix.loc[col, idx]
            result[col][idx] = None if pd.isna(value) else round(float(value), 4)
    return result


def p_values_to_dict(p_values):
    """Konversi p-values ke dictionary dengan handling NaN"""
    result = {}
    for col in p_values.columns:
        result[col] = {}
        for idx in p_values.index:
            value = p_values.loc[col, idx]
            result[col][idx] = None if pd.isna(value) else round(float(value), 6)
    return result


def summary_stats_to_dict(stats_df):
    """Konversi summary statistics ke dictionary dengan handling NaN"""
    result = {}
    for col in stats_df.columns:
        result[col] = {}
        for idx in stats_df.index:
            value = stats_df.loc[idx, col]
            result[col][idx] = None if pd.isna(value) else round(float(value), 2)
    return result


def calculate_p_values_fast(df):
    """
    Hitung p-value dengan optimasi untuk Vercel
    Skip jika terlalu banyak kolom
    """
    columns = df.columns
    max_cols = min(len(columns), 20)  # Limit ke 20 kolom
    
    p_values = pd.DataFrame(
        np.ones((max_cols, max_cols)), 
        columns=columns[:max_cols], 
        index=columns[:max_cols]
    )
    
    for i, col1 in enumerate(columns[:max_cols]):
        for j, col2 in enumerate(columns[:max_cols]):
            if i != j:
                try:
                    _, p_val = pearsonr(df[col1].dropna(), df[col2].dropna())
                    p_values.iloc[i, j] = p_val
                except Exception as e:
                    print(f"Error calculating p-value for {col1} vs {col2}: {e}")
                    p_values.iloc[i, j] = np.nan
            else:
                p_values.iloc[i, j] = 0
    
    return p_values


def extract_strong_correlations(corr_matrix, p_values, threshold=0.7, alpha=0.05):
    """
    Ekstrak korelasi yang kuat dan signifikan secara statistik
    """
    strong_corr = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            p_value = p_values.iloc[i, j]
            
            # Skip jika ada NaN
            if pd.isna(corr_value) or pd.isna(p_value):
                continue
            
            # Hanya tampilkan jika |korelasi| > threshold dan p-value signifikan
            if abs(corr_value) > threshold and p_value < alpha:
                strong_corr.append({
                    "column_1": str(col1),
                    "column_2": str(col2),
                    "correlation": round(float(corr_value), 4),
                    "p_value": round(float(p_value), 6),
                    "strength": "Sangat Kuat" if abs(corr_value) > 0.9 else "Kuat",
                    "direction": "Positif" if corr_value > 0 else "Negatif"
                })
    
    return sorted(strong_corr, key=lambda x: abs(x["correlation"]), reverse=True)


@router.get("/analyze/correlation-info")
def correlation_info():
    """
    Informasi tentang analisis korelasi dan interpretasinya
    """
    return {
        "info": "Analisis Korelasi Pearson",
        "interpretasi": {
            "1.0": "Korelasi sempurna positif",
            "0.7-0.99": "Korelasi sangat kuat positif",
            "0.5-0.69": "Korelasi kuat positif",
            "0.3-0.49": "Korelasi sedang positif",
            "0.1-0.29": "Korelasi lemah positif",
            "0.0-0.09": "Tidak ada korelasi",
            "-0.09-0.0": "Tidak ada korelasi",
            "-0.29--0.1": "Korelasi lemah negatif",
            "-0.49--0.3": "Korelasi sedang negatif",
            "-0.69--0.5": "Korelasi kuat negatif",
            "-0.99--0.7": "Korelasi sangat kuat negatif",
            "-1.0": "Korelasi sempurna negatif"
        },
        "p_value_interpretation": {
            "< 0.05": "Signifikan secara statistik (95% confidence)",
            ">= 0.05": "Tidak signifikan secara statistik"
        }
    }