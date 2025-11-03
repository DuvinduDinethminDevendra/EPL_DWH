

def clean_player_names(df, name_col="player_name"):
   
    if name_col in df.columns:
        df[name_col] = df[name_col].astype(str).str.strip().str.title()
    return df
