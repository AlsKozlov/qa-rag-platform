import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class DataCleaner:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def basic_info(self, df: pd.DataFrame) -> None:
        if self.verbose:
            print("\n=== Пример данных ===")
            print(df.head())
            print("\n=== Типы данных ===")
            print(df.dtypes)
            print("\n=== Пропущенные значения ===")
            print(df.isna().sum())
            print("\n=== Дубликаты по (query, doc) ===")
            print(df.duplicated(subset=["query", "doc"]).sum())

    def clean_text(self, df: pd.DataFrame) -> None:
        before = len(df)
        df.dropna(subset=["query", "doc", "label"], inplace=True)
        after = len(df)
        if self.verbose and before != after:
            print(f"Удалено {before - after} строк с пустыми значениями.")
        for col in ["query", "doc"]:
            df.loc[:, col] = df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

    def filter_binary_labels(self, df: pd.DataFrame) -> None:
        before = len(df)
        df.drop(df[~df["label"].isin([0, 1])].index, inplace=True)
        after = len(df)
        if self.verbose and before != after:
            print(f"Удалено {before - after} строк с метками вне [0, 1].")

    def drop_duplicates_and_check_labels(self, df: pd.DataFrame) -> None:
        before = len(df)
        df.drop_duplicates(subset=["query", "doc"], inplace=True)
        after = len(df)
        if self.verbose and before != after:
            print(f"Удалено {before - after} дубликатов.")
        assert df["label"].isin([0, 1]).all(), "Label содержит значения вне 0 или 1!"

    def visualize(self, df: pd.DataFrame) -> None:
        plt.figure(figsize=(6, 4))
        sns.countplot(data=df, x="label")
        plt.title("Частота меток (0/1)")
        plt.xlabel("Метка")
        plt.ylabel("Количество")
        plt.grid(True)
        plt.savefig("/tmp/label_distribution.png")
        plt.close()
