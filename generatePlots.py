import seaborn as sns
import pandas as pd
import csv
import matplotlib.pyplot as plt
from scipy.stats import shapiro, ttest_rel, wilcoxon

if __name__ == "__main__":
    df = pd.read_csv("results.csv")
    plot = sns.catplot(data=df, x="Instance", y="Time", hue="Language")
    #plt.title("Porównanie czasów znalezienia rozwiązania między C++ a Julią")

    plt.xlabel("Instancja")
    plt.ylabel("Czas [ms]")

    ax = plot.ax
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.2f}"))  # Zaokrąglanie wartości na osi Y


    plt.show()

    

    results = []
    for (instance, language), group in df.groupby(["Instance", "Language"]):
        times = group['Time']
        
        # Przeprowadzamy test Shapiro-Wilka
        stat, p_value = shapiro(times)
        
        # Dodajemy wynik do listy
        results.append({
            "Instance": instance,
            "Language": language,
            "Shapiro Stat": stat,
            "p-value": p_value,
            "Normal": p_value > 0.05  # True, jeśli dane są normalne
        })

    # Konwertuj wyniki Shapiro-Wilka do DataFrame
    normality_df = pd.DataFrame(results)

    # Wyniki testów
    ttest_results = []
    wilcoxon_results = []

    for instance in normality_df["Instance"].unique():
        # Pobierz unikalne języki dla tej instancji
        languages = df[df['Instance'] == instance]['Language'].unique()
        
        # Porównujemy pary języków
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i + 1:]:
                # Filtrujemy dane dla obu języków
                times1 = df[(df['Instance'] == instance) & (df['Language'] == lang1)]['Time']
                times2 = df[(df['Instance'] == instance) & (df['Language'] == lang2)]['Time']
                
                # Sprawdzenie normalności rozkładu dla obu próbek
                is_normal1 = normality_df[(normality_df["Instance"] == instance) & (normality_df["Language"] == lang1)]["Normal"].iloc[0]
                is_normal2 = normality_df[(normality_df["Instance"] == instance) & (normality_df["Language"] == lang2)]["Normal"].iloc[0]
                
                if is_normal1 and is_normal2:
                    # Test t-Studenta
                    stat, p_value = ttest_rel(times1, times2)  # Założenie różnej wariancji
                    
                    # Zapisz wynik
                    ttest_results.append({
                        "Instance": instance,
                        "t-Stat": stat,
                        "p-value": p_value,
                        "Significant": p_value < 0.05  # True, jeśli różnica jest istotna
                    })
                else:
                    # Test Manna-Whitneya
                    stat, p_value = wilcoxon(times1, times2, alternative='two-sided')
                    
                    # Zapisz wynik
                    wilcoxon_results.append({
                        "Instance": instance,
                        "Wilcoxon-Stat": stat,
                        "p-value": p_value,
                        "Significant": p_value < 0.05  # True, jeśli różnica jest istotna
                    })



    # Konwertuj wyniki
    ttest_df = pd.DataFrame(ttest_results)
    wilcoxon_df = pd.DataFrame(wilcoxon_results)

    # Wyświetl wyniki
    print("Wyniki testu Shapiro-Wilka:")
    print(normality_df)

    print("\nWyniki testu t-Studenta:")
    print(ttest_df)

    print("\nWyniki testu Wilcoxon'a:")
    print(wilcoxon_df)

    # Opcjonalnie: zapis wyników do plików CSV
    normality_df.to_csv("shapiro_results.csv", index=False)
    ttest_df.to_csv("ttest_results.csv", index=False)
    wilcoxon_df.to_csv("wilcoxon_results.csv", index=False)
