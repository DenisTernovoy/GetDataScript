import pandas as pd


def merge_cost(df_main, file_path):

    df_cost = pd.read_excel(file_path, sheet_name="Вид исследования")

    df_cost["Наименование исследования"] = df_cost["Наименование исследования"].apply(lambda x: x.lower())

    result = pd.merge(
        df_main,
        df_cost[["Наименование исследования", "Стоимость исследования \n(только реактивы & расходные материалы), руб."]],
        on="Наименование исследования",
    )

    result.rename(columns={'Стоимость исследования \n(только реактивы & расходные материалы), руб.': 'Стоимость'}, inplace=True)

    return result


# Функция для форматирования значений
def format_value(row):
    if "серология" in row["Вид исследования"].lower():
        try:
            if "." in row["Количество образцов ТОЛЬКО ДЛЯ СЕРОЛОГИИ"]:
                result = int(
                    row["Количество образцов ТОЛЬКО ДЛЯ СЕРОЛОГИИ"][
                        : row["Количество образцов ТОЛЬКО ДЛЯ СЕРОЛОГИИ"].find(".")
                    ]
                )
            else:
                result = int(row["Количество образцов ТОЛЬКО ДЛЯ СЕРОЛОГИИ"])
        except Exception:
            result = 1
        return result
    else:
        return 1