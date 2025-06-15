def check_data_integrity(df):
    print("Shape:", df.shape)
    print("Missing values:\n", df.isnull().sum())
    print("Describe:\n", df.describe())
    # Supprime ou commente la ligne ci-dessous car la colonne 'surface' n'existe plus
    # print("Surface values:\n", df['surface'].value_counts())
