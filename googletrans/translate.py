from googletrans import Translator
def translate_text():
    translator = Translator()
    f = open("output.txt","r")
    trans = translator.translate(f.read())
    print(trans.text)

translate_text()

# # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
# translator.translate('안녕하세요.', dest='ja')
# # <Translated src=ko dest=ja text=こんにちは。 pronunciation=Kon'nichiwa.>
# translator.translate('veritas lux mea', src='la')
# # <Translated src=la dest=en text=The truth is my light pronunciation=The truth is my light>
