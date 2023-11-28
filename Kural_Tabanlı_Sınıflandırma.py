                              #########################################################################
                              # Kural Tabanlı Sınıflandırma ile Potansiyel Müşteri Getirisi Hesaplama #
                              #########################################################################


#      +++++++++++++++++++++++++++++++++++++++++++++            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#      +             UYGULAMA ÖNCESİ               +            +                     UYGULAMA SONRASI                    +
#      +++++++++++++++++++++++++++++++++++++++++++++            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#      +                                          +             +                                                         +
#      +     PRICE   SOURCE   SEX COUNTRY  AGE    +             +       CUSTOMERS_LEVEL_BASED        PRICE     SEGMENT    +
#      +  0     39  android  male     bra   17    +             +  0   FRA_ANDROID_FEMALE_24_30     45.429        A       +
#      +  1     39  android  male     bra   17    +             +  1   TUR_IOS_MALE_24_30           45.000        A       +
#      +  2     49  android  male     bra   17    +             +  2   TUR_IOS_MALE_31_40           42.333        A       +
#      +  3     29  android  male     tur   17    +             +  3   TUR_ANDROID_FEMLAE_31_40     41.833        A       +
#      +  4     49  android  male     tur   17    +             +  4   CAN_ANDROID_FEMALE_19_23     40.111        A       +
#      +                                          +             +                                                         +
#      ++++++++++++++++++++++++++++++++++++++++++++             +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# Gerekli kütüphane importları ve bazı görsel ayarlamaları yapıyoruz.
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda  x : "%.3f" % x)


# İlgili veri setini projemize dahil ediyoruz.
def load_dataset():
    data = pd.read_csv("data_sets/persona.csv")
    return data

df = load_dataset()


# Veri setini tanımak adına check_df fonkdiyonunu tanımlıyoruz.
def check_df(dataframe, head=10):
    """
    Veri setindeki gözlem birimi, boyut bilgisi, değişken isimleri
    gibi veri seti hakkındaki genel resmi verir.

    Parameters
    ----------
    dataframe : dataframe
                Bilgisi istenilen veri seti

    head : int
           Kaç satır gözlem birimi istenildiği bilgisi


    """
    print("\n###################################")
    print(f"---> İlk {head} Gözlem Birimi <---")
    print("###################################")
    print(dataframe.head(head))

    print("\n###################################")
    print("---> Veri Seti Boyut Bilgisi <---")
    print("###################################")
    print(dataframe.shape)

    print("\n###################################")
    print("---> Değişken İsimleri <---")
    print("###################################")
    print(dataframe.columns)

    print("\n###################################")
    print("---> Eksik Değer Var mı? <---")
    print("###################################")
    print(dataframe.isnull().values.any())

    print("\n###################################")
    print("---> Betimsel İstatistikler <---")
    print("###################################")
    print(dataframe.describe().T)

    print("\n###################################")
    print("---> Veri Seti Hakkında Bilgiler <---")
    print("###################################")
    print(dataframe.info())


check_df(dataframe=df)


####
# Veri setini daha iyi tanımak adına bazı soruları cevaplandırıyoruz.
####
# Soru 1: Hangi ülkeden kaçar tane satış olmuş?
df["COUNTRY"].value_counts()

# Soru 2: Ülkelere göre satışlardan toplam ne kadar kazanılmış?
df.groupby("COUNTRY").agg({"PRICE":"mean"})

# Soru 3: COUNTRY-SOURCE kırılımında PRICE ortalamaları nedir?
df.groupby(["COUNTRY", "SOURCE"]).agg({"PRICE":"mean"})



# Veri seti her satış işleminde oluşan kayıtlardan meydana gelmektedir. Bunun anlamı tablo tekilleştirilmemiştir.
# Diğer bir ifade ile belirli demografik özelliklere sahip bir kullanıcı birden fazla kez alışveriş yapmış olabilir.
# value_counts() fonksiyonu ile birden fazla satış kaydı olup olmadığını sorguluyoruz.
df.value_counts()


# Birden fazla kez aynı alışveirşi gerçekleştiren kullanıcıları tekilleştirmek için groupby() fonksiyonunu kullanıyoruz.
# Bunu yapmamızdaki amaç kural tabanlı sınıflandırma yöntemini uygularken birden fazla kez aynı alışveirşi yapan kullanıcıları
# tekilleştirerek hesaplamalardaki şaşmaları engellemektir.
df = df.groupby(["COUNTRY", "SOURCE", "SEX", "AGE"]).agg({"PRICE" : "mean"}).sort_values(by="PRICE", ascending=False)
df.reset_index(inplace=True)


# Age sayısal değişkenini kategorik değişkene çeviriyoruz.
# Aralıkları ikna edici olacağını düşündüğümüz şekilde bölüyoruz.
df["AGE_CAT"] = pd.cut(df["AGE"], bins=[0, 18, 23, 30, 40, df["AGE"].max()], labels=["0_18", "19_23", "24_30", "31_40", "41_" + str(df["AGE"].max())])


# Yeni level based müşterileri tanımlayıp ve veri setine değişken olarak ekliyoruz.
df["CUSTOMERS_LEVEL_BASED"] = [row[0] + "_" +
                               row[1] + "_" +
                               row[2] + "_" +
                               row[5]
                               for row in df.values]


# Birden fazla aynı müşteri tanımına sahip kullanıcı var mı sorgusunu gerçekleştiriyoruz.
df["CUSTOMERS_LEVEL_BASED"].value_counts()


# Aynı müşteri tanımına sahip kullanıcıları tekilleştiriyoruz.
df = df.groupby("CUSTOMERS_LEVEL_BASED").agg({"PRICE":"mean"}).sort_values(by="PRICE", ascending=False)
df.reset_index(inplace=True)


# Müşterileri "PRICE" değişkenine göre segmentlere ayırıyoruz.
df["SEGMENT"] = pd.qcut(df["PRICE"], 4, labels=["D", "C", "B", "A"])


# Yeni gelebilecek müşterilerin şirkete ortalama ne kadar kazandıracağı sorgusun gerçekleştiriyoruz.

# 33 yaşında ANDROID kullanan bir Türk kadını hangi segmente aittir ve ortalama ne kadar gelir kazandırması beklenir?
new_user = "tur_ios_female_31_40"
df[df["CUSTOMERS_LEVEL_BASED"] == new_user]

# 35 yaşında IOS kullanan bir Fransız kadını hangi segmente ve ortalama ne kadar gelir kazandırması beklenir?
new_user = "fra_ios_female_31_40"
df[df["CUSTOMERS_LEVEL_BASED"] == new_user]
